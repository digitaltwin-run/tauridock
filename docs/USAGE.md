# 📖 Przewodnik Użytkowania

[← Poprzedni: Instalacja](./INSTALL.md) | [Spis treści](./INDEX.md) | [Następny: API Reference →](./API.md)

---

## 📋 Spis Treści

- [Podstawowe Komendy](#podstawowe-komendy)
- [Tryby Pracy](#tryby-pracy)
- [Budowanie Aplikacji](#budowanie-aplikacji)
- [Publikowanie](#publikowanie)
- [Przykłady Użycia](#przykłady-użycia)
- [Zaawansowane Scenariusze](#zaawansowane-scenariusze)
- [Best Practices](#best-practices)
- [Tips & Tricks](#tips--tricks)

---

## 🎯 Podstawowe Komendy

### Szybki start

```bash
# Pomoc
tb help
tb --help

# Wersja
tb --version

# Setup projektu
tb setup

# Tryb interaktywny
tb
```

### Struktura komendy

```bash
tb [COMMAND] [OPTIONS] [ARGUMENTS]

# Przykłady:
tb dev --hot-reload
tb build --platforms windows --optimize
tb publish --tag v1.0.0
```

---

## 🔄 Tryby Pracy

### 🔧 Tryb Developerski

Tryb developerski umożliwia szybkie iteracje podczas rozwoju aplikacji.

```bash
# Podstawowe uruchomienie
tb dev

# Z dodatkowymi opcjami
tb dev --hot-reload --devtools --debug

# Z custom portem
tb dev --frontend-port 8080

# Z plikiem środowiskowym
tb dev --env-file .env.development
```

#### Funkcje trybu dev:
- ✅ Hot reload
- ✅ DevTools
- ✅ Source maps
- ✅ Verbose logging
- ✅ Live preview

#### Skróty klawiszowe w trybie dev:
- `Ctrl+R` - Restart aplikacji
- `Ctrl+D` - Otwórz DevTools
- `Ctrl+L` - Wyczyść logi
- `Ctrl+C` - Zatrzymaj serwer

### 🏗️ Tryb Build

Budowanie aplikacji dla produkcji.

```bash
# Build dla wszystkich platform
tb build --all

# Build dla konkretnej platformy
tb build --platforms windows
tb build --platforms macos
tb build --platforms linux

# Build dla wielu platform
tb build --platforms windows,linux

# Build z optymalizacjami
tb build --optimize --sign
```

### 📤 Tryb Publish

Publikowanie aplikacji na GitHub Releases.

```bash
# Podstawowa publikacja
tb publish

# Z custom tagiem
tb publish --tag v2.0.0

# Draft release
tb publish --draft

# Prerelease
tb publish --prerelease

# Z release notes
tb publish --release-notes ./CHANGELOG.md
```

---

## 🏗️ Budowanie Aplikacji

### Platformy

#### Windows

```bash
# Windows x64
tb build --platforms windows --arch x64

# Windows ARM64
tb build --platforms windows --arch arm64

# Wszystkie architektury
tb build --platforms windows --arch x64,arm64

# Specyficzne formaty
tb build --platforms windows --bundle-types msi,nsis,exe

# Z podpisywaniem
tb build --platforms windows --sign --cert-path ./cert.pfx
```

#### macOS

```bash
# macOS Universal (x64 + ARM64)
tb build --platforms macos --arch universal

# Tylko Apple Silicon
tb build --platforms macos --arch arm64

# Z notarization
tb build --platforms macos --notarize --apple-id user@example.com

# Specyficzne formaty
tb build --platforms macos --bundle-types dmg,app
```

#### Linux

```bash
# Linux x64
tb build --platforms linux --arch x64

# Linux ARM64 (Raspberry Pi, etc.)
tb build --platforms linux --arch arm64

# Wszystkie formaty
tb build --platforms linux --bundle-types deb,rpm,AppImage,snap

# Dla konkretnej dystrybucji
tb build --platforms linux --distro ubuntu
```

### Optymalizacje

```bash
# Pełna optymalizacja
tb build --optimize

# Kompresja
tb build --compress

# Minimalizacja
tb build --minimize

# Strip debug symbols
tb build --strip

# Wszystkie optymalizacje
tb build --optimize --compress --minimize --strip
```

### Cache

```bash
# Użyj cache Docker
tb build --docker-cache

# Użyj cache dependencies
tb build --cache-deps

# Wyczyść cache przed budowaniem
tb build --clean-cache

# Użyj zewnętrznego cache
tb build --cache-dir /path/to/cache
```

---

## 📤 Publikowanie

### GitHub Releases

```bash
# Podstawowa publikacja
export GITHUB_TOKEN=your_token
tb publish --github-repo owner/repo

# Z wszystkimi opcjami
tb publish \
  --github-repo owner/repo \
  --tag v1.0.0 \
  --release-name "Release 1.0.0" \
  --release-notes ./CHANGELOG.md \
  --draft false \
  --prerelease false
```

### Automatyczne wersjonowanie

```bash
# Patch release (1.0.0 -> 1.0.1)
tb publish --bump patch

# Minor release (1.0.0 -> 1.1.0)
tb publish --bump minor

# Major release (1.0.0 -> 2.0.0)
tb publish --bump major

# Z automatycznym changelog
tb publish --auto-changelog
```

### Upload artefaktów

```bash
# Upload z checksumami
tb publish --checksums

# Kompresja przed uploadem
tb publish --compress-artifacts

# Upload tylko określonych plików
tb publish --include "*.msi,*.dmg,*.deb"
```

---

## 🎭 Przykłady Użycia

### Przykład 1: Podstawowy Development

```bash
# 1. Setup projektu
cd my-tauri-app
tb setup

# 2. Development
tb dev

# 3. Test build
tb build --platforms linux --arch x64

# 4. Production build
tb build --all --optimize

# 5. Publish
tb publish --tag v1.0.0
```

### Przykład 2: CI/CD Pipeline

```bash
#!/bin/bash
# ci-build.sh

# Setup
pip install -r requirements.txt

# Test
pytest tests/

# Build dla wszystkich platform
tb build \
  --all \
  --optimize \
  --sign \
  --output-dir ./artifacts

# Upload artifacts
if [ "$GITHUB_REF_TYPE" == "tag" ]; then
  tb publish \
    --github-repo $GITHUB_REPOSITORY \
    --tag $GITHUB_REF_NAME \
    --release-notes ./CHANGELOG.md
fi
```

### Przykład 3: Docker Workflow

```bash
# Build Docker image
docker build -t my-tauri-builder .

# Run in Docker
docker run -it --rm \
  -v $(pwd):/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  my-tauri-builder \
  tb build --all

# Lub z docker-compose
docker-compose run tauri-builder tb build --all
```

### Przykład 4: Custom Configuration

```bash
# Z własnym config file
tb build --config ./custom-config.yml

# Override config values
tb build \
  --config .tauri-builder.yml \
  --platforms windows \
  --override "build.optimize=true"

# Z environment variables
export TB_PLATFORMS=windows,linux
export TB_OPTIMIZE=true
tb build
```

---

## 🚀 Zaawansowane Scenariusze

### Cross-compilation

```bash
# Linux -> Windows
tb build \
  --platforms windows \
  --cross-compile \
  --target x86_64-pc-windows-gnu

# macOS -> Linux
tb build \
  --platforms linux \
  --cross-compile \
  --target x86_64-unknown-linux-gnu

# Multiple targets
tb build \
  --cross-compile \
  --targets x86_64-pc-windows-gnu,aarch64-unknown-linux-gnu
```

### Parallel Builds

```bash
# Parallel builds dla wszystkich platform
tb build --all --parallel

# Ogranicz liczbę równoległych zadań
tb build --all --parallel --max-jobs 2

# Sekwencyjne budowanie (default)
tb build --all --no-parallel
```

### Custom Docker Images

```bash
# Użyj custom Docker image
tb build --docker-image my-custom-image:latest

# Build z custom Dockerfile
tb build --dockerfile ./custom/Dockerfile

# Multi-stage build
tb build \
  --dockerfile ./Dockerfile.multistage \
  --docker-target production
```

### Hooks

```bash
# Pre-build hook
tb build --pre-build "npm run lint && npm test"

# Post-build hook
tb build --post-build "./scripts/notify-team.sh"

# Custom hooks z pliku
tb build --hooks ./build-hooks.yml
```

---

## 📚 Best Practices

### 1. Struktura Projektu

```
my-tauri-app/
├── src/                    # Frontend source
├── src-tauri/             # Tauri/Rust source
├── dist/                  # Build output
├── .tauri-builder.yml     # TB config
├── Dockerfile             # Docker config
├── .env                   # Environment variables
└── package.json          # Node.js config
```

### 2. Wersjonowanie

```bash
# Semantic versioning
# MAJOR.MINOR.PATCH
# 1.0.0

# Tag format
git tag v1.0.0
git push origin v1.0.0

# Automatyczne w CI
tb publish --auto-version
```

### 3. Security

```bash
# Zawsze podpisuj releases
tb build --sign

# Używaj secrets dla sensitive data
export SIGNING_KEY=$(vault read -field=key secret/signing)
tb build --sign --key $SIGNING_KEY

# Skanuj security
tb build --security-scan
```

### 4. Performance

```bash
# Cache wszystko co możliwe
tb build --docker-cache --cache-deps

# Parallel builds
tb build --all --parallel

# Optimize size
tb build --optimize --compress --strip
```

### 5. Testing

```bash
# Test przed budowaniem
tb build --pre-build "npm test"

# Smoke test po budowaniu
tb build --post-build "./tests/smoke-test.sh"

# Automated testing
tb test --all-platforms
```

---

## 💡 Tips & Tricks

### Skróty i aliasy

```bash
# Bash/Zsh aliases
alias tbd="tb dev --hot-reload"
alias tbb="tb build --all --optimize"
alias tbp="tb publish"

# PowerShell
Set-Alias -Name tbd -Value "tb dev --hot-reload"
```

### Debug Mode

```bash
# Verbose output
tb build --debug

# Trace mode
RUST_BACKTRACE=full tb build

# Log to file
tb build --log-file build.log

# JSON output
tb build --output json
```

### Performance Tips

1. **Use SSD** - Znacznie przyspiesza budowanie
2. **Increase Docker memory** - Minimum 8GB dla Docker Desktop
3. **Use parallel builds** - `--parallel` dla multi-core
4. **Cache aggressively** - `--docker-cache --cache-deps`
5. **Exclude unnecessary files** - `.dockerignore`

### Common Issues

```bash
# "Out of memory"
tb build --max-memory 4G

# "Docker timeout"
tb build --docker-timeout 3600

# "Network issues"
tb build --retry 3 --retry-delay 10

# "Permission denied"
sudo tb build  # Nie zalecane!
# Lepiej: fix Docker permissions
```

---

## 📊 Monitoring

### Progress Tracking

```bash
# Show progress bar
tb build --progress

# Detailed progress
tb build --progress --verbose

# Export metrics
tb build --metrics ./build-metrics.json
```

### Logging

```bash
# Different log levels
tb build --log-level debug
tb build --log-level info
tb build --log-level warning
tb build --log-level error

# Log rotation
tb build --log-file build.log --log-rotate --log-max-size 10M
```

---

## 🔗 Integracje

### VS Code

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Tauri Dev",
      "type": "shell",
      "command": "tb dev",
      "problemMatcher": []
    },
    {
      "label": "Tauri Build",
      "type": "shell",
      "command": "tb build --all",
      "problemMatcher": []
    }
  ]
}
```

### npm scripts

```json
// package.json
{
  "scripts": {
    "tauri:dev": "tb dev",
    "tauri:build": "tb build --all",
    "tauri:publish": "tb publish"
  }
}
```

---

## 📝 Następne Kroki

- [API Reference](./API.md) - Pełna dokumentacja API
- [Configuration](./CONFIG.md) - Zaawansowana konfiguracja
- [CI/CD](./07-CI-CD.md) - Automatyzacja
- [Examples](./11-EXAMPLES.md) - Więcej przykładów

---

<div align="center">

[← Poprzedni: Instalacja](./INSTALL.md) | [Spis treści](./INDEX.md) | [Następny: API Reference →](./API.md)

</div>