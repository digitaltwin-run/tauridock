# 👨‍💻 Developer Guide

[← Poprzedni: Konfiguracja](./CONFIG.md) | [Spis treści](./INDEX.md) | [Następny: Architektura →](./06-ARCHITECTURE.md)

---

## 📋 Spis Treści

- [Struktura Projektu](#struktura-projektu)
- [Środowisko Deweloperskie](#środowisko-deweloperskie)
- [Rozszerzanie Funkcjonalności](#rozszerzanie-funkcjonalności)
- [Tworzenie Pluginów](#tworzenie-pluginów)
- [Testing](#testing)
- [Debugging](#debugging)
- [Contributing](#contributing)
- [Code Style](#code-style)

---

## 📁 Struktura Projektu

### Drzewo katalogów

```
tauri-builder/
├── tauri_builder/          # Główny pakiet Python
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── builder.py         # Core builder logic
│   ├── docker_manager.py  # Docker operations
│   ├── platform_builder.py # Platform-specific builds
│   ├── github_publisher.py # GitHub releases
│   ├── config_manager.py  # Configuration handling
│   ├── utils/             # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py      # Logging
│   │   ├── validator.py   # Validation
│   │   └── helpers.py     # Helper functions
│   └── plugins/           # Plugin system
│       ├── __init__.py
│       └── base.py        # Base plugin class
├── tests/                 # Tests
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── docs/                 # Documentation
├── examples/             # Example projects
├── scripts/              # Utility scripts
├── docker/               # Docker files
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-compose.yml
├── .github/              # GitHub Actions
│   └── workflows/
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Dev dependencies
├── setup.py             # Package setup
├── Makefile             # Make targets
└── README.md            # Main README
```

### Moduły główne

#### `cli.py` - Command Line Interface

```python
"""CLI entry point"""

import click
from .builder import TauriBuilder
from .config_manager import ConfigManager

@click.command()
@click.option('--config', help='Config file path')
def main(config):
    """Main CLI entry point"""
    config_data = ConfigManager.load(config)
    builder = TauriBuilder(config_data)
    builder.run()
```

#### `builder.py` - Core Builder

```python
"""Core builder logic"""

class TauriBuilder:
    def __init__(self, config):
        self.config = config
        self.docker = DockerManager(config)
        self.platform_builder = PlatformBuilder(config)
        
    def run(self):
        """Execute build process"""
        if self.config.mode == 'dev':
            return self.run_dev()
        elif self.config.mode == 'build':
            return self.run_build()
```

---

## 🛠️ Środowisko Deweloperskie

### Setup środowiska

```bash
# Clone repo
git clone https://github.com/digitaltwin-run/tauri-builder.git
cd tauri-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dev dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Setup pre-commit hooks
pre-commit install
```

### Narzędzia deweloperskie

#### VS Code configuration

```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug CLI",
      "type": "python",
      "request": "launch",
      "module": "tauri_builder",
      "args": ["--debug", "--config", ".tauri-builder.yml"],
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-vv", "--no-cov"],
      "console": "integratedTerminal"
    }
  ]
}
```

#### PyCharm configuration

```xml
<!-- .idea/runConfigurations/TauriBuilder.xml -->
<component name="ProjectRunConfigurationManager">
  <configuration name="TauriBuilder" type="PythonConfigurationType">
    <module name="tauri-builder" />
    <option name="SCRIPT_NAME" value="tauri_builder/__main__.py" />
    <option name="PARAMETERS" value="--debug" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
  </configuration>
</component>
```

---

## 🔧 Rozszerzanie Funkcjonalności

### Dodawanie nowej platformy

```python
# tauri_builder/platforms/new_platform.py

from ..platform_builder import PlatformBase

class NewPlatformBuilder(PlatformBase):
    """Builder for NewPlatform"""
    
    PLATFORM_NAME = "newplatform"
    SUPPORTED_ARCHS = ["x64", "arm64"]
    
    def get_rust_target(self, arch: str) -> str:
        """Get Rust target triple"""
        targets = {
            "x64": "x86_64-unknown-newplatform",
            "arm64": "aarch64-unknown-newplatform"
        }
        return targets.get(arch)
    
    def build(self, arch: str) -> List[Path]:
        """Build for architecture"""
        target = self.get_rust_target(arch)
        
        # Build logic
        self.run_command(f"cargo build --target {target}")
        
        # Return artifacts
        return self.collect_artifacts()
    
    def package(self, artifacts: List[Path]) -> List[Path]:
        """Package artifacts"""
        packages = []
        for artifact in artifacts:
            package = self.create_package(artifact)
            packages.append(package)
        return packages
```

### Dodawanie nowego bundle type

```python
# tauri_builder/bundlers/new_bundler.py

from ..bundler import BundlerBase

class NewBundler(BundlerBase):
    """Custom bundler implementation"""
    
    BUNDLE_TYPE = "custom"
    EXTENSION = ".custom"
    
    def bundle(self, app_path: Path) -> Path:
        """Create bundle from app"""
        bundle_path = app_path.with_suffix(self.EXTENSION)
        
        # Bundling logic
        with ZipFile(bundle_path, 'w') as bundle:
            # Add files to bundle
            for file in self.get_files(app_path):
                bundle.write(file)
        
        return bundle_path
```

### Dodawanie nowego hook

```python
# tauri_builder/hooks/custom_hook.py

from ..hooks import Hook

class CustomHook(Hook):
    """Custom build hook"""
    
    NAME = "custom"
    PHASE = "pre_build"  # pre_build, post_build, pre_publish, post_publish
    
    def execute(self, context):
        """Execute hook"""
        self.logger.info(f"Executing {self.NAME} hook")
        
        # Hook logic
        if context.platform == "windows":
            self.run_windows_specific()
        
        return True
    
    def run_windows_specific(self):
        """Windows-specific logic"""
        pass
```

---

## 🔌 Tworzenie Pluginów

### Struktura pluginu

```python
# plugins/my_plugin/__init__.py

from tauri_builder.plugins import Plugin

class MyPlugin(Plugin):
    """Custom plugin for Tauri Builder"""
    
    NAME = "my_plugin"
    VERSION = "1.0.0"
    
    def __init__(self, config):
        super().__init__(config)
        self.setup()
    
    def setup(self):
        """Initialize plugin"""
        self.register_command("custom", self.custom_command)
        self.register_hook("pre_build", self.pre_build_hook)
    
    def custom_command(self, *args, **kwargs):
        """Custom command implementation"""
        self.logger.info("Executing custom command")
        # Command logic
    
    def pre_build_hook(self, context):
        """Pre-build hook"""
        self.logger.info("Pre-build hook from plugin")
        # Hook logic
        
    def cleanup(self):
        """Cleanup resources"""
        pass

# Export plugin
plugin = MyPlugin
```

### Rejestracja pluginu

```yaml
# .tauri-builder.yml
plugins:
  - name: my_plugin
    enabled: true
    config:
      option1: value1
      option2: value2
```

### Plugin API

```python
class Plugin:
    """Base plugin class"""
    
    def register_command(self, name: str, handler: Callable):
        """Register CLI command"""
        
    def register_hook(self, phase: str, handler: Callable):
        """Register build hook"""
        
    def register_platform(self, platform: PlatformBase):
        """Register platform builder"""
        
    def register_bundler(self, bundler: BundlerBase):
        """Register bundler"""
        
    def emit_event(self, event: str, data: Any):
        """Emit event"""
        
    def on_event(self, event: str, handler: Callable):
        """Listen to event"""
```

---

## 🧪 Testing

### Struktura testów

```python
# tests/unit/test_builder.py

import pytest
from unittest.mock import Mock, patch
from tauri_builder import TauriBuilder, BuildConfig

class TestTauriBuilder:
    """Test TauriBuilder class"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return BuildConfig(
            dockerfile=Path("Dockerfile"),
            mode="build",
            platforms=["linux"]
        )
    
    @pytest.fixture
    def builder(self, config):
        """Create builder instance"""
        return TauriBuilder(config)
    
    def test_initialization(self, builder, config):
        """Test builder initialization"""
        assert builder.config == config
        assert builder.docker is not None
    
    @patch('tauri_builder.DockerManager')
    def test_build_process(self, mock_docker, builder):
        """Test build process"""
        mock_docker.build_image.return_value = "image:tag"
        
        result = builder.run()
        
        assert result is not None
        mock_docker.build_image.assert_called()
```

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tauri_builder --cov-report=html

# Run specific test
pytest tests/unit/test_builder.py::TestTauriBuilder::test_initialization

# Run with markers
pytest -m "not slow"

# Watch mode
pytest-watch

# Parallel execution
pytest -n auto
```

### Test fixtures

```python
# tests/conftest.py

import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_config(temp_dir):
    """Create mock configuration"""
    return {
        'dockerfile': temp_dir / 'Dockerfile',
        'mode': 'build',
        'platforms': ['linux'],
        'output_dir': temp_dir / 'dist'
    }

@pytest.fixture
def docker_client(mocker):
    """Mock Docker client"""
    return mocker.MagicMock()
```

---

## 🐛 Debugging

### Debug mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment
export TB_DEBUG=1
export RUST_BACKTRACE=full
```

### Debugging tools

```python
# Use debugger
import pdb
pdb.set_trace()

# Or ipdb for better experience
import ipdb
ipdb.set_trace()

# Or built-in breakpoint (Python 3.7+)
breakpoint()
```

### Remote debugging

```python
# Using debugpy (VS Code)
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()

# Using pydevd (PyCharm)
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=5678)
```

### Performance profiling

```python
# Using cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Code to profile
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

---

## 🤝 Contributing

### Workflow

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Run tests
6. Commit changes
7. Push to branch
8. Create Pull Request

### Commit messages

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat: New feature
fix: Bug fix
docs: Documentation
style: Formatting
refactor: Code restructuring
test: Tests
chore: Maintenance

# Examples
feat(builder): add support for iOS platform
fix(docker): resolve memory leak in container management
docs(api): update REST API documentation
```

### Pull Request template

```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

---

## 🎨 Code Style

### Python style guide

```python
"""
Module docstring describing purpose
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

# Constants in UPPER_CASE
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Class names in PascalCase
class MyClass:
    """Class docstring"""
    
    # Class variables
    class_var: int = 0
    
    def __init__(self, name: str) -> None:
        """Initialize instance
        
        Args:
            name: Instance name
        """
        self.name = name
        self._private_var = None
    
    def public_method(self, param: str) -> str:
        """Public method docstring
        
        Args:
            param: Parameter description
            
        Returns:
            Return value description
            
        Raises:
            ValueError: If param is invalid
        """
        if not param:
            raise ValueError("Param cannot be empty")
        return f"Result: {param}"
    
    def _private_method(self) -> None:
        """Private method (internal use)"""
        pass
    
    @property
    def computed_property(self) -> str:
        """Computed property"""
        return f"Name: {self.name}"
    
    @staticmethod
    def static_method(value: int) -> int:
        """Static method"""
        return value * 2
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MyClass':
        """Create instance from dictionary"""
        return cls(data['name'])

# Functions in snake_case
def helper_function(param1: str, param2: Optional[int] = None) -> bool:
    """Helper function
    
    Args:
        param1: First parameter
        param2: Optional second parameter
        
    Returns:
        Success status
    """
    return True

# Type hints
ConfigDict = Dict[str, Any]
PathList = List[Path]

# Async functions
async def async_function() -> None:
    """Async function"""
    await some_async_operation()
```

### Linting configuration

```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist

[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[pylint]
max-line-length = 88
disable = C0111,R0903

[isort]
profile = black
line_length = 88
```

---

## 📝 Następne Kroki

- [Architecture](./06-ARCHITECTURE.md) - Architektura systemu
- [CI/CD](./07-CI-CD.md) - Continuous Integration
- [Examples](./11-EXAMPLES.md) - Przykładowe implementacje

---

<div align="center">

[← Poprzedni: Konfiguracja](./CONFIG.md) | [Spis treści](./INDEX.md) | [Następny: Architektura →](./06-ARCHITECTURE.md)

</div>