#!/usr/bin/env python3
"""
Tauri Builder CLI - Multi-platform Tauri application builder using Docker
"""

import os
import sys
import json
import time
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import click
import docker
import yaml
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.logging import RichHandler
import logging
from github import Github, GithubException

# Setup logging with rich
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("tauridock")


@dataclass
class BuildConfig:
    """Configuration for build process"""
    dockerfile: Path
    frontend_port: int
    mode: str
    platforms: List[str]
    architectures: List[str]
    app_name: str
    version: str
    output_dir: Path
    optimize: bool
    sign: bool
    bundle_types: Dict[str, List[str]]
    docker_image: str
    docker_cache: bool
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    release_tag: Optional[str] = None
    release_notes: Optional[str] = None
    draft: bool = False
    prerelease: bool = False


class DockerManager:
    """Manages Docker containers and images"""

    def __init__(self, config: BuildConfig):
        self.config = config
        try:
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException as e:
            logger.error(f"Docker is not running or not accessible: {e}")
            sys.exit(1)

    def build_image(self, platform: str, arch: str) -> str:
        """Build Docker image for specific platform"""
        tag = f"tauridock-{platform}-{arch}:latest"

        build_args = {
            'PLATFORM': platform,
            'ARCH': arch,
            'FRONTEND_PORT': str(self.config.frontend_port)
        }

        try:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    console=console
            ) as progress:
                task = progress.add_task(
                    f"Building Docker image for {platform}/{arch}...",
                    total=100
                )

                image, build_logs = self.client.images.build(
                    path=str(self.config.dockerfile.parent),
                    dockerfile=str(self.config.dockerfile.name),
                    tag=tag,
                    buildargs=build_args,
                    nocache=not self.config.docker_cache,
                    rm=True
                )

                progress.update(task, completed=100)

            logger.info(f"✅ Docker image built: {tag}")
            return tag

        except docker.errors.BuildError as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise

    def run_container(self, image: str, command: str, volumes: Dict = None,
                      ports: Dict = None, environment: Dict = None) -> Tuple[int, str]:
        """Run command in Docker container"""
        container = None
        try:
            container = self.client.containers.run(
                image=image,
                command=command,
                volumes=volumes or {},
                ports=ports or {},
                environment=environment or {},
                detach=True,
                remove=False
            )

            # Stream logs
            for log in container.logs(stream=True):
                logger.debug(log.decode('utf-8').strip())

            result = container.wait()
            logs = container.logs().decode('utf-8')

            return result['StatusCode'], logs

        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {e}")
            raise
        finally:
            if container:
                container.remove(force=True)

    def run_dev_container(self, image: str, project_path: Path):
        """Run container in development mode with hot reload"""
        volumes = {
            str(project_path): {'bind': '/app', 'mode': 'rw'}
        }

        ports = {
            f'{self.config.frontend_port}/tcp': self.config.frontend_port,
            '1420/tcp': 1420  # Tauri dev server
        }

        environment = {
            'TAURI_DEV': '1',
            'RUST_BACKTRACE': '1'
        }

        try:
            container = self.client.containers.run(
                image=image,
                command='tauri dev',
                volumes=volumes,
                ports=ports,
                environment=environment,
                detach=True,
                remove=False,
                stdin_open=True,
                tty=True
            )

            console.print(Panel.fit(
                f"🚀 Development server started!\n"
                f"Frontend: http://localhost:{self.config.frontend_port}\n"
                f"Tauri Dev: http://localhost:1420\n\n"
                f"Press Ctrl+C to stop",
                title="Tauri Development Mode"
            ))

            # Stream logs until interrupted
            try:
                for log in container.logs(stream=True):
                    console.print(log.decode('utf-8').strip())
            except KeyboardInterrupt:
                console.print("\n⏹️  Stopping development server...")
                container.stop()
                container.remove()

        except docker.errors.ContainerError as e:
            logger.error(f"Failed to run development container: {e}")
            raise


class PlatformBuilder:
    """Handles platform-specific build logic"""

    PLATFORM_CONFIG = {
        'windows': {
            'rust_target': {
                'x64': 'x86_64-pc-windows-msvc',
                'arm64': 'aarch64-pc-windows-msvc'
            },
            'bundle_types': ['msi', 'nsis', 'exe'],
            'ext': '.exe'
        },
        'macos': {
            'rust_target': {
                'x64': 'x86_64-apple-darwin',
                'arm64': 'aarch64-apple-darwin'
            },
            'bundle_types': ['dmg', 'app'],
            'ext': '.app'
        },
        'linux': {
            'rust_target': {
                'x64': 'x86_64-unknown-linux-gnu',
                'arm64': 'aarch64-unknown-linux-gnu'
            },
            'bundle_types': ['deb', 'AppImage', 'rpm'],
            'ext': ''
        }
    }

    def __init__(self, config: BuildConfig, docker_manager: DockerManager):
        self.config = config
        self.docker_manager = docker_manager

    def build_for_platform(self, platform: str, arch: str) -> List[Path]:
        """Build Tauri app for specific platform and architecture"""
        logger.info(f"🔨 Building for {platform}/{arch}")

        # Get platform-specific configuration
        platform_config = self.PLATFORM_CONFIG[platform]
        rust_target = platform_config['rust_target'][arch]

        # Build Docker image
        image_tag = self.docker_manager.build_image(platform, arch)

        # Prepare build command
        build_cmd = self._prepare_build_command(platform, arch, rust_target)

        # Run build in container
        status, logs = self.docker_manager.run_container(
            image=image_tag,
            command=build_cmd,
            volumes={
                str(Path.cwd()): {'bind': '/app', 'mode': 'rw'}
            }
        )

        if status != 0:
            logger.error(f"Build failed for {platform}/{arch}")
            logger.debug(logs)
            raise RuntimeError(f"Build failed with status {status}")

        # Collect artifacts
        artifacts = self._collect_artifacts(platform, arch)
        logger.info(f"✅ Built {len(artifacts)} artifacts for {platform}/{arch}")

        return artifacts

    def _prepare_build_command(self, platform: str, arch: str, rust_target: str) -> str:
        """Prepare build command with all necessary flags"""
        cmd_parts = [
            'cd /app &&',
            'npm install &&',
            'npm run build &&',
            f'rustup target add {rust_target} &&',
            'cargo tauri build',
            f'--target {rust_target}'
        ]

        if self.config.optimize:
            cmd_parts.append('--release')

        if platform in self.config.bundle_types:
            for bundle in self.config.bundle_types[platform]:
                cmd_parts.append(f'--bundles {bundle}')

        return ' '.join(cmd_parts)

    def _collect_artifacts(self, platform: str, arch: str) -> List[Path]:
        """Collect built artifacts from output directory"""
        artifacts = []
        target_dir = Path('target') / f'{platform}-{arch}' / 'release' / 'bundle'

        if target_dir.exists():
            for bundle_type in self.config.bundle_types.get(platform, []):
                bundle_dir = target_dir / bundle_type
                if bundle_dir.exists():
                    for file in bundle_dir.glob('*'):
                        if file.is_file():
                            # Move to output directory
                            dest = self.config.output_dir / platform / file.name
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file, dest)
                            artifacts.append(dest)

        return artifacts


class GitHubPublisher:
    """Handles GitHub release publishing"""

    def __init__(self, config: BuildConfig):
        self.config = config
        if not config.github_token:
            raise ValueError("GitHub token is required for publishing")

        self.github = Github(config.github_token)
        self.repo = self.github.get_repo(config.github_repo)

    def create_release(self, artifacts: Dict[str, List[Path]]) -> str:
        """Create GitHub release and upload artifacts"""
        logger.info(f"📦 Creating GitHub release {self.config.release_tag}")

        try:
            # Create release
            release = self.repo.create_git_release(
                tag=self.config.release_tag,
                name=self.config.release_tag,
                message=self._get_release_notes(),
                draft=self.config.draft,
                prerelease=self.config.prerelease
            )

            # Upload artifacts with progress
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    console=console
            ) as progress:

                total_files = sum(len(files) for files in artifacts.values())
                task = progress.add_task(
                    f"Uploading {total_files} artifacts...",
                    total=total_files
                )

                for platform, files in artifacts.items():
                    for file_path in files:
                        # Generate checksum
                        checksum = self._calculate_checksum(file_path)

                        # Upload file
                        with open(file_path, 'rb') as f:
                            release.upload_asset(
                                path=str(file_path),
                                label=f"{file_path.name} ({platform})",
                                content_type='application/octet-stream'
                            )

                        # Upload checksum
                        checksum_file = file_path.with_suffix('.sha256')
                        checksum_file.write_text(f"{checksum}  {file_path.name}")

                        with open(checksum_file, 'rb') as f:
                            release.upload_asset(
                                path=str(checksum_file),
                                label=f"{checksum_file.name}",
                                content_type='text/plain'
                            )

                        progress.update(task, advance=1)

            logger.info(f"✅ Release created: {release.html_url}")
            return release.html_url

        except GithubException as e:
            logger.error(f"Failed to create GitHub release: {e}")
            raise

    def _get_release_notes(self) -> str:
        """Get release notes from file or generate default"""
        if self.config.release_notes and Path(self.config.release_notes).exists():
            return Path(self.config.release_notes).read_text()

        return f"""# Release {self.config.release_tag}

## What's New
- Built with Tauri Builder CLI
- Supports multiple platforms and architectures

## Downloads
Choose the appropriate installer for your system below.

## Checksums
SHA256 checksums are provided for each file.
"""

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


class ConfigManager:
    """Manages Tauri and build configuration"""

    @staticmethod
    def load_config_file(config_path: Path = Path('.tauridock.yml')) -> Dict:
        """Load configuration from YAML file"""
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    @staticmethod
    def get_tauri_config(config_path: Path = Path('src-tauri/tauri.conf.json')) -> Dict:
        """Load Tauri configuration"""
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}

    @staticmethod
    def get_package_info(package_path: Path = Path('package.json')) -> Dict:
        """Get package.json information"""
        if package_path.exists():
            with open(package_path) as f:
                return json.load(f)
        return {}


class TauriBuilder:
    """Main Tauri Builder orchestrator"""

    def __init__(self, config: BuildConfig):
        self.config = config
        self.docker_manager = DockerManager(config)
        self.platform_builder = PlatformBuilder(config, self.docker_manager)

        if config.mode == 'publish':
            self.github_publisher = GitHubPublisher(config)

    def run(self):
        """Execute build process based on mode"""
        start_time = time.time()

        try:
            if self.config.mode == 'dev':
                self._run_dev_mode()
            elif self.config.mode == 'build':
                artifacts = self._run_build_mode()
                self._display_results(artifacts)
            elif self.config.mode == 'publish':
                artifacts = self._run_build_mode()
                release_url = self._run_publish_mode(artifacts)
                self._display_results(artifacts, release_url)

            elapsed = time.time() - start_time
            logger.info(f"✨ Completed in {elapsed:.2f} seconds")

        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            sys.exit(1)

    def _run_dev_mode(self):
        """Run development mode with hot reload"""
        logger.info("🚀 Starting development mode")

        # Build dev image
        image = self.docker_manager.build_image('linux', 'x64')

        # Run dev container
        self.docker_manager.run_dev_container(image, Path.cwd())

    def _run_build_mode(self) -> Dict[str, List[Path]]:
        """Run build for all specified platforms"""
        logger.info(f"🏗️  Building for platforms: {', '.join(self.config.platforms)}")

        artifacts = {}

        # Build in parallel using thread pool
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            for platform in self.config.platforms:
                for arch in self.config.architectures:
                    # Check if platform/arch combination is valid
                    if arch in PlatformBuilder.PLATFORM_CONFIG[platform]['rust_target']:
                        future = executor.submit(
                            self.platform_builder.build_for_platform,
                            platform, arch
                        )
                        futures.append((future, platform, arch))

            # Collect results
            for future, platform, arch in futures:
                try:
                    result = future.result(timeout=3600)  # 1 hour timeout
                    key = f"{platform}-{arch}"
                    artifacts[key] = result
                except Exception as e:
                    logger.error(f"Failed to build {platform}/{arch}: {e}")

        return artifacts

    def _run_publish_mode(self, artifacts: Dict[str, List[Path]]) -> str:
        """Publish artifacts to GitHub"""
        logger.info("📤 Publishing to GitHub")
        return self.github_publisher.create_release(artifacts)

    def _display_results(self, artifacts: Dict[str, List[Path]], release_url: str = None):
        """Display build results in a nice table"""
        table = Table(title="Build Results", show_header=True)
        table.add_column("Platform", style="cyan")
        table.add_column("Architecture", style="magenta")
        table.add_column("Artifacts", style="green")
        table.add_column("Size", style="yellow")

        total_size = 0

        for key, files in artifacts.items():
            platform, arch = key.split('-')
            file_list = []

            for file in files:
                size = file.stat().st_size
                total_size += size
                file_list.append(f"• {file.name} ({self._format_size(size)})")

            table.add_row(
                platform.capitalize(),
                arch.upper(),
                '\n'.join(file_list),
                self._format_size(sum(f.stat().st_size for f in files))
            )

        console.print(table)

        if release_url:
            console.print(Panel.fit(
                f"🎉 Release published successfully!\n"
                f"URL: {release_url}\n"
                f"Total size: {self._format_size(total_size)}",
                title="GitHub Release"
            ))

    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


@click.command()
@click.option('--dockerfile', type=click.Path(exists=True), required=True,
              help='Path to Dockerfile for building')
@click.option('--frontend-port', type=int, default=3003,
              help='Port for frontend server')
@click.option('--mode', type=click.Choice(['dev', 'build', 'publish']), default='build',
              help='Operation mode')
@click.option('--platforms', default='windows,macos,linux',
              help='Comma-separated list of target platforms')
@click.option('--arch', '--architectures', default='x64',
              help='Comma-separated list of architectures')
@click.option('--app-name', help='Application name')
@click.option('--version', help='Application version')
@click.option('--output-dir', type=click.Path(), default='dist',
              help='Output directory for built artifacts')
@click.option('--optimize', is_flag=True, help='Enable production optimizations')
@click.option('--sign', is_flag=True, help='Sign the application')
@click.option('--bundle-types', help='Bundle types per platform (JSON format)')
@click.option('--config', type=click.Path(exists=True),
              help='Path to configuration file')
@click.option('--hot-reload', is_flag=True, help='Enable hot reload in dev mode')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--devtools', is_flag=True, help='Open devtools in dev mode')
@click.option('--watch', is_flag=True, help='Watch for file changes')
@click.option('--env-file', type=click.Path(exists=True),
              help='Path to environment file')
@click.option('--docker-image', default='rust:latest',
              help='Base Docker image')
@click.option('--docker-cache', is_flag=True, help='Use Docker cache')
@click.option('--github-token', envvar='GITHUB_TOKEN',
              help='GitHub token for publishing')
@click.option('--github-repo', help='GitHub repository (owner/repo)')
@click.option('--release-tag', help='Release tag')
@click.option('--release-notes', type=click.Path(exists=True),
              help='Path to release notes file')
@click.option('--draft', is_flag=True, help='Create draft release')
@click.option('--prerelease', is_flag=True, help='Mark as prerelease')
def main(**kwargs):
    """Tauri Builder CLI - Build Tauri apps for all platforms using Docker"""

    # Setup logging level
    if kwargs.get('debug'):
        logger.setLevel(logging.DEBUG)

    # Display banner
    console.print(Panel.fit(
        "🦀 Tauri Builder CLI v1.0.0\n"
        "Multi-platform Tauri application builder",
        title="Welcome",
        style="bold blue"
    ))

    # Load configuration
    config_data = {}
    if kwargs.get('config'):
        config_data = ConfigManager.load_config_file(Path(kwargs['config']))

    # Merge CLI args with config file
    final_config = {**config_data, **{k: v for k, v in kwargs.items() if v is not None}}

    # Get app info from tauri.conf.json and package.json
    tauri_config = ConfigManager.get_tauri_config()
    package_info = ConfigManager.get_package_info()

    # Build configuration object
    config = BuildConfig(
        dockerfile=Path(final_config['dockerfile']),
        frontend_port=final_config.get('frontend_port', 3003),
        mode=final_config.get('mode', 'build'),
        platforms=final_config.get('platforms', 'windows,macos,linux').split(','),
        architectures=final_config.get('architectures', 'x64').split(','),
        app_name=final_config.get('app_name') or tauri_config.get('package', {}).get('productName', 'TauriApp'),
        version=final_config.get('version') or package_info.get('version', '1.0.0'),
        output_dir=Path(final_config.get('output_dir', 'dist')),
        optimize=final_config.get('optimize', False),
        sign=final_config.get('sign', False),
        bundle_types=json.loads(final_config.get('bundle_types', '{}')) if isinstance(final_config.get('bundle_types'),
                                                                                      str) else final_config.get(
            'bundle_types', {}),
        docker_image=final_config.get('docker_image', 'rust:latest'),
        docker_cache=final_config.get('docker_cache', False),
        github_token=final_config.get('github_token'),
        github_repo=final_config.get('github_repo'),
        release_tag=final_config.get('release_tag') or f"v{final_config.get('version', '1.0.0')}",
        release_notes=final_config.get('release_notes'),
        draft=final_config.get('draft', False),
        prerelease=final_config.get('prerelease', False)
    )

    # Create and run builder
    builder = TauriBuilder(config)
    builder.run()


if __name__ == '__main__':
    main()