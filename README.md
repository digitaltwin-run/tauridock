# tauridock
Python CLI Script dla Tauri Multi-Platform Builder
# 🦀 Tauri Builder CLI

[![Build Status](https://github.com/digitaltwin-run/tauri-builder/workflows/Tauri%20Build%20and%20Release/badge.svg)](https://github.com/digitaltwin-run/tauri-builder/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/digitaltwin-run/tauri-builder)](https://hub.docker.com/r/digitaltwin-run/tauri-builder)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

Zaawansowane narzędzie CLI do budowania aplikacji Tauri dla wszystkich platform (Windows, macOS, Linux) z wykorzystaniem Docker dla zapewnienia spójnego środowiska budowania.

## ✨ Funkcje

- 🚀 **Multi-platform builds** - Buduj dla Windows, macOS i Linux z jednego miejsca
- 🐳 **Docker integration** - Izolowane, powtarzalne środowisko budowania
- 📦 **Automatyczne pakowanie** - Generowanie MSI, DMG, DEB, AppImage i więcej
- 🔄 **Hot reload** - Tryb developerski z automatycznym przeładowaniem
- 📤 **GitHub Releases** - Automatyczna publikacja na GitHub
- 🔧 **CI/CD Ready** - Integracja z GitHub Actions, GitLab CI, Jenkins
- 🎯 **Cross-compilation** - Buduj dla ARM64 i x64
- 📝 **Konfiguracja YAML** - Elastyczna konfiguracja przez plik
- 🔔 **Powiadomienia** - Discord, Slack, email
- ✅ **Testy jednostkowe** - Pełne pokrycie testami

## 📋 Wymagania

- Python 3.8+
- Docker Desktop lub Docker Engine
- Git
- 8GB RAM (minimum)
- 20GB wolnego miejsca na dysku

## 🚀 Szybki start

### Instalacja

```bash
# Klonuj repozytorium
git clone https://github.com/digitaltwin-run/tauri-builder.git
cd tauri-builder

# Zainstaluj zależności
pip install -r requirements.txt

# Opcjonalnie: Zainstaluj globalnie
pip install -e .
```

### Podstawowe użycie

```bash
# Tryb developerski
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode dev

# Budowanie dla wszystkich platform
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode build

# Publikacja na GitHub
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode publish \
  --github-token $GITHUB_TOKEN --github-repo owner/repo
```

## 📖 Szczegółowa dokumentacja

### Parametry CLI

#### Wymagane parametry

| Parametr | Opis | Przykład |
|----------|------|----------|
| `--dockerfile` | Ścieżka do Dockerfile | `./Dockerfile` |
| `--frontend-port` | Port frontendu | `3000` |

#### Tryby pracy

| Tryb | Opis | Użycie |
|------|------|--------|
| `dev` | Tryb developerski z hot-reload | Rozwój aplikacji |
| `build` | Budowanie dla produkcji | Tworzenie release |
| `publish` | Budowanie i publikacja | Automatyczne release |

#### Parametry opcjonalne

##### Platformy i architektury

```bash
# Buduj tylko dla Windows x64
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --platforms windows --arch x64

# Buduj dla Linux ARM64
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --platforms linux --arch arm64

# Buduj dla wielu platform
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --platforms windows,macos,linux --arch x64,arm64
```

##### Opcje developmentu

```bash
# Development z hot-reload i devtools
python tauri-builder.py --dockerfile ./Dockerfile --mode dev \
  --hot-reload --devtools --debug

# Z plikiem środowiskowym
python tauri-builder.py --dockerfile ./Dockerfile --mode dev \
  --env-file .env.local --watch
```

##### Opcje budowania

```bash
# Budowanie z optymalizacjami i podpisywaniem
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --optimize --sign --bundle-types '{"windows": ["msi", "nsis"]}'

# Własna nazwa i wersja
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --app-name "MyApp" --version "2.0.0" --output-dir ./releases
```

##### Publikacja na GitHub

```bash
# Pełna publikacja z release notes
python tauri-builder.py --dockerfile ./Dockerfile --mode publish \
  --github-token $GITHUB_TOKEN \
  --github-repo owner/repo \
  --release-tag v1.0.0 \
  --release-notes ./CHANGELOG.md \
  --draft false \
  --prerelease false
```

### Konfiguracja przez plik YAML

Utwórz plik `.tauri-builder.yml` w katalogu projektu:

```yaml
dockerfile: ./Dockerfile
frontend_port: 3000
mode: build

platforms:
  - windows
  - macos
  - linux

architectures:
  - x64
  - arm64

build:
  optimize: true
  sign: true
  output_dir: ./dist

bundle_types:
  windows: [msi, nsis]
  macos: [dmg]
  linux: [deb, AppImage]

publish:
  github_repo: owner/repo
  draft: false
  prerelease: false
```

Następnie uruchom:

```bash
python tauri-builder.py --config .tauri-builder.yml
```

### Struktura Dockerfile

Przykładowy Dockerfile znajduje się w repozytorium. Kluczowe elementy:

```dockerfile
# Multi-stage build dla różnych platform
FROM rust:1.75 AS base

# Instalacja Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Instalacja Tauri CLI
RUN cargo install tauri-cli

# Platform-specific stages
FROM base AS linux-builder
# Linux dependencies...

FROM base AS windows-builder
# Windows cross-compilation...

FROM base AS macos-builder
# macOS cross-compilation...
```

## 🐳 Docker

### Budowanie obrazu Docker

```bash
# Buduj obraz lokalnie
docker build -t tauri-builder .

# Buduj dla wielu platform
docker buildx build --platform linux/amd64,linux/arm64 -t tauri-builder .
```

### Używanie gotowego obrazu

```bash
# Pobierz obraz z Docker Hub
docker pull digitaltwin-run/tauri-builder:latest

# Lub z GitHub Container Registry
docker pull ghcr.io/digitaltwin-run/tauri-builder:latest
```

### Uruchomienie w kontenerze

```bash
# Tryb developerski
docker run -it --rm \
  -v $(pwd):/app \
  -p 3000:3000 \
  -e MODE=dev \
  tauri-builder

# Budowanie
docker run -it --rm \
  -v $(pwd):/app \
  -v $(pwd)/dist:/dist \
  -e MODE=build \
  -e PLATFORM=linux \
  -e ARCH=x64 \
  tauri-builder
```

## 🔄 CI/CD

### GitHub Actions

Workflow znajduje się w `.github/workflows/tauri-build.yml`:

```yaml
name: Build Tauri App

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build with Tauri Builder
        run: |
          python tauri-builder.py \
            --dockerfile ./Dockerfile \
            --mode build \
            --platforms windows,macos,linux
```

### GitLab CI

`.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - release

build:
  stage: build
  image: python:3.11
  services:
    - docker:dind
  script:
    - pip install -r requirements.txt
    - python tauri-builder.py --dockerfile ./Dockerfile --mode build
  artifacts:
    paths:
      - dist/
```

### Jenkins

`Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python tauri-builder.py --dockerfile ./Dockerfile --mode build'
            }
        }
        
        stage('Publish') {
            when {
                tag pattern: "v\\d+\\.\\d+\\.\\d+", comparator: "REGEXP"
            }
            steps {
                sh 'python tauri-builder.py --dockerfile ./Dockerfile --mode publish'
            }
        }
    }
}
```

## 🧪 Testowanie

### Uruchomienie testów

```bash
# Wszystkie testy
pytest test_tauri_builder.py -v

# Z coverage
pytest test_tauri_builder.py --cov=tauri_builder --cov-report=html

# Tylko określone testy
pytest test_tauri_builder.py::TestDockerManager -v
```

### Struktura testów

```
tests/
├── test_tauri_builder.py     # Główne testy jednostkowe
├── test_integration.py        # Testy integracyjne
├── test_docker.py            # Testy Docker
├── test_platforms.py         # Testy platform
└── fixtures/                 # Dane testowe
```

## 📊 Monitoring i Logi

### Poziomy logowania

```bash
# Debug mode - wszystkie logi
python tauri-builder.py --dockerfile ./Dockerfile --mode build --debug

# Tylko błędy
LOG_LEVEL=ERROR python tauri-builder.py --dockerfile ./Dockerfile --mode build
```

### Lokalizacja logów

- Domyślnie: `./tauri-builder.log`
- Docker logs: `docker logs <container_id>`
- CI/CD: Artefakty w systemie CI

## 🔧 Rozwiązywanie problemów

### Częste problemy

#### Docker nie działa

```bash
# Linux
sudo systemctl start docker
sudo usermod -aG docker $USER

# macOS
open -a Docker

# Windows
# Uruchom Docker Desktop
```

#### Brak pamięci podczas budowania

```bash
# Zwiększ pamięć Docker
# Docker Desktop: Settings -> Resources -> Memory

# Lub buduj sekwencyjnie
python tauri-builder.py --dockerfile ./Dockerfile --mode build \
  --platforms windows --arch x64
```

#### Błędy cross-compilation

```bash
# Zainstaluj brakujące toolchains
rustup target add x86_64-pc-windows-gnu
rustup target add aarch64-unknown-linux-gnu
```

## 🤝 Współpraca

### Jak pomóc

1. Fork repozytorium
2. Stwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmiany (`git commit -m 'Add AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

### Zgłaszanie błędów

Używaj [GitHub Issues](https://github.com/digitaltwin-run/tauri-builder/issues) z następującymi informacjami:

- Wersja Python i Docker
- System operacyjny
- Pełny log błędu
- Kroki do reprodukcji

## 📄 Licencja

Projekt jest dostępny na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 🙏 Podziękowania

- [Tauri](https://tauri.app/) - Framework do budowania aplikacji
- [Docker](https://www.docker.com/) - Konteneryzacja
- [Rich](https://github.com/Textualize/rich) - Piękne CLI
- Społeczność open source

## 📚 Dodatkowe zasoby

- [Dokumentacja Tauri](https://tauri.app/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Rust Cross-compilation](https://rust-lang.github.io/rustup/cross-compilation.html)

## 🗺️ Roadmap

- [ ] Wsparcie dla iOS i Android (Tauri 2.0)
- [ ] Web assembly builds
- [ ] Automatyczne testowanie UI
- [ ] Integracja z innymi registry (npm, cargo)
- [ ] GUI dla konfiguracji
- [ ] Cloud builds (AWS, GCP, Azure)
- [ ] Podpisywanie certyfikatami EV
- [ ] Automatyczna walidacja pakietów

---

Stworzone z ❤️ dla społeczności Tauri

## Python CLI Script dla Tauri Multi-Platform Builder

Skrypt command-line w Pythonie, który automatyzuje proces budowania aplikacji Tauri dla wszystkich platform (Windows, macOS, Linux) wykorzystując Docker jako środowisko budowania.


### 1. Nazwa skryptu
`tauri-builder.py`

### 2. Zależności
- Python 3.8+
- Biblioteki: `click`, `docker`, `pyyaml`, `requests`, `rich` (dla kolorowego outputu)
- Docker API client
- Git Python library (dla integracji z GitHub)

### 3. Parametry CLI

#### Wymagane parametry:
- `--dockerfile PATH` - ścieżka do Dockerfile używanego do budowania
- `--frontend-port PORT` - port na którym serwowany jest frontend (domyślnie: 3000)

#### Parametry opcjonalne:

##### Tryby pracy:
- `--mode {dev|build|publish}` - tryb działania skryptu
  - `dev` - uruchamia aplikację w trybie developerskim
  - `build` - buduje aplikację dla produkcji
  - `publish` - buduje i publikuje na GitHub Releases

##### Platformy docelowe:
- `--platforms PLATFORMS` - lista platform oddzielona przecinkami (domyślnie: "windows,macos,linux")
- `--arch ARCHITECTURES` - architektury CPU (domyślnie: "x64,arm64")

##### Opcje developmentu:
- `--hot-reload` - włącza hot-reload dla frontendu
- `--debug` - włącza tryb debug z verbose logging
- `--devtools` - otwiera devtools w aplikacji
- `--watch` - monitoruje zmiany w kodzie źródłowym
- `--env-file PATH` - ścieżka do pliku .env z zmiennymi środowiskowymi

##### Opcje budowania:
- `--app-name NAME` - nazwa aplikacji (domyślnie: pobiera z tauri.conf.json)
- `--version VERSION` - wersja aplikacji (domyślnie: pobiera z package.json)
- `--output-dir PATH` - katalog wyjściowy dla zbudowanych aplikacji
- `--sign` - podpisuje aplikacje (wymaga certyfikatów)
- `--optimize` - włącza optymalizacje produkcyjne
- `--bundle-types TYPES` - typy pakietów (AppImage, deb, msi, dmg, etc.)
- `--icon PATH` - ścieżka do ikony aplikacji
- `--config PATH` - ścieżka do niestandardowego tauri.conf.json

##### Opcje publikowania:
- `--github-token TOKEN` - token GitHub dla autoryzacji
- `--github-repo REPO` - repozytorium w formacie "owner/repo"
- `--release-tag TAG` - tag dla release (domyślnie: v{version})
- `--release-name NAME` - nazwa release
- `--release-notes PATH` - ścieżka do pliku z release notes
- `--draft` - tworzy draft release
- `--prerelease` - oznacza jako prerelease
- `--assets-only` - aktualizuje tylko assety w istniejącym release

##### Opcje Docker:
- `--docker-image IMAGE` - bazowy obraz Docker (domyślnie: rust:latest)
- `--docker-cache` - używa cache Docker
- `--docker-network NETWORK` - sieć Docker
- `--docker-volumes VOLUMES` - dodatkowe wolumeny Docker
- `--docker-env VARS` - zmienne środowiskowe dla kontenera

## Struktura skryptu

### Moduły/Klasy:
1. **TauriBuilder** - główna klasa zarządzająca procesem
2. **DockerManager** - zarządza kontenerami Docker
3. **PlatformBuilder** - logika budowania dla każdej platformy
4. **GitHubPublisher** - obsługa publikacji na GitHub
5. **ConfigManager** - zarządzanie konfiguracją Tauri
6. **Logger** - zaawansowane logowanie z kolorami

### Funkcjonalności szczegółowe:

#### Tryb Development:
- Uruchamia kontener Docker z mapowaniem portów
- Montuje lokalne pliki źródłowe jako volume
- Uruchamia `tauri dev` z hot-reload
- Wyświetla logi w czasie rzeczywistym
- Automatycznie restartuje przy zmianach

#### Tryb Build:
- Tworzy osobne kontenery dla każdej platformy
- Instaluje wymagane zależności (Node.js, Rust, Tauri CLI)
- Buduje frontend (npm/yarn/pnpm)
- Kompiluje aplikację Tauri
- Generuje instalatory/pakiety dla każdej platformy
- Kopiuje artefakty do lokalnego systemu plików

#### Tryb Publish:
- Wykonuje pełny build dla wszystkich platform
- Tworzy lub aktualizuje GitHub Release
- Uploaduje wszystkie zbudowane artefakty
- Generuje checksums (SHA256) dla każdego pliku
- Opcjonalnie generuje changelog

## Przykłady użycia

```bash
# Development mode
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode dev --hot-reload

# Build dla wszystkich platform
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode build --platforms windows,macos,linux --optimize

# Build tylko dla Windows x64
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode build --platforms windows --arch x64

# Publikacja na GitHub
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 3000 --mode publish \
  --github-token $GITHUB_TOKEN --github-repo myuser/myapp --release-tag v1.0.0

# Development z custom config
python tauri-builder.py --dockerfile ./Dockerfile --frontend-port 8080 --mode dev \
  --config ./custom-tauri.conf.json --env-file .env.local --debug
```

## Format Dockerfile

Dockerfile powinien zawierać:
- Multi-stage build dla różnych platform
- Instalację Node.js, Rust, i Tauri CLI
- Konfigurację cross-compilation dla różnych platform
- Instalację zależności systemowych (webkit2gtk dla Linux, etc.)

## Output i logowanie

### Format logów:
- Kolorowe logi z poziomami: DEBUG, INFO, WARNING, ERROR
- Timestamps dla każdej operacji
- Progress bars dla długich operacji
- Podsumowanie na końcu z listą zbudowanych artefaktów

### Struktura outputu:
```
dist/
├── windows/
│   ├── MyApp_1.0.0_x64.msi
│   └── MyApp_1.0.0_x64.exe
├── macos/
│   ├── MyApp_1.0.0_x64.dmg
│   └── MyApp_1.0.0_arm64.dmg
└── linux/
    ├── MyApp_1.0.0_amd64.deb
    ├── MyApp_1.0.0_amd64.AppImage
    └── MyApp_1.0.0_amd64.rpm
```

## Obsługa błędów

- Walidacja wszystkich parametrów przed rozpoczęciem
- Sprawdzanie dostępności Docker daemon
- Weryfikacja istnienia plików (Dockerfile, configs)
- Graceful shutdown przy Ctrl+C
- Automatyczne czyszczenie kontenerów po zakończeniu
- Retry logic dla operacji sieciowych
- Szczegółowe komunikaty błędów z sugestiami rozwiązań

## Konfiguracja przez plik

Obsługa pliku konfiguracyjnego `.tauri-builder.yml`:
```yaml
dockerfile: ./Dockerfile
frontend_port: 3000
platforms:
  - windows
  - macos
  - linux
architectures:
  - x64
  - arm64
build:
  optimize: true
  sign: true
  bundle_types:
    windows: [msi, nsis]
    macos: [dmg, app]
    linux: [deb, AppImage, rpm]
publish:
  github_repo: owner/repo
  draft: false
  prerelease: false
docker:
  image: rust:1.70
  cache: true
```

## Dodatkowe wymagania

1. **Walidacja środowiska**: Sprawdzanie wersji Docker, dostępnej pamięci, miejsca na dysku
2. **Parallel builds**: Możliwość równoległego budowania dla różnych platform
3. **Caching**: Inteligentne cachowanie zależności Node i Rust
4. **Hooks**: Pre-build i post-build hooks dla custom logiki
5. **Notifications**: Opcjonalne powiadomienia (Discord, Slack) o statusie budowania
6. **Metrics**: Zbieranie metryk czasu budowania i rozmiaru artefaktów
7. **Rollback**: Możliwość cofnięcia publikacji w przypadku błędu
8. **Dry-run**: Tryb symulacji bez faktycznego budowania/publikowania

## Integracja CI/CD

Skrypt powinien być kompatybilny z:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

