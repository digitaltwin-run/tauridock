# 🔌 API Reference

[← Poprzedni: Przewodnik użytkowania](./USAGE.md) | [Spis treści](./INDEX.md) | [Następny: Konfiguracja →](./CONFIG.md)

---

## 📋 Spis Treści

- [CLI API](#cli-api)
- [Python API](#python-api)
- [REST API](#rest-api)
- [Docker API](#docker-api)
- [Kody Błędów](#kody-błędów)
- [Typy Danych](#typy-danych)
- [Webhooks](#webhooks)
- [Events](#events)

---

## 🖥️ CLI API

### Składnia podstawowa

```bash
tauri-builder [OPTIONS] [COMMAND] [ARGS]
tb [OPTIONS] [COMMAND] [ARGS]  # Alias
```

### Globalne opcje

| Opcja | Skrót | Opis | Domyślnie |
|-------|-------|------|-----------|
| `--help` | `-h` | Wyświetla pomoc | - |
| `--version` | `-v` | Wyświetla wersję | - |
| `--config FILE` | `-c` | Ścieżka do pliku konfiguracyjnego | `.tauri-builder.yml` |
| `--verbose` | `-V` | Tryb verbose | `false` |
| `--quiet` | `-q` | Tryb cichy | `false` |
| `--debug` | `-d` | Tryb debug | `false` |
| `--json` | `-j` | Output w formacie JSON | `false` |
| `--no-color` | - | Wyłącza kolorowanie | `false` |

### Komendy

#### `dev` - Tryb developerski

```bash
tb dev [OPTIONS]
```

**Opcje:**

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--hot-reload` | Włącza hot reload | `true` |
| `--devtools` | Otwiera devtools | `false` |
| `--watch` | Monitoruje zmiany plików | `true` |
| `--frontend-port PORT` | Port dla frontendu | `3000` |
| `--backend-port PORT` | Port dla backendu | `1420` |
| `--host HOST` | Host address | `localhost` |
| `--env-file FILE` | Plik środowiskowy | `.env` |
| `--browser` | Otwiera w przeglądarce | `false` |

**Przykłady:**

```bash
tb dev
tb dev --hot-reload --devtools
tb dev --frontend-port 8080 --browser
```

#### `build` - Budowanie aplikacji

```bash
tb build [OPTIONS]
```

**Opcje:**

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--platforms PLATFORMS` | Platformy docelowe | `current` |
| `--arch ARCHITECTURES` | Architektury | `x64` |
| `--mode MODE` | Tryb budowania | `release` |
| `--optimize` | Włącza optymalizacje | `false` |
| `--sign` | Podpisuje aplikację | `false` |
| `--compress` | Kompresuje output | `false` |
| `--bundle-types TYPES` | Typy pakietów | `auto` |
| `--output-dir DIR` | Katalog wyjściowy | `./dist` |
| `--parallel` | Budowanie równoległe | `false` |
| `--max-jobs N` | Max parallel jobs | `CPU cores` |
| `--clean` | Czyści przed budowaniem | `false` |
| `--docker-image IMAGE` | Docker image | `rust:latest` |
| `--docker-cache` | Użyj Docker cache | `true` |
| `--dry-run` | Symulacja | `false` |

**Przykłady:**

```bash
tb build --platforms windows --arch x64
tb build --platforms windows,linux --optimize --sign
tb build --all --parallel --max-jobs 4
```

#### `publish` - Publikowanie

```bash
tb publish [OPTIONS]
```

**Opcje:**

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--github-repo REPO` | Repository GitHub | from config |
| `--github-token TOKEN` | GitHub token | `$GITHUB_TOKEN` |
| `--tag TAG` | Release tag | auto |
| `--release-name NAME` | Nazwa release | auto |
| `--release-notes FILE` | Release notes | `CHANGELOG.md` |
| `--draft` | Draft release | `false` |
| `--prerelease` | Pre-release | `false` |
| `--assets PATTERN` | Assets pattern | `dist/*` |
| `--checksums` | Generuj checksums | `true` |
| `--compress-assets` | Kompresuj assets | `false` |

**Przykłady:**

```bash
tb publish --tag v1.0.0
tb publish --github-repo owner/repo --draft
tb publish --prerelease --release-notes ./notes.md
```

#### `test` - Testowanie

```bash
tb test [OPTIONS]
```

**Opcje:**

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--unit` | Testy jednostkowe | `true` |
| `--integration` | Testy integracyjne | `false` |
| `--e2e` | Testy E2E | `false` |
| `--coverage` | Generuj coverage | `false` |
| `--watch` | Watch mode | `false` |
| `--bail` | Stop on first fail | `false` |

#### `clean` - Czyszczenie

```bash
tb clean [OPTIONS]
```

**Opcje:**

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--dist` | Czyść dist | `true` |
| `--cache` | Czyść cache | `false` |
| `--docker` | Czyść Docker | `false` |
| `--all` | Czyść wszystko | `false` |

---

## 🐍 Python API

### Import

```python
from tauri_builder import (
    TauriBuilder,
    BuildConfig,
    DockerManager,
    PlatformBuilder,
    GitHubPublisher
)
```

### Klasy główne

#### `BuildConfig`

```python
@dataclass
class BuildConfig:
    """Konfiguracja budowania"""
    
    dockerfile: Path
    frontend_port: int = 3000
    mode: str = "build"
    platforms: List[str] = field(default_factory=lambda: ["current"])
    architectures: List[str] = field(default_factory=lambda: ["x64"])
    app_name: str = "TauriApp"
    version: str = "1.0.0"
    output_dir: Path = Path("./dist")
    optimize: bool = False
    sign: bool = False
    bundle_types: Dict[str, List[str]] = field(default_factory=dict)
    docker_image: str = "rust:latest"
    docker_cache: bool = True
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    release_tag: Optional[str] = None
    release_notes: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
```

**Przykład użycia:**

```python
config = BuildConfig(
    dockerfile=Path("./Dockerfile"),
    frontend_port=3000,
    mode="build",
    platforms=["windows", "linux"],
    architectures=["x64", "arm64"],
    optimize=True,
    sign=True
)
```

#### `TauriBuilder`

```python
class TauriBuilder:
    """Główna klasa buildera"""
    
    def __init__(self, config: BuildConfig):
        """Inicjalizacja buildera"""
        
    def run(self) -> Dict[str, Any]:
        """Uruchomienie procesu budowania"""
        
    def build(self, platform: str, arch: str) -> List[Path]:
        """Budowanie dla konkretnej platformy"""
        
    def publish(self, artifacts: Dict[str, List[Path]]) -> str:
        """Publikowanie artefaktów"""
```

**Przykład użycia:**

```python
# Inicjalizacja
builder = TauriBuilder(config)

# Budowanie
results = builder.run()

# Lub budowanie dla konkretnej platformy
artifacts = builder.build("windows", "x64")

# Publikowanie
release_url = builder.publish({"windows-x64": artifacts})
```

#### `DockerManager`

```python
class DockerManager:
    """Zarządzanie kontenerami Docker"""
    
    def __init__(self, config: BuildConfig):
        """Inicjalizacja"""
        
    def build_image(self, platform: str, arch: str) -> str:
        """Budowanie obrazu Docker"""
        
    def run_container(
        self, 
        image: str, 
        command: str,
        volumes: Dict = None,
        ports: Dict = None,
        environment: Dict = None
    ) -> Tuple[int, str]:
        """Uruchomienie kontenera"""
        
    def run_dev_container(self, image: str, project_path: Path):
        """Uruchomienie kontenera dev"""
```

**Przykład użycia:**

```python
docker = DockerManager(config)

# Build image
image_tag = docker.build_image("linux", "x64")

# Run container
status, logs = docker.run_container(
    image=image_tag,
    command="cargo build --release",
    volumes={"/host/path": {"bind": "/container/path", "mode": "rw"}}
)

# Dev mode
docker.run_dev_container(image_tag, Path.cwd())
```

#### `PlatformBuilder`

```python
class PlatformBuilder:
    """Builder dla konkretnych platform"""
    
    PLATFORM_CONFIG = {
        'windows': {...},
        'macos': {...},
        'linux': {...}
    }
    
    def build_for_platform(
        self, 
        platform: str, 
        arch: str
    ) -> List[Path]:
        """Build dla platformy"""
        
    def get_rust_target(self, platform: str, arch: str) -> str:
        """Pobierz Rust target"""
```

**Przykład użycia:**

```python
platform_builder = PlatformBuilder(config, docker_manager)

# Build for Windows x64
artifacts = platform_builder.build_for_platform("windows", "x64")

# Get Rust target
target = platform_builder.get_rust_target("linux", "arm64")
# Returns: "aarch64-unknown-linux-gnu"
```

#### `GitHubPublisher`

```python
class GitHubPublisher:
    """Publikowanie na GitHub"""
    
    def __init__(self, config: BuildConfig):
        """Inicjalizacja z tokenem"""
        
    def create_release(
        self, 
        artifacts: Dict[str, List[Path]]
    ) -> str:
        """Tworzenie release"""
        
    def upload_asset(
        self, 
        release_id: str, 
        file_path: Path
    ) -> bool:
        """Upload pojedynczego pliku"""
```

**Przykład użycia:**

```python
publisher = GitHubPublisher(config)

# Create release
release_url = publisher.create_release({
    "windows-x64": [Path("app.msi")],
    "linux-x64": [Path("app.deb")]
})

print(f"Release created: {release_url}")
```

### Funkcje pomocnicze

```python
# Config management
def load_config(path: Path) -> Dict[str, Any]:
    """Wczytaj konfigurację z pliku"""

def merge_configs(*configs: Dict) -> Dict:
    """Połącz konfiguracje"""

# File operations
def calculate_checksum(file: Path) -> str:
    """Oblicz SHA256"""

def compress_file(file: Path, format: str = "zip") -> Path:
    """Kompresuj plik"""

# Validation
def validate_platform(platform: str) -> bool:
    """Waliduj platformę"""

def validate_architecture(arch: str) -> bool:
    """Waliduj architekturę"""
```

---

## 🌐 REST API

### Endpoints

#### `GET /status`

Sprawdza status serwera.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "builds_in_progress": 2
}
```

#### `POST /build`

Rozpoczyna proces budowania.

**Request:**
```json
{
  "platforms": ["windows", "linux"],
  "architectures": ["x64"],
  "optimize": true,
  "sign": false
}
```

**Response:**
```json
{
  "build_id": "uuid-1234",
  "status": "started",
  "estimated_time": 300
}
```

#### `GET /build/{build_id}`

Pobiera status budowania.

**Response:**
```json
{
  "build_id": "uuid-1234",
  "status": "in_progress",
  "progress": 45,
  "current_step": "Building Windows x64",
  "logs": ["Step 1 complete", "Step 2 in progress"]
}
```

#### `GET /build/{build_id}/artifacts`

Pobiera artefakty budowania.

**Response:**
```json
{
  "artifacts": [
    {
      "platform": "windows",
      "arch": "x64",
      "file": "app-1.0.0-x64.msi",
      "size": 52428800,
      "checksum": "sha256:abc123...",
      "download_url": "/download/uuid-1234/app-1.0.0-x64.msi"
    }
  ]
}
```

#### `POST /publish`

Publikuje release.

**Request:**
```json
{
  "build_id": "uuid-1234",
  "github_repo": "owner/repo",
  "tag": "v1.0.0",
  "draft": false
}
```

**Response:**
```json
{
  "release_id": "release-5678",
  "url": "https://github.com/owner/repo/releases/tag/v1.0.0",
  "assets_uploaded": 4
}
```

### Autentykacja

```http
Authorization: Bearer <token>
X-API-Key: <api-key>
```

### Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

---

## 🐳 Docker API

### Environment Variables

| Zmienna | Opis | Domyślnie |
|---------|------|-----------|
| `MODE` | Tryb pracy (dev/build/publish) | `build` |
| `PLATFORM` | Platforma docelowa | `linux` |
| `ARCH` | Architektura | `x64` |
| `FRONTEND_PORT` | Port frontendu | `3000` |
| `RUST_BACKTRACE` | Rust backtrace | `1` |
| `NODE_ENV` | Node environment | `production` |
| `DOCKER_BUILDKIT` | Docker BuildKit | `1` |

### Volumes

| Host Path | Container Path | Opis |
|-----------|---------------|------|
| `./` | `/app` | Kod źródłowy |
| `./dist` | `/dist` | Output |
| `~/.cargo` | `/root/.cargo` | Cargo cache |
| `./node_modules` | `/app/node_modules` | Node modules |

### Ports

| Port | Opis |
|------|------|
| `3000` | Frontend dev server |
| `1420` | Tauri dev server |
| `1421` | HMR WebSocket |

---

## ❌ Kody Błędów

### CLI Exit Codes

| Kod | Znaczenie |
|-----|-----------|
| `0` | Sukces |
| `1` | Ogólny błąd |
| `2` | Błąd parametrów |
| `3` | Błąd konfiguracji |
| `4` | Błąd Docker |
| `5` | Błąd budowania |
| `6` | Błąd publikacji |
| `7` | Błąd sieci |
| `8` | Błąd autoryzacji |
| `9` | Timeout |
| `10` | Przerwane przez użytkownika |

### HTTP Status Codes

| Kod | Znaczenie |
|-----|-----------|
| `200` | OK |
| `201` | Created |
| `202` | Accepted |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `409` | Conflict |
| `422` | Unprocessable Entity |
| `429` | Too Many Requests |
| `500` | Internal Server Error |
| `503` | Service Unavailable |

### Error Response Format

```json
{
  "error": {
    "code": "BUILD_FAILED",
    "message": "Build failed for Windows x64",
    "details": {
      "platform": "windows",
      "arch": "x64",
      "step": "compilation",
      "logs": ["error details..."]
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req-123456"
  }
}
```

---

## 📊 Typy Danych

### Platform

```typescript
type Platform = "windows" | "macos" | "linux";
```

### Architecture

```typescript
type Architecture = "x64" | "x86" | "arm64" | "arm" | "universal";
```

### BundleType

```typescript
type BundleType = {
  windows: ["msi", "nsis", "exe"],
  macos: ["dmg", "app", "pkg"],
  linux: ["deb", "rpm", "AppImage", "snap", "flatpak"]
};
```

### BuildMode

```typescript
type BuildMode = "dev" | "build" | "publish";
```

### BuildStatus

```typescript
type BuildStatus = 
  | "pending"
  | "started"
  | "in_progress"
  | "completed"
  | "failed"
  | "cancelled";
```

---

## 🔔 Webhooks

### Konfiguracja

```yaml
webhooks:
  - url: https://example.com/webhook
    events:
      - build.started
      - build.completed
      - build.failed
    secret: webhook_secret
```

### Events

| Event | Opis | Payload |
|-------|------|---------|
| `build.started` | Build rozpoczęty | `{build_id, platforms, timestamp}` |
| `build.completed` | Build zakończony | `{build_id, artifacts, duration}` |
| `build.failed` | Build nieudany | `{build_id, error, logs}` |
| `publish.started` | Publikacja rozpoczęta | `{release_id, tag}` |
| `publish.completed` | Publikacja zakończona | `{release_id, url, assets}` |

### Payload Example

```json
{
  "event": "build.completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "build_id": "uuid-1234",
    "platforms": ["windows", "linux"],
    "duration": 300,
    "artifacts": [
      {
        "platform": "windows",
        "arch": "x64",
        "file": "app.msi",
        "size": 52428800
      }
    ]
  }
}
```

---

## 📡 Events

### Event System

```python
from tauri_builder.events import EventEmitter

# Create emitter
emitter = EventEmitter()

# Subscribe to events
@emitter.on("build.progress")
def on_progress(data):
    print(f"Progress: {data['percentage']}%")

# Emit events
emitter.emit("build.progress", {"percentage": 50})
```

### Available Events

| Event | Description | Data |
|-------|-------------|------|
| `build.progress` | Build progress update | `{percentage, step, message}` |
| `docker.image.built` | Docker image built | `{image_tag, size}` |
| `artifact.created` | Artifact created | `{path, size, checksum}` |
| `release.published` | Release published | `{url, tag, assets}` |

---

## 📝 Następne Kroki

- [Konfiguracja](./CONFIG.md) - Szczegółowa konfiguracja
- [Developer Guide](./05-DEVELOPER-GUIDE.md) - Rozszerzanie funkcjonalności
- [Examples](./11-EXAMPLES.md) - Przykłady użycia API

---

<div align="center">

[← Poprzedni: Przewodnik użytkowania](./USAGE.md) | [Spis treści](./INDEX.md) | [Następny: Konfiguracja →](./CONFIG.md)

</div>