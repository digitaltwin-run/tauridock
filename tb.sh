#!/bin/bash

# Tauri Builder CLI Wrapper
# Provides convenient shortcuts and environment management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="${PYTHON_CMD:-python3}"
CONFIG_FILE="${CONFIG_FILE:-.tauridock.yml}"
ENV_FILE="${ENV_FILE:-.env}"

# Version
VERSION="1.0.0"

# Load environment variables if .env exists
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
fi

# Functions
print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       🦀 Tauri Builder CLI v$VERSION      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo
}

print_help() {
    print_header
    cat << EOF
${GREEN}Usage:${NC} tb [command] [options]

${GREEN}Commands:${NC}
  ${YELLOW}dev${NC}        Start development server with hot-reload
  ${YELLOW}build${NC}      Build application for production
  ${YELLOW}publish${NC}    Build and publish to GitHub Releases
  ${YELLOW}test${NC}       Run tests
  ${YELLOW}docker${NC}     Docker operations
  ${YELLOW}setup${NC}      Initial project setup
  ${YELLOW}clean${NC}      Clean build artifacts
  ${YELLOW}help${NC}       Show this help message

${GREEN}Quick Commands:${NC}
  ${YELLOW}win${NC}        Build for Windows
  ${YELLOW}mac${NC}        Build for macOS
  ${YELLOW}linux${NC}      Build for Linux
  ${YELLOW}all${NC}        Build for all platforms
  ${YELLOW}arm${NC}        Build for ARM64

${GREEN}Options:${NC}
  --config FILE    Use custom config file (default: .tauridock.yml)
  --port PORT      Frontend port (default: 3003)
  --debug          Enable debug mode
  --docker         Use Docker for building
  --native         Use native toolchain

${GREEN}Examples:${NC}
  ${BLUE}tb dev${NC}                    # Start development server
  ${BLUE}tb build --all${NC}           # Build for all platforms
  ${BLUE}tb win --optimize${NC}        # Build optimized Windows version
  ${BLUE}tb publish --tag v1.0${NC}    # Publish release
  ${BLUE}tb docker build${NC}          # Build Docker image
  ${BLUE}tb test --coverage${NC}       # Run tests with coverage

${GREEN}Environment Variables:${NC}
  GITHUB_TOKEN     GitHub token for publishing
  DOCKER_HOST      Docker daemon host
  TB_CONFIG        Default config file path
  TB_DEBUG         Enable debug mode (1/0)

EOF
}

check_requirements() {
    local missing=()

    # Check Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        missing+=("Python 3.8+")
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing+=("Docker")
    fi

    # Check Git
    if ! command -v git &> /dev/null; then
        missing+=("Git")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing requirements:${NC}"
        printf '%s\n' "${missing[@]}"
        echo
        echo -e "${YELLOW}Please install missing requirements and try again.${NC}"
        exit 1
    fi
}

run_tauri_builder() {
    local cmd="$PYTHON_CMD $SCRIPT_DIR/tauridock.py"

    # Add default options
    if [ -f "$CONFIG_FILE" ]; then
        cmd="$cmd --config $CONFIG_FILE"
    fi

    if [ -f "Dockerfile" ]; then
        cmd="$cmd --dockerfile ./Dockerfile"
    else
        echo -e "${YELLOW}Warning: Dockerfile not found in current directory${NC}"
    fi

    # Add frontend port if not specified
    if [[ ! "$@" =~ "--frontend-port" ]]; then
        cmd="$cmd --frontend-port ${FRONTEND_PORT:-3003}"
    fi

    # Execute command
    echo -e "${GREEN}Running:${NC} $cmd $@"
    eval $cmd "$@"
}

# Command handlers
cmd_dev() {
    echo -e "${GREEN}Starting development server...${NC}"
    run_tauri_builder --mode dev --hot-reload --devtools "$@"
}

cmd_build() {
    echo -e "${GREEN}Building application...${NC}"
    run_tauri_builder --mode build --optimize "$@"
}

cmd_publish() {
    echo -e "${GREEN}Publishing to GitHub...${NC}"

    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}Error: GITHUB_TOKEN not set${NC}"
        echo "Please set GITHUB_TOKEN environment variable or add it to .env file"
        exit 1
    fi

    run_tauri_builder --mode publish "$@"
}

cmd_test() {
    echo -e "${GREEN}Running tests...${NC}"

    if [[ "$@" =~ "--coverage" ]]; then
        pytest test_tauri_builder.py --cov=tauri_builder --cov-report=html -v
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    else
        pytest test_tauri_builder.py -v "$@"
    fi
}

cmd_docker() {
    local subcmd="${1:-build}"
    shift || true

    case "$subcmd" in
        build)
            echo -e "${GREEN}Building Docker image...${NC}"
            docker build -t tauridock:latest .
            ;;
        run)
            echo -e "${GREEN}Running Docker container...${NC}"
            docker run -it --rm \
                -v $(pwd):/app \
                -p 3003:3003 \
                tauridock:latest "$@"
            ;;
        compose)
            echo -e "${GREEN}Starting Docker Compose...${NC}"
            docker-compose up -d "$@"
            ;;
        push)
            echo -e "${GREEN}Pushing Docker image...${NC}"
            docker push tauridock:latest
            ;;
        *)
            echo -e "${RED}Unknown docker command: $subcmd${NC}"
            exit 1
            ;;
    esac
}

cmd_setup() {
    echo -e "${GREEN}Setting up Tauri Builder...${NC}"

    # Install Python dependencies
    echo "Installing Python dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt

    # Create default config if not exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Creating default configuration..."
        cat > "$CONFIG_FILE" << 'EOF'
dockerfile: ./Dockerfile
frontend_port: 3003
platforms:
  - windows
  - macos
  - linux
architectures:
  - x64
build:
  optimize: true
  output_dir: ./dist
EOF
        echo -e "${GREEN}Created $CONFIG_FILE${NC}"
    fi

    # Create .env file if not exists
    if [ ! -f "$ENV_FILE" ]; then
        echo "Creating .env file..."
        cat > "$ENV_FILE" << 'EOF'
# GitHub Token for publishing
# GITHUB_TOKEN=your_token_here

# Docker settings
# DOCKER_HOST=unix:///var/run/docker.sock

# Frontend port
FRONTEND_PORT=3003

# Build settings
NODE_ENV=production
RUST_BACKTRACE=1
EOF
        echo -e "${GREEN}Created $ENV_FILE${NC}"
    fi

    # Create Dockerfile if not exists
    if [ ! -f "Dockerfile" ]; then
        echo "Creating Dockerfile..."
        cp "$SCRIPT_DIR/Dockerfile" ./Dockerfile
        echo -e "${GREEN}Created Dockerfile${NC}"
    fi

    echo
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo -e "You can now run: ${CYAN}tb dev${NC} to start development"
}

cmd_clean() {
    echo -e "${YELLOW}Cleaning build artifacts...${NC}"

    # Remove build directories
    rm -rf dist/ build/ target/
    rm -rf node_modules/ .npm/ .pnpm-store/
    rm -rf __pycache__/ .pytest_cache/ .coverage htmlcov/

    # Clean Docker
    if command -v docker &> /dev/null; then
        echo "Cleaning Docker resources..."
        docker system prune -f
    fi

    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Quick build commands
cmd_win() {
    echo -e "${GREEN}Building for Windows...${NC}"
    run_tauri_builder --mode build --platforms windows --arch x64 --optimize "$@"
}

cmd_mac() {
    echo -e "${GREEN}Building for macOS...${NC}"
    run_tauri_builder --mode build --platforms macos --arch x64,arm64 --optimize "$@"
}

cmd_linux() {
    echo -e "${GREEN}Building for Linux...${NC}"
    run_tauri_builder --mode build --platforms linux --arch x64 --optimize "$@"
}

cmd_all() {
    echo -e "${GREEN}Building for all platforms...${NC}"
    run_tauri_builder --mode build --platforms windows,macos,linux --arch x64,arm64 --optimize "$@"
}

cmd_arm() {
    echo -e "${GREEN}Building for ARM64...${NC}"
    run_tauri_builder --mode build --platforms linux --arch arm64 --optimize "$@"
}

# Interactive mode
interactive_mode() {
    print_header

    PS3="Select an option: "
    options=(
        "Start Development Server"
        "Build for All Platforms"
        "Build for Windows"
        "Build for macOS"
        "Build for Linux"
        "Run Tests"
        "Setup Project"
        "Clean Artifacts"
        "Docker Build"
        "Exit"
    )

    select opt in "${options[@]}"; do
        case $REPLY in
            1) cmd_dev; break ;;
            2) cmd_all; break ;;
            3) cmd_win; break ;;
            4) cmd_mac; break ;;
            5) cmd_linux; break ;;
            6) cmd_test; break ;;
            7) cmd_setup; break ;;
            8) cmd_clean; break ;;
            9) cmd_docker build; break ;;
            10) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid option. Please try again." ;;
        esac
    done
}

# Main execution
main() {
    # Check if running without arguments
    if [ $# -eq 0 ]; then
        interactive_mode
        exit 0
    fi

    # Parse command
    COMMAND="${1:-help}"
    shift || true

    # Handle commands
    case "$COMMAND" in
        dev)
            check_requirements
            cmd_dev "$@"
            ;;
        build)
            check_requirements
            cmd_build "$@"
            ;;
        publish)
            check_requirements
            cmd_publish "$@"
            ;;
        test)
            cmd_test "$@"
            ;;
        docker)
            cmd_docker "$@"
            ;;
        setup)
            cmd_setup
            ;;
        clean)
            cmd_clean
            ;;
        win|windows)
            check_requirements
            cmd_win "$@"
            ;;
        mac|macos)
            check_requirements
            cmd_mac "$@"
            ;;
        linux)
            check_requirements
            cmd_linux "$@"
            ;;
        all)
            check_requirements
            cmd_all "$@"
            ;;
        arm|arm64)
            check_requirements
            cmd_arm "$@"
            ;;
        help|--help|-h)
            print_help
            ;;
        version|--version|-v)
            echo "Tauri Builder CLI v$VERSION"
            ;;
        *)
            echo -e "${RED}Unknown command: $COMMAND${NC}"
            echo "Run 'tb help' for usage information"
            exit 1
            ;;
    esac
}

# Trap errors
trap 'echo -e "${RED}Error occurred at line $LINENO${NC}"' ERR

# Run main function
main "$@"