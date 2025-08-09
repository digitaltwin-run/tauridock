# ⚙️ Konfiguracja

[← Poprzedni: API Reference](./03-API-REFERENCE.md) | [Spis treści](./INDEX.md) | [Następny: Developer Guide →](./05-DEVELOPER-GUIDE.md)

---

## 📋 Spis Treści

- [Plik Konfiguracyjny](#plik-konfiguracyjny)
- [Zmienne Środowiskowe](#zmienne-środowiskowe)
- [Dockerfile Configuration](#dockerfile-configuration)
- [Platform-Specific Settings](#platform-specific-settings)
- [Bundle Configuration](#bundle-configuration)
- [Security Settings](#security-settings)
- [CI/CD Configuration](#cicd-configuration)
- [Advanced Options](#advanced-options)

---

## 📄 Plik Konfiguracyjny

### Lokalizacja

Tauri Builder szuka pliku konfiguracyjnego w następującej kolejności:

1. `--config` parameter
2. `.tauri-builder.yml`
3. `.tauri-builder.yaml`
4. `tauri-builder.yml`
5. `tauri-builder.yaml`
6. `.tb.yml`
7. `~/.config/tauri-builder/config.yml`

### Struktura podstawowa

```yaml
# .tauri-builder.yml
version: 1  # Wersja formatu konfiguracji

# Podstawowe ustawienia
project:
  name: "MyTauriApp"
  version: "1.0.0"
  description: "My awesome Tauri application"
  author: "Your Name <email@example.com>"
  license: "MIT"
  homepage: "https://example.com"

# Docker configuration
docker:
  dockerfile: ./Dockerfile
  image: rust:1.75
  cache: true
  buildkit: true
  
# Build configuration  
build:
  frontend_port: 3000
  platforms:
    - windows
    - macos
    - linux
  architectures:
    - x64
    - arm64
  output_dir: ./dist
  optimize: true
  
# Publishing
publish:
  github_repo: owner/repo
  auto_release: true
```

### Pełna struktura

```yaml
# Wersja formatu
version: 1

# Informacje o projekcie
project:
  name: "MyTauriApp"
  version: "1.0.0"
  description: "Application description"
  author: "Author Name <email@example.com>"
  license: "MIT"
  homepage: "https://example.com"
  repository: "https://github.com/owner/repo"
  keywords:
    - tauri
    - desktop
    - app
  categories:
    - Development
    - Productivity

# Docker configuration
docker:
  # Dockerfile path
  dockerfile: ./Dockerfile
  
  # Base image
  image: rust:1.75-slim
  
  # Build arguments
  build_args:
    NODE_VERSION: "20"
    RUST_VERSION: "1.75"
    TAURI_CLI_VERSION: "1.5"
  
  # Docker BuildKit
  buildkit: true
  
  # Cache settings
  cache: true
  cache_from:
    - type=registry,ref=myregistry.com/myapp:cache
  cache_to:
    - type=registry,ref=myregistry.com/myapp:cache,mode=max
  
  # Network
  network: bridge
  
  # Volumes
  volumes:
    - ./cache:/cache
    - ./node_modules:/app/node_modules:cached
  
  # Environment
  environment:
    DOCKER_BUILDKIT: "1"
    COMPOSE_DOCKER_CLI_BUILD: "1"
  
  # Resources
  resources:
    memory: 4g
    cpus: "2.0"
    
  # Registry
  registry:
    url: myregistry.com
    username: ${REGISTRY_USERNAME}
    password: ${REGISTRY_PASSWORD}

# Build configuration
build:
  # Development server port
  frontend_port: 3000
  backend_port: 1420
  
  # Target platforms
  platforms:
    - windows
    - macos
    - linux
  
  # Target architectures
  architectures:
    - x64
    - arm64
  
  # Output directory
  output_dir: ./dist
  
  # Build mode
  mode: release  # debug, release, or custom
  
  # Optimizations
  optimize: true
  minimize: true
  strip: true
  compress: true
  
  # Signing
  sign: true
  
  # Parallel builds
  parallel: true
  max_jobs: 4
  
  # Timeout (seconds)
  timeout: 3600
  
  # Clean before build
  clean: true
  
  # Custom build commands
  pre_build:
    - npm run lint
    - npm run test
  
  post_build:
    - ./scripts/validate.sh
    
  # Environment variables
  env:
    NODE_ENV: production
    RUST_BACKTRACE: 1

# Platform-specific settings
platforms:
  windows:
    # Rust target
    rust_target:
      x64: x86_64-pc-windows-msvc
      x86: i686-pc-windows-msvc
      arm64: aarch64-pc-windows-msvc
    
    # Bundle types
    bundles:
      - msi
      - nsis
      - exe
    
    # Signing
    sign:
      certificate: ./certs/windows.pfx
      password: ${WINDOWS_CERT_PASSWORD}
      timestamp_url: http://timestamp.digicert.com
      algorithm: sha256
    
    # Windows-specific settings
    settings:
      webview_install_mode: embedBootstrapper
      allow_downgrades: false
      license: ./LICENSE.rtf
      
    # WiX settings (for MSI)
    wix:
      language: en-US
      banner: ./assets/banner.bmp
      dialog: ./assets/dialog.bmp
      license: ./LICENSE.rtf
      
    # NSIS settings
    nsis:
      installer_icon: ./icons/installer.ico
      header_image: ./assets/header.bmp
      sidebar_image: ./assets/sidebar.bmp
      install_mode: both  # both, currentUser, perMachine
      languages:
        - English
        - Spanish
        - French
  
  macos:
    # Rust target
    rust_target:
      x64: x86_64-apple-darwin
      arm64: aarch64-apple-darwin
      universal: universal-apple-darwin
    
    # Bundle types
    bundles:
      - dmg
      - app
      - pkg
    
    # Signing
    sign:
      identity: "Developer ID Application: Your Name (TEAMID)"
      entitlements: ./entitlements.plist
      hardened_runtime: true
      
    # Notarization
    notarize:
      enabled: true
      apple_id: ${APPLE_ID}
      password: ${APPLE_PASSWORD}
      team_id: ${APPLE_TEAM_ID}
      
    # macOS-specific settings
    settings:
      minimum_system_version: "10.15"
      exception_domain: ""
      frameworks: []
      info_plist_additions: {}
      
    # DMG settings
    dmg:
      background: ./assets/dmg-background.png
      window_size:
        width: 600
        height: 400
      icon_size: 128
      contents:
        - x: 150
          y: 200
          type: file
        - x: 450
          y: 200
          type: link
          path: /Applications
  
  linux:
    # Rust target
    rust_target:
      x64: x86_64-unknown-linux-gnu
      x86: i686-unknown-linux-gnu
      arm64: aarch64-unknown-linux-gnu
      arm: armv7-unknown-linux-gnueabihf
    
    # Bundle types
    bundles:
      - deb
      - rpm
      - AppImage
      - snap
      - flatpak
    
    # Dependencies
    dependencies:
      deb:
        - libwebkit2gtk-4.0-37
        - libgtk-3-0
      rpm:
        - webkit2gtk3
        - gtk3
      
    # Desktop entry
    desktop_entry:
      name: MyTauriApp
      comment: My awesome Tauri application
      categories:
        - Development
        - Utility
      keywords:
        - tauri
        - app
      startup_notify: true
      
    # AppImage settings
    appimage:
      runtime_version: continuous
      update_information: "gh-releases-zsync|owner|repo|latest|*.AppImage.zsync"
      
    # Snap settings
    snap:
      grade: stable
      confinement: strict
      base: core20
      slots:
        - desktop
        - desktop-legacy
        - wayland
        
    # Flatpak settings
    flatpak:
      runtime: org.freedesktop.Platform
      runtime_version: "21.08"
      sdk: org.freedesktop.Sdk
      finish_args:
        - "--share=network"
        - "--socket=x11"
        - "--socket=wayland"

# Bundle configuration
bundles:
  # Icon paths
  icons:
    - icons/32x32.png
    - icons/128x128.png
    - icons/128x128@2x.png
    - icons/icon.icns
    - icons/icon.ico
  
  # Resources to include
  resources:
    - assets/
    - data/config.json
  
  # External binaries
  external_bin:
    - bins/my-sidecar
  
  # File associations
  file_associations:
    - ext: myapp
      name: MyApp Document
      description: MyApp document file
      role: Editor
      mime_type: application/x-myapp

# Development settings
development:
  # Hot reload
  hot_reload: true
  
  # DevTools
  devtools: true
  
  # Watch paths
  watch:
    - src/
    - src-tauri/
    - public/
  
  # Ignore paths
  ignore:
    - node_modules/
    - target/
    - dist/
  
  # Server settings
  server:
    host: 0.0.0.0
    port: 3000
    https: false
    open: true
    
  # Environment file
  env_file: .env.development

# Publishing configuration
publish:
  # GitHub settings
  github:
    repo: owner/repo
    token: ${GITHUB_TOKEN}
    draft: false
    prerelease: false
    
  # Release settings
  release:
    auto_tag: true
    tag_format: "v{version}"
    name_format: "Release {version}"
    notes_file: CHANGELOG.md
    auto_changelog: true
    
  # Assets
  assets:
    include:
      - "dist/**/*.{msi,exe,dmg,deb,AppImage}"
    exclude:
      - "*.log"
      - "*.tmp"
    compress: true
    checksums: true
    
  # Channels
  channels:
    - stable
    - beta
    - nightly
    
  # Update server
  update_server:
    url: https://updates.example.com
    public_key: ${UPDATE_PUBLIC_KEY}

# Security settings
security:
  # CSP (Content Security Policy)
  csp: "default-src 'self'; script-src 'self' 'unsafe-inline'"
  
  # Dangerous allow list
  dangerous_allow_all: false
  
  # Freeze prototype
  freeze_prototype: true
  
  # Asset protocol
  asset_protocol:
    scope:
      - $APP/*
      - $RESOURCE/*
    
  # Permissions
  permissions:
    - window:allow-create
    - window:allow-close
    - fs:allow-read
    - fs:allow-write

# CI/CD configuration
ci:
  # GitHub Actions
  github_actions:
    enabled: true
    workflows:
      - build
      - test
      - release
    
  # GitLab CI
  gitlab_ci:
    enabled: false
    file: .gitlab-ci.yml
    
  # Jenkins
  jenkins:
    enabled: false
    file: Jenkinsfile
    
  # CircleCI
  circleci:
    enabled: false
    file: .circleci/config.yml

# Hooks
hooks:
  # Lifecycle hooks
  pre_install:
    - echo "Installing dependencies..."
    
  post_install:
    - echo "Dependencies installed"
    
  pre_build:
    - npm run lint
    - npm run test
    
  post_build:
    - ./scripts/validate.sh
    
  pre_publish:
    - ./scripts/prepare-release.sh
    
  post_publish:
    - ./scripts/notify-team.sh

# Notifications
notifications:
  # Discord
  discord:
    enabled: true
    webhook: ${DISCORD_WEBHOOK}
    events:
      - build.success
      - build.failure
      - publish.success
      
  # Slack
  slack:
    enabled: false
    webhook: ${SLACK_WEBHOOK}
    channel: "#releases"
    
  # Email
  email:
    enabled: false
    smtp:
      host: smtp.gmail.com
      port: 587
      username: ${SMTP_USERNAME}
      password: ${SMTP_PASSWORD}
    recipients:
      - team@example.com

# Cache settings
cache:
  enabled: true
  directory: ./.cache
  
  # What to cache
  items:
    - cargo
    - npm
    - rust-artifacts
    - docker-layers
    
  # TTL in days
  ttl: 7
  
  # Max size
  max_size: 10GB
  
  # Compression
  compress: true

# Logging
logging:
  # Log level
  level: info  # debug, info, warning, error
  
  # Output
  output:
    - console
    - file
    
  # File settings
  file:
    path: ./tauri-builder.log
    rotate: true
    max_size: 10MB
    max_files: 5
    
  # Format
  format: json  # text, json
  
  # Include timestamps
  timestamps: true

# Advanced options
advanced:
  # Retry policy
  retry:
    enabled: true
    max_attempts: 3
    delay: 5
    backoff: exponential
    
  # Timeouts
  timeouts:
    build: 3600
    docker: 600
    network: 30
    
  # Parallel execution
  parallel:
    enabled: true
    max_workers: 4
    
  # Dry run
  dry_run: false
  
  # Verbose output
  verbose: false
  
  # Metrics
  metrics:
    enabled: true
    export: ./metrics.json
    
  # Telemetry
  telemetry:
    enabled: false
    endpoint: https://telemetry.example.com

# Environment variable substitution
env:
  # Variables that will be replaced in config
  GITHUB_TOKEN: ${GITHUB_TOKEN}
  APPLE_ID: ${APPLE_ID}
  WINDOWS_CERT_PASSWORD: ${WINDOWS_CERT_PASSWORD}
```

---

## 🌍 Zmienne Środowiskowe

### Plik `.env`

```bash
# .env
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=owner/repo

# Apple (macOS)
APPLE_ID=developer@example.com
APPLE_PASSWORD=@keychain:AC_PASSWORD
APPLE_TEAM_ID=XXXXXXXXXX

# Windows
WINDOWS_CERT_PASSWORD=certificate_password

# Docker
DOCKER_REGISTRY=myregistry.com
REGISTRY_USERNAME=username
REGISTRY_PASSWORD=password

# Notifications
DISCORD_WEBHOOK=https://discord.com/api/webhooks/xxx
SLACK_WEBHOOK=https://hooks.slack.com/services/xxx

# Build
NODE_ENV=production
RUST_BACKTRACE=1
RUST_LOG=info

# Paths
TAURI_BUILDER_HOME=/opt/tauri-builder
TB_CONFIG=./.tauri-builder.yml

# Features
TB_TELEMETRY=false
TB_ANALYTICS=false
```

### System Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TB_CONFIG` | Config file path | `.tauri-builder.yml` |
| `TB_HOME` | Tauri Builder home | `~/.tauri-builder` |
| `TB_CACHE` | Cache directory | `~/.tauri-builder/cache` |
| `TB_LOG_LEVEL` | Log level | `info` |
| `TB_PARALLEL` | Enable parallel builds | `true` |
| `TB_DOCKER_IMAGE` | Default Docker image | `rust:latest` |
| `TB_TIMEOUT` | Build timeout (seconds) | `3600` |

### Precedence

1. Command line arguments
2. Environment variables
3. Config file
4. Defaults

---

## 🐳 Dockerfile Configuration

### Multi-stage Dockerfile

```dockerfile
# Build stage arguments
ARG RUST_VERSION=1.75
ARG NODE_VERSION=20
ARG PLATFORM=linux
ARG ARCH=x64

# Base stage
FROM rust:${RUST_VERSION} AS base
# Common dependencies...

# Platform-specific stages
FROM base AS linux-builder
# Linux-specific...

FROM base AS windows-builder
# Windows-specific...

FROM base AS macos-builder
# macOS-specific...

# Final stage
FROM ${PLATFORM}-builder AS final
# Final configuration...
```

### Build Arguments

```yaml
docker:
  build_args:
    RUST_VERSION: "1.75"
    NODE_VERSION: "20"
    TAURI_CLI_VERSION: "1.5"
    CUSTOM_ARG: "value"
```

---

## 🎯 Platform-Specific Settings

### Windows Configuration

```yaml
platforms:
  windows:
    # Specific Windows SDK version
    sdk_version: "10.0.22621.0"
    
    # Visual Studio version
    vs_version: "2022"
    
    # Target Windows version
    target_version: "10"
    min_version: "10"
    
    # UWP settings
    uwp:
      enabled: false
      capabilities:
        - internetClient
        - privateNetworkClientServer
```

### macOS Configuration

```yaml
platforms:
  macos:
    # Xcode version
    xcode_version: "14.0"
    
    # SDK settings
    sdk: macosx
    deployment_target: "10.15"
    
    # Universal binary
    universal:
      enabled: true
      architectures:
        - x86_64
        - arm64
```

### Linux Configuration

```yaml
platforms:
  linux:
    # Distribution-specific
    distros:
      ubuntu:
        versions: ["20.04", "22.04"]
        dependencies:
          - libwebkit2gtk-4.0-dev
          
      fedora:
        versions: ["37", "38"]
        dependencies:
          - webkit2gtk3-devel
```

---

## 📝 Następne Kroki

- [Developer Guide](./05-DEVELOPER-GUIDE.md) - Rozszerzanie funkcjonalności
- [Architecture](./06-ARCHITECTURE.md) - Architektura systemu
- [Examples](./11-EXAMPLES.md) - Przykładowe konfiguracje

---

<div align="center">

[← Poprzedni: API Reference](./03-API-REFERENCE.md) | [Spis treści](./INDEX.md) | [Następny: Developer Guide →](./05-DEVELOPER-GUIDE.md)

</div>