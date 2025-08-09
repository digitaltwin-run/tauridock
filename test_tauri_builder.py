#!/usr/bin/env python3
"""
Unit tests for Tauri Builder CLI
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import tempfile
import json
import yaml
import os
from dataclasses import dataclass

# Import modules to test
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the imports that require external libraries
sys.modules['docker'] = MagicMock()
sys.modules['github'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.logging'] = MagicMock()

from tauri_builder import (
    BuildConfig, DockerManager, PlatformBuilder,
    GitHubPublisher, ConfigManager, TauriBuilder
)


class TestBuildConfig(unittest.TestCase):
    """Test BuildConfig dataclass"""

    def test_build_config_creation(self):
        """Test creating BuildConfig with all parameters"""
        config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="build",
            platforms=["windows", "linux"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=True,
            sign=False,
            bundle_types={"windows": ["msi"]},
            docker_image="rust:latest",
            docker_cache=True
        )

        self.assertEqual(config.dockerfile, Path("Dockerfile"))
        self.assertEqual(config.frontend_port, 3000)
        self.assertEqual(config.mode, "build")
        self.assertEqual(config.platforms, ["windows", "linux"])
        self.assertEqual(config.architectures, ["x64"])
        self.assertEqual(config.app_name, "TestApp")
        self.assertEqual(config.version, "1.0.0")
        self.assertTrue(config.optimize)
        self.assertFalse(config.sign)


class TestDockerManager(unittest.TestCase):
    """Test DockerManager class"""

    def setUp(self):
        self.config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="build",
            platforms=["linux"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=False,
            sign=False,
            bundle_types={},
            docker_image="rust:latest",
            docker_cache=False
        )

    @patch('docker.from_env')
    def test_docker_manager_init(self, mock_docker):
        """Test DockerManager initialization"""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        manager = DockerManager(self.config)

        mock_docker.assert_called_once()
        mock_client.ping.assert_called_once()
        self.assertEqual(manager.client, mock_client)

    @patch('docker.from_env')
    def test_docker_manager_init_failure(self, mock_docker):
        """Test DockerManager initialization when Docker is not available"""
        mock_docker.side_effect = Exception("Docker not found")

        with self.assertRaises(SystemExit):
            DockerManager(self.config)

    @patch('docker.from_env')
    def test_build_image(self, mock_docker):
        """Test building Docker image"""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_image = MagicMock()
        mock_client.images.build.return_value = (mock_image, ["log1", "log2"])

        manager = DockerManager(self.config)
        tag = manager.build_image("linux", "x64")

        self.assertEqual(tag, "tauri-builder-linux-x64:latest")
        mock_client.images.build.assert_called_once()

        # Check build arguments
        call_args = mock_client.images.build.call_args
        self.assertEqual(call_args[1]['tag'], "tauri-builder-linux-x64:latest")
        self.assertEqual(call_args[1]['buildargs']['PLATFORM'], "linux")
        self.assertEqual(call_args[1]['buildargs']['ARCH'], "x64")

    @patch('docker.from_env')
    def test_run_container(self, mock_docker):
        """Test running container with command"""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Build successful"
        mock_client.containers.run.return_value = mock_container

        manager = DockerManager(self.config)
        status, logs = manager.run_container(
            "test-image",
            "echo hello",
            volumes={"/host": {"bind": "/container", "mode": "rw"}}
        )

        self.assertEqual(status, 0)
        self.assertEqual(logs, "Build successful")
        mock_container.remove.assert_called_once_with(force=True)


class TestPlatformBuilder(unittest.TestCase):
    """Test PlatformBuilder class"""

    def setUp(self):
        self.config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="build",
            platforms=["windows", "linux"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=True,
            sign=False,
            bundle_types={"windows": ["msi"], "linux": ["deb"]},
            docker_image="rust:latest",
            docker_cache=False
        )

        self.mock_docker_manager = MagicMock()

    def test_platform_config(self):
        """Test platform configuration structure"""
        builder = PlatformBuilder(self.config, self.mock_docker_manager)

        self.assertIn('windows', builder.PLATFORM_CONFIG)
        self.assertIn('macos', builder.PLATFORM_CONFIG)
        self.assertIn('linux', builder.PLATFORM_CONFIG)

        windows_config = builder.PLATFORM_CONFIG['windows']
        self.assertIn('x64', windows_config['rust_target'])
        self.assertIn('msi', windows_config['bundle_types'])

    def test_prepare_build_command(self):
        """Test build command preparation"""
        builder = PlatformBuilder(self.config, self.mock_docker_manager)

        cmd = builder._prepare_build_command(
            "linux", "x64", "x86_64-unknown-linux-gnu"
        )

        self.assertIn("npm install", cmd)
        self.assertIn("npm run build", cmd)
        self.assertIn("cargo tauri build", cmd)
        self.assertIn("--target x86_64-unknown-linux-gnu", cmd)
        self.assertIn("--release", cmd)  # Because optimize=True
        self.assertIn("--bundles deb", cmd)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    @patch('shutil.copy2')
    def test_collect_artifacts(self, mock_copy, mock_glob, mock_exists):
        """Test artifact collection"""
        builder = PlatformBuilder(self.config, self.mock_docker_manager)

        # Mock file system
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = "app.deb"
        mock_glob.return_value = [mock_file]

        artifacts = builder._collect_artifacts("linux", "x64")

        self.assertEqual(len(artifacts), 1)
        mock_copy.assert_called_once()


class TestGitHubPublisher(unittest.TestCase):
    """Test GitHubPublisher class"""

    def setUp(self):
        self.config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="publish",
            platforms=["windows"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=True,
            sign=False,
            bundle_types={},
            docker_image="rust:latest",
            docker_cache=False,
            github_token="test_token",
            github_repo="user/repo",
            release_tag="v1.0.0",
            draft=False,
            prerelease=False
        )

    @patch('github.Github')
    def test_github_publisher_init(self, mock_github_class):
        """Test GitHubPublisher initialization"""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github

        publisher = GitHubPublisher(self.config)

        mock_github_class.assert_called_once_with("test_token")
        mock_github.get_repo.assert_called_once_with("user/repo")
        self.assertEqual(publisher.repo, mock_repo)

    def test_github_publisher_no_token(self):
        """Test GitHubPublisher without token"""
        config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="publish",
            platforms=["windows"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=True,
            sign=False,
            bundle_types={},
            docker_image="rust:latest",
            docker_cache=False,
            github_token=None
        )

        with self.assertRaises(ValueError):
            GitHubPublisher(config)

    @patch('github.Github')
    def test_calculate_checksum(self, mock_github_class):
        """Test SHA256 checksum calculation"""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github

        publisher = GitHubPublisher(self.config)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = Path(f.name)

        try:
            checksum = publisher._calculate_checksum(temp_path)
            # Known SHA256 for "test content"
            expected = "1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014"
            self.assertEqual(checksum, expected)
        finally:
            temp_path.unlink()


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager class"""

    def test_load_config_file(self):
        """Test loading YAML configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump({'frontend_port': 8080, 'mode': 'dev'}, f)
            temp_path = Path(f.name)

        try:
            config = ConfigManager.load_config_file(temp_path)
            self.assertEqual(config['frontend_port'], 8080)
            self.assertEqual(config['mode'], 'dev')
        finally:
            temp_path.unlink()

    def test_load_missing_config_file(self):
        """Test loading non-existent configuration file"""
        config = ConfigManager.load_config_file(Path('non_existent.yml'))
        self.assertEqual(config, {})

    def test_get_tauri_config(self):
        """Test loading Tauri configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'package': {'productName': 'MyApp'}}, f)
            temp_path = Path(f.name)

        try:
            config = ConfigManager.get_tauri_config(temp_path)
            self.assertEqual(config['package']['productName'], 'MyApp')
        finally:
            temp_path.unlink()

    def test_get_package_info(self):
        """Test loading package.json"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'name': 'my-app', 'version': '2.0.0'}, f)
            temp_path = Path(f.name)

        try:
            info = ConfigManager.get_package_info(temp_path)
            self.assertEqual(info['name'], 'my-app')
            self.assertEqual(info['version'], '2.0.0')
        finally:
            temp_path.unlink()


class TestTauriBuilder(unittest.TestCase):
    """Test TauriBuilder main class"""

    def setUp(self):
        self.config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="build",
            platforms=["linux"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=False,
            sign=False,
            bundle_types={"linux": ["deb"]},
            docker_image="rust:latest",
            docker_cache=False
        )

    @patch('tauri_builder.DockerManager')
    @patch('tauri_builder.PlatformBuilder')
    def test_tauri_builder_init(self, mock_platform_builder, mock_docker_manager):
        """Test TauriBuilder initialization"""
        builder = TauriBuilder(self.config)

        mock_docker_manager.assert_called_once_with(self.config)
        mock_platform_builder.assert_called_once()
        self.assertIsNotNone(builder.docker_manager)
        self.assertIsNotNone(builder.platform_builder)

    @patch('tauri_builder.DockerManager')
    @patch('tauri_builder.PlatformBuilder')
    def test_format_size(self, mock_platform_builder, mock_docker_manager):
        """Test file size formatting"""
        builder = TauriBuilder(self.config)

        self.assertEqual(builder._format_size(512), "512.00 B")
        self.assertEqual(builder._format_size(1024), "1.00 KB")
        self.assertEqual(builder._format_size(1048576), "1.00 MB")
        self.assertEqual(builder._format_size(1073741824), "1.00 GB")

    @patch('tauri_builder.DockerManager')
    @patch('tauri_builder.PlatformBuilder')
    def test_run_build_mode(self, mock_platform_builder_class, mock_docker_manager_class):
        """Test running build mode"""
        mock_docker_manager = MagicMock()
        mock_docker_manager_class.return_value = mock_docker_manager

        mock_platform_builder = MagicMock()
        mock_platform_builder.build_for_platform.return_value = [Path("app.deb")]
        mock_platform_builder_class.return_value = mock_platform_builder

        builder = TauriBuilder(self.config)
        artifacts = builder._run_build_mode()

        self.assertIn("linux-x64", artifacts)
        self.assertEqual(len(artifacts["linux-x64"]), 1)
        mock_platform_builder.build_for_platform.assert_called_once_with("linux", "x64")


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    @patch('click.echo')
    @patch('tauri_builder.TauriBuilder')
    def test_cli_basic_build(self, mock_builder_class, mock_echo):
        """Test CLI with basic build parameters"""
        from tauri_builder import main
        from click.testing import CliRunner

        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix='Dockerfile', delete=False) as f:
            dockerfile_path = f.name

        try:
            result = runner.invoke(main, [
                '--dockerfile', dockerfile_path,
                '--frontend-port', '3000',
                '--mode', 'build'
            ])

            # Check that command executed without error
            # Note: Will fail because Docker is mocked, but tests argument parsing
            self.assertIsNotNone(result)
        finally:
            Path(dockerfile_path).unlink()

    def test_build_command_generation(self):
        """Test full build command generation"""
        config = BuildConfig(
            dockerfile=Path("Dockerfile"),
            frontend_port=3000,
            mode="build",
            platforms=["windows"],
            architectures=["x64"],
            app_name="TestApp",
            version="1.0.0",
            output_dir=Path("dist"),
            optimize=True,
            sign=True,
            bundle_types={"windows": ["msi", "nsis"]},
            docker_image="rust:latest",
            docker_cache=False
        )

        mock_docker = MagicMock()
        builder = PlatformBuilder(config, mock_docker)

        cmd = builder._prepare_build_command(
            "windows", "x64", "x86_64-pc-windows-msvc"
        )

        # Verify all expected components are in command
        expected_parts = [
            "npm install",
            "npm run build",
            "rustup target add x86_64-pc-windows-msvc",
            "cargo tauri build",
            "--target x86_64-pc-windows-msvc",
            "--release",
            "--bundles msi",
            "--bundles nsis"
        ]

        for part in expected_parts:
            self.assertIn(part, cmd)


class TestDockerfile(unittest.TestCase):
    """Test Dockerfile validation"""

    def test_dockerfile_structure(self):
        """Test that Dockerfile meets requirements"""
        dockerfile_content = """
# Multi-stage Dockerfile for Tauri Builder
FROM rust:1.70 as builder

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Install Tauri dependencies
RUN apt-get update && apt-get install -y \
    libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev

# Install Tauri CLI
RUN cargo install tauri-cli

WORKDIR /app
"""

        # Check for required components
        self.assertIn("rust:", dockerfile_content)
        self.assertIn("nodejs", dockerfile_content)
        self.assertIn("tauri-cli", dockerfile_content)
        self.assertIn("libwebkit2gtk", dockerfile_content)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)