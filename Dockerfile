# Multi-stage Dockerfile for Tauri multi-platform builds
# Supports: Windows, macOS, Linux (x64 and ARM64)

ARG RUST_VERSION=1.75
ARG NODE_VERSION=20
ARG PLATFORM=linux
ARG ARCH=x64

# Base stage with common dependencies
FROM rust:${RUST_VERSION} AS base

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs

# Install pnpm and yarn globally
RUN npm install -g pnpm yarn

# Install common build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    pkg-config \
    libssl-dev \
    jq \
    zip \
    unzip

# Linux builder stage
FROM base AS linux-builder

# Install Linux-specific dependencies
RUN apt-get update && apt-get install -y \
    libwebkit2gtk-4.0-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev \
    patchelf \
    squashfs-tools \
    zsync \
    desktop-file-utils \
    libfuse2

# Install additional tools for Linux packaging
RUN apt-get install -y \
    rpm \
    fakeroot \
    dpkg-dev

# Windows cross-compilation stage
FROM base AS windows-builder

# Install Windows cross-compilation tools
RUN apt-get update && apt-get install -y \
    gcc-mingw-w64 \
    g++-mingw-w64 \
    wine64 \
    wine32 \
    wine \
    mono-devel \
    osslsigncode \
    nsis

# Add Windows Rust targets
RUN rustup target add x86_64-pc-windows-gnu && \
    rustup target add i686-pc-windows-gnu && \
    rustup target add aarch64-pc-windows-msvc

# Configure cargo for Windows cross-compilation
RUN mkdir -p ~/.cargo && \
    echo '[target.x86_64-pc-windows-gnu]' >> ~/.cargo/config.toml && \
    echo 'linker = "x86_64-w64-mingw32-gcc"' >> ~/.cargo/config.toml && \
    echo '[target.i686-pc-windows-gnu]' >> ~/.cargo/config.toml && \
    echo 'linker = "i686-w64-mingw32-gcc"' >> ~/.cargo/config.toml

# macOS cross-compilation stage (experimental)
FROM base AS macos-builder

# Install macOS cross-compilation tools (osxcross)
RUN apt-get update && apt-get install -y \
    clang \
    cmake \
    libxml2-dev \
    llvm-dev \
    uuid-dev \
    libssl-dev

# Download and setup osxcross (requires macOS SDK)
# Note: You need to provide macOS SDK separately due to licensing
WORKDIR /opt
RUN git clone https://github.com/tpoechtrager/osxcross && \
    cd osxcross && \
    wget -nc https://github.com/phracker/MacOSX-SDKs/releases/download/11.3/MacOSX11.3.sdk.tar.xz || true

# Build osxcross (only if SDK is available)
RUN cd /opt/osxcross && \
    if [ -f MacOSX11.3.sdk.tar.xz ]; then \
        mv MacOSX11.3.sdk.tar.xz tarballs/ && \
        UNATTENDED=yes ./build.sh; \
    fi

# Add macOS Rust targets
RUN rustup target add x86_64-apple-darwin && \
    rustup target add aarch64-apple-darwin

# ARM64 builder stage
FROM base AS arm64-builder

# Install ARM64 cross-compilation tools
RUN apt-get update && apt-get install -y \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    libc6-dev-arm64-cross

# Add ARM64 Rust targets
RUN rustup target add aarch64-unknown-linux-gnu && \
    rustup target add aarch64-unknown-linux-musl

# Configure cargo for ARM64 cross-compilation
RUN mkdir -p ~/.cargo && \
    echo '[target.aarch64-unknown-linux-gnu]' >> ~/.cargo/config.toml && \
    echo 'linker = "aarch64-linux-gnu-gcc"' >> ~/.cargo/config.toml

# Final builder stage - combines all platforms
FROM ${PLATFORM}-builder AS final-builder

# Install Tauri CLI
RUN cargo install tauri-cli --version ^1.5

# Install additional Rust tools
RUN cargo install cargo-edit cargo-watch

# Setup working directory
WORKDIR /app

# Copy entrypoint script
COPY <<'EOF' /entrypoint.sh
#!/bin/bash
set -e

# Parse arguments
PLATFORM=${PLATFORM:-linux}
ARCH=${ARCH:-x64}
FRONTEND_PORT=${FRONTEND_PORT:-3003}
MODE=${MODE:-build}

echo "🚀 Tauri Builder"
echo "Platform: $PLATFORM"
echo "Architecture: $ARCH"
echo "Mode: $MODE"

# Function to get Rust target
get_rust_target() {
    case "$PLATFORM-$ARCH" in
        linux-x64) echo "x86_64-unknown-linux-gnu" ;;
        linux-arm64) echo "aarch64-unknown-linux-gnu" ;;
        windows-x64) echo "x86_64-pc-windows-gnu" ;;
        windows-arm64) echo "aarch64-pc-windows-msvc" ;;
        macos-x64) echo "x86_64-apple-darwin" ;;
        macos-arm64) echo "aarch64-apple-darwin" ;;
        *) echo "unknown" ;;
    esac
}

# Function to build the application
build_app() {
    local rust_target=$(get_rust_target)

    if [ "$rust_target" = "unknown" ]; then
        echo "❌ Unknown platform/architecture combination: $PLATFORM-$ARCH"
        exit 1
    fi

    echo "📦 Installing dependencies..."
    if [ -f "pnpm-lock.yaml" ]; then
        pnpm install
    elif [ -f "yarn.lock" ]; then
        yarn install
    elif [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi

    echo "🔨 Building frontend..."
    npm run build

    echo "🦀 Building Tauri application for $rust_target..."
    cd src-tauri

    # Add Rust target if not already added
    rustup target add $rust_target || true

    # Build based on mode
    if [ "$MODE" = "dev" ]; then
        cargo tauri dev
    else
        cargo tauri build --target $rust_target
    fi
}

# Function for development mode
run_dev() {
    echo "🔧 Starting development server..."

    # Install dependencies
    if [ -f "pnpm-lock.yaml" ]; then
        pnpm install
    elif [ -f "yarn.lock" ]; then
        yarn install
    else
        npm install
    fi

    # Start Tauri dev server
    npm run tauri dev -- --port $FRONTEND_PORT
}

# Main execution
case "$MODE" in
    dev)
        run_dev
        ;;
    build|publish)
        build_app
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        exit 1
        ;;
esac
EOF

RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["build"]

# Metadata
LABEL maintainer="Tauri Builder"
LABEL description="Multi-platform Tauri application builder"
LABEL version="1.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD cargo --version && node --version && tauri --version || exit 1