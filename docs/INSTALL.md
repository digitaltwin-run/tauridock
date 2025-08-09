# 📦 Instalacja i Konfiguracja

[← Powrót do spisu treści](./INDEX.md) | [Następny: Przewodnik użytkowania →](./USAGE.md)

---

## 📋 Spis Treści

- [Wymagania Systemowe](#wymagania-systemowe)
- [Instalacja Krok po Kroku](#instalacja-krok-po-kroku)
- [Instalacja Globalna](#instalacja-globalna)
- [Instalacja przez Docker](#instalacja-przez-docker)
- [Weryfikacja Instalacji](#weryfikacja-instalacji)
- [Szybka Konfiguracja](#szybka-konfiguracja)
- [Rozwiązywanie Problemów](#rozwiązywanie-problemów)

---

## 🖥️ Wymagania Systemowe

### Minimalne wymagania

| Komponent | Wymaganie | Zalecane |
|-----------|-----------|----------|
| **System operacyjny** | Windows 10+, macOS 10.15+, Ubuntu 20.04+ | Najnowsze wersje |
| **Python** | 3.8+ | 3.11+ |
| **Docker** | 20.10+ | Latest stable |
| **RAM** | 8 GB | 16 GB |
| **Dysk** | 20 GB wolnego miejsca | 50 GB |
| **CPU** | 4 rdzenie | 8 rdzeni |
| **Internet** | Wymagany | Szybkie łącze |

### Dodatkowe wymagania dla development

- **Git** 2.25+
- **Node.js** 18+ (dla frontendu Tauri)
- **Rust** 1.70+ (opcjonalnie, dla native builds)

---

## 🚀 Instalacja Krok po Kroku

### 1️⃣ Klonowanie repozytorium

```bash
# Przez HTTPS
git clone https://github.com/digitaltwin-run/tauridock.git

# Przez SSH
git clone git@github.com:digitaltwin-run/tauridock.git

# Wejście do katalogu
cd tauridock
```

### 2️⃣ Instalacja Python i zależności

#### Windows

```powershell
# Instalacja Python (jeśli nie masz)
winget install Python.Python.3.11

# Lub pobierz z python.org
# https://www.python.org/downloads/

# Utworzenie środowiska wirtualnego
python -m venv venv

# Aktywacja środowiska
.\venv\Scripts\Activate.ps1

# Instalacja zależności
pip install -r requirements.txt
```

#### macOS

```bash
# Instalacja Python przez Homebrew
brew install python@3.11

# Utworzenie środowiska wirtualnego
python3 -m venv venv

# Aktywacja środowiska
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian)

```bash
# Aktualizacja pakietów
sudo apt update

# Instalacja Python i pip
sudo apt install python3.11 python3-pip python3-venv

# Utworzenie środowiska wirtualnego
python3 -m venv venv

# Aktywacja środowiska
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

### 3️⃣ Instalacja Docker

#### Windows

1. Pobierz [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Uruchom installer
3. Restart systemu
4. Uruchom Docker Desktop

```powershell
# Weryfikacja
docker --version
docker run hello-world
```

#### macOS

```bash
# Przez Homebrew
brew install --cask docker

# Uruchom Docker Desktop
open -a Docker

# Weryfikacja
docker --version
```

#### Linux

```bash
# Usunięcie starych wersji
sudo apt remove docker docker-engine docker.io containerd runc

# Instalacja zależności
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release

# Dodanie klucza GPG Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Dodanie repozytorium
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalacja Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Dodanie użytkownika do grupy docker
sudo usermod -aG docker $USER
newgrp docker

# Weryfikacja
docker --version
docker run hello-world
```

---

## 🌍 Instalacja Globalna

### Metoda 1: pip install

```bash
# Instalacja w trybie edytowalnym
pip install -e .

# Lub instalacja standardowa
pip install .

# Weryfikacja
tauridock --version
tb --version  # Skrót
```

### Metoda 2: setuptools

```bash
# Budowanie pakietu
python setup.py sdist bdist_wheel

# Instalacja
pip install dist/tauri_builder-1.0.0-py3-none-any.whl

# Weryfikacja
which tauridock
```

### Metoda 3: Make

```bash
# Użycie Makefile
make install-global

# Weryfikacja
tb --version
```

---

## 🐳 Instalacja przez Docker

### Opcja 1: Użycie gotowego obrazu

```bash
# Pobranie obrazu z Docker Hub
docker pull digitaltwin-run/tauridock:latest

# Lub z GitHub Container Registry
docker pull ghcr.io/digitaltwin-run/tauridock:latest

# Uruchomienie
docker run -it --rm \
  -v $(pwd):/app \
  -p 3000:3000 \
  digitaltwin-run/tauridock:latest
```

### Opcja 2: Budowanie lokalnie

```bash
# Budowanie obrazu
docker build -t tauridock:local .

# Uruchomienie
docker run -it --rm \
  -v $(pwd):/app \
  -p 3000:3000 \
  tauridock:local
```

### Opcja 3: Docker Compose

```bash
# Uruchomienie wszystkich serwisów
docker-compose up -d

# Sprawdzenie statusu
docker-compose ps

# Logi
docker-compose logs -f
```

---

## ✅ Weryfikacja Instalacji

### Automatyczna weryfikacja

```bash
# Uruchom skrypt weryfikacyjny
./scripts/verify-installation.sh

# Lub użyj Make
make verify
```

### Manualna weryfikacja

```bash
# 1. Sprawdź Python
python --version
# Oczekiwany output: Python 3.8+

# 2. Sprawdź pip
pip --version

# 3. Sprawdź Docker
docker --version
docker ps

# 4. Sprawdź tauridock
python tauridock.py --version
# Lub jeśli zainstalowane globalnie
tb --version

# 5. Sprawdź zależności
pip list | grep -E "click|docker|PyYAML|rich|PyGithub"

# 6. Test podstawowy
python tauridock.py --help
```

### Test funkcjonalny

```bash
# Utwórz przykładowy projekt
mkdir test-project
cd test-project

# Inicjalizacja
tb setup

# Sprawdź utworzone pliki
ls -la
# Powinny być: Dockerfile, .tauridock.yml, .env

# Test budowania
tb build --platforms linux --arch x64 --dry-run
```

---

## ⚡ Szybka Konfiguracja

### Użycie interaktywnego setup

```bash
# Uruchom wizard konfiguracji
./tb.sh setup

# Lub
python tauridock.py setup --interactive
```

### Konfiguracja manualna

#### 1. Utwórz plik konfiguracyjny

```yaml
# .tauridock.yml
dockerfile: ./Dockerfile
frontend_port: 3000
platforms:
  - windows
  - macos
  - linux
architectures:
  - x64
build:
  optimize: true
  output_dir: ./dist
docker:
  image: rust:1.75
  cache: true
```

#### 2. Utwórz plik środowiskowy

```bash
# .env
GITHUB_TOKEN=your_github_token_here
DOCKER_HOST=unix:///var/run/docker.sock
FRONTEND_PORT=3000
NODE_ENV=production
RUST_BACKTRACE=1
```

#### 3. Skopiuj Dockerfile

```bash
# Użyj przykładowego Dockerfile
cp examples/Dockerfile ./Dockerfile

# Lub utwórz własny
cat > Dockerfile << 'EOF'
FROM rust:1.75
# Twoja konfiguracja...
EOF
```

---

## 🔧 Konfiguracja zaawansowana

### Proxy konfiguracja

```bash
# Dla pip
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Dla Docker
mkdir -p ~/.docker
cat > ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:8080",
      "httpsProxy": "http://proxy.example.com:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
EOF
```

### Konfiguracja dla różnych shell

#### Bash

```bash
# ~/.bashrc
echo 'alias tb="python /path/to/tauridock.py"' >> ~/.bashrc
echo 'export TAURI_BUILDER_HOME="/path/to/tauridock"' >> ~/.bashrc
source ~/.bashrc
```

#### Zsh

```bash
# ~/.zshrc
echo 'alias tb="python /path/to/tauridock.py"' >> ~/.zshrc
echo 'export TAURI_BUILDER_HOME="/path/to/tauridock"' >> ~/.zshrc
source ~/.zshrc
```

#### PowerShell

```powershell
# $PROFILE
Add-Content $PROFILE @"
function tb {
    python C:\path\to\tauridock.py `$args
}
`$env:TAURI_BUILDER_HOME = "C:\path\to\tauridock"
"@
```

---

## 🐛 Rozwiązywanie Problemów

### Problem: "Docker daemon not running"

```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS
open -a Docker

# Windows
# Uruchom Docker Desktop
```

### Problem: "Permission denied" dla Docker

```bash
# Linux - dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER
newgrp docker

# Restart terminal
```

### Problem: "Module not found"

```bash
# Reinstalacja zależności
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Lub użyj pipenv
pipenv install
pipenv shell
```

### Problem: "Python version mismatch"

```bash
# Użyj pyenv do zarządzania wersjami
curl https://pyenv.run | bash

# Instalacja konkretnej wersji
pyenv install 3.11.0
pyenv local 3.11.0
```

---

## 📝 Następne Kroki

Po pomyślnej instalacji:

1. **[Przeczytaj przewodnik użytkowania](./USAGE.md)** - Naucz się podstawowych komend
2. **[Skonfiguruj projekt](./CONFIG.md)** - Dostosuj ustawienia
3. **[Uruchom przykład](./11-EXAMPLES.md)** - Zobacz działający przykład
4. **[Dołącz do społeczności](https://discord.gg/tauridock)** - Uzyskaj pomoc

---

## 📚 Dodatkowe zasoby

- [Dokumentacja Docker](https://docs.docker.com/)
- [Dokumentacja Python](https://docs.python.org/3/)
- [Tauri Docs](https://tauri.app/docs/)
- [Troubleshooting Guide](./09-TROUBLESHOOTING.md)

---

<div align="center">

[← Powrót do spisu treści](./INDEX.md) | [Następny: Przewodnik użytkowania →](./USAGE.md)

</div>