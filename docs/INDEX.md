# 📚 Tauri Builder - Dokumentacja

<div align="center">

![Tauri Builder Logo](./assets/logo.png)

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-required-blue)](https://www.docker.com)

**Zaawansowane narzędzie CLI do budowania aplikacji Tauri dla wszystkich platform**

[Szybki Start](./INSTALL.md) | [Przewodnik](./USAGE.md) | [API](./API.md) | [FAQ](./10-FAQ.md)

</div>

---

## 📖 Spis Treści

### 🚀 Rozpoczęcie Pracy

1. **[Instalacja](./INSTALL.md)**
   - Wymagania systemowe
   - Instalacja krok po kroku
   - Weryfikacja instalacji
   - Szybka konfiguracja

2. **[Przewodnik Użytkowania](./USAGE.md)**
   - Podstawowe komendy
   - Tryby pracy
   - Przykłady użycia
   - Best practices

3. **[Dokumentacja API](./API.md)**
   - Parametry CLI
   - Python API
   - REST API
   - Odpowiedzi i kody błędów

### 🔧 Konfiguracja i Rozwój

4. **[Konfiguracja](./CONFIG.md)**
   - Plik konfiguracyjny YAML
   - Zmienne środowiskowe
   - Dockerfile customization
   - Platform-specific settings

5. **[Przewodnik Developera](./05-DEVELOPER-GUIDE.md)**
   - Struktura projektu
   - Rozszerzanie funkcjonalności
   - Tworzenie pluginów
   - Contributing guidelines

6. **[Architektura](./06-ARCHITECTURE.md)**
   - Diagram architektury
   - Komponenty systemu
   - Flow budowania
   - Decyzje projektowe

### 🔄 Integracje i Deployment

7. **[CI/CD](./07-CI-CD.md)**
   - GitHub Actions
   - GitLab CI
   - Jenkins
   - Azure DevOps

8. **[Docker](./08-DOCKER.md)**
   - Budowanie obrazów
   - Multi-stage builds
   - Optymalizacja
   - Registry management

### 📘 Pomoc i Wsparcie

9. **[Rozwiązywanie Problemów](./09-TROUBLESHOOTING.md)**
   - Częste problemy
   - Kody błędów
   - Debugging
   - Logi i monitoring

10. **[FAQ](./10-FAQ.md)**
    - Najczęściej zadawane pytania
    - Tips & tricks
    - Znane ograniczenia
    - Roadmap

### 📚 Dodatkowe Zasoby

11. **[Przykłady](./11-EXAMPLES.md)**
    - Przykładowe projekty
    - Case studies
    - Recepty
    - Integracje

12. **[Changelog](./CHANGELOG.md)**
    - Historia wersji
    - Breaking changes
    - Migration guides

---

## 🎯 Kluczowe Funkcjonalności

| Funkcja | Opis | Dokumentacja |
|---------|------|--------------|
| 🚀 **Multi-platform** | Buduj dla Windows, macOS, Linux | [Platformy](./USAGE.md#platformy) |
| 🐳 **Docker Integration** | Izolowane środowisko budowania | [Docker](./08-DOCKER.md) |
| 📦 **Auto-packaging** | MSI, DMG, DEB, AppImage | [Pakowanie](./CONFIG.md#bundle-types) |
| 🔄 **Hot Reload** | Development z live reload | [Dev Mode](./USAGE.md#tryb-developerski) |
| 📤 **GitHub Releases** | Automatyczna publikacja | [Publishing](./07-CI-CD.md#github-releases) |
| 🔧 **CI/CD Ready** | Pełna integracja | [CI/CD](./07-CI-CD.md) |
| 🎯 **Cross-compilation** | ARM64 i x64 | [Architektury](./06-ARCHITECTURE.md#cross-compilation) |
| 📝 **YAML Config** | Elastyczna konfiguracja | [Config](./CONFIG.md) |

---

## 💡 Szybki Start

### Minimalna konfiguracja

```bash
# Instalacja
pip install -r requirements.txt

# Pierwsze uruchomienie
./tb.sh setup

# Development
./tb.sh dev

# Build
./tb.sh build --all
```

### Przykład użycia

```python
from tauri_builder import TauriBuilder, BuildConfig

config = BuildConfig(
    dockerfile=Path("Dockerfile"),
    frontend_port=3000,
    mode="build",
    platforms=["windows", "linux"],
    optimize=True
)

builder = TauriBuilder(config)
builder.run()
```

---

## 🗺️ Mapa Dokumentacji

```mermaid
graph TD
    A[INDEX] --> B[INSTALL]
    B --> C[USAGE]
    C --> D[API]
    
    A --> E[CONFIG]
    E --> F[05-DEVELOPER-GUIDE]
    F --> G[06-ARCHITECTURE]
    
    A --> H[07-CI-CD]
    H --> I[08-DOCKER]
    
    A --> J[09-TROUBLESHOOTING]
    J --> K[10-FAQ]
    
    A --> L[11-EXAMPLES]
    L --> M[CHANGELOG]
```

---

## 📊 Status Projektu

| Komponent | Status | Wersja | Testy |
|-----------|--------|--------|-------|
| Core CLI | ✅ Stable | 1.0.0 | ![Coverage](https://img.shields.io/badge/coverage-95%25-green) |
| Docker Builder | ✅ Stable | 1.0.0 | ![Tests](https://img.shields.io/badge/tests-passing-green) |
| GitHub Publisher | ✅ Stable | 1.0.0 | ![Tests](https://img.shields.io/badge/tests-passing-green) |
| Cross-compilation | 🔄 Beta | 0.9.0 | ![Tests](https://img.shields.io/badge/tests-partial-yellow) |
| ARM64 Support | 🔄 Beta | 0.9.0 | ![Tests](https://img.shields.io/badge/tests-partial-yellow) |
| Web UI | 📅 Planned | - | - |

---

## 🤝 Wsparcie

- 📧 **Email**: support@tauridock.com
- 💬 **Discord**: [Join our server](https://discord.gg/tauridock)
- 🐛 **Issues**: [GitHub Issues](https://github.com/digitaltwin-run/tauridock/issues)
- 📖 **Wiki**: [GitHub Wiki](https://github.com/digitaltwin-run/tauridock/wiki)

---

## 📜 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz [LICENSE](../LICENSE) dla szczegółów.

---

<div align="center">

**[⬆ Powrót do góry](#-tauridock---dokumentacja)**

Stworzone z ❤️ dla społeczności Tauri

</div>