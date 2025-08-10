# 🐳➡️🦀 Docker-to-Tauri Integration Guide

## Overview

TauriDock allows you to run **any Docker container** as a **native desktop application** using Tauri. This creates a seamless bridge between containerized web applications and native desktop experiences.

## 🎯 Use Cases

- **Web Applications**: React, Vue, Angular apps as desktop apps
- **Development Tools**: VS Code Server, Jupyter, Grafana  
- **Database Management**: phpMyAdmin, Adminer, MongoDB Compass
- **Monitoring Dashboards**: Prometheus, Kibana, Portainer
- **CMS Systems**: WordPress, Ghost, Strapi
- **API Services**: Any REST API with web interface

## 🚀 Quick Start

### Method 1: Universal Wrapper (Recommended)

```bash
# Run any Docker container as Tauri app
./docker-tauri-wrapper.sh <docker-image> <host-port> <container-port>

# Examples:
./docker-tauri-wrapper.sh nginx:alpine 8080 80
./docker-tauri-wrapper.sh grafana/grafana 3001 3000  
./docker-tauri-wrapper.sh jupyter/scipy-notebook 8888 8888
```

### Method 2: Manual Configuration

1. **Update `src-tauri/tauri.conf.json`:**
```json
{
  "build": {
    "beforeDevCommand": "docker run -d -p 8080:80 nginx:alpine",
    "devUrl": "http://localhost:8080"
  }
}
```

2. **Run Tauri:**
```bash
cd src-tauri && cargo tauri dev
```

## 📁 Project Structure

```
tauridock/
├── app/                          # Frontend files (fallback/config UI)
│   ├── index.html               # Main HTML
│   ├── index.css                # Styling  
│   └── index.js                 # Tauri API interactions
├── src-tauri/                   # Tauri backend
│   ├── src/main.rs              # Rust backend with Docker integration
│   ├── Cargo.toml               # Dependencies
│   └── tauri.conf.json          # Dynamic Docker configuration
├── docker-tauri-wrapper.sh      # Universal Docker launcher
└── docs/
    └── DOCKER-TO-TAURI.md       # This documentation
```

## 🔧 Configuration Options

### Tauri Configuration (`tauri.conf.json`)

```json
{
  "build": {
    "beforeDevCommand": "docker run -d -p <PORT>:<CONTAINER_PORT> <IMAGE>",
    "devUrl": "http://localhost:<PORT>",
    "frontendDist": "../app"
  },
  "app": {
    "windows": [{
      "title": "My Docker App",
      "width": 1200,
      "height": 800,
      "resizable": true
    }]
  }
}
```

### Docker Configuration Examples

| Service | Command | Port Mapping |
|---------|---------|--------------|
| **Nginx** | `docker run -d -p 8080:80 nginx:alpine` | 8080→80 |
| **Node.js** | `docker run -d -p 3000:3000 node:18-alpine` | 3000→3000 |
| **Python Flask** | `docker run -d -p 5000:5000 python:3.9` | 5000→5000 |
| **Grafana** | `docker run -d -p 3001:3000 grafana/grafana` | 3001→3000 |
| **Jupyter** | `docker run -d -p 8888:8888 jupyter/base-notebook` | 8888→8888 |

## 🎮 Advanced Features

### 1. **Dynamic Port Management**
The wrapper automatically handles port conflicts and cleanup.

### 2. **Container Lifecycle**
- Starts containers before Tauri launches
- Stops containers when Tauri exits
- Health checks before launching

### 3. **Custom Window Configuration**
Each Docker service can have custom window settings:

```json
{
  "app": {
    "windows": [{
      "title": "Grafana Dashboard",
      "width": 1400,
      "height": 900,
      "minWidth": 800,
      "minHeight": 600,
      "resizable": true,
      "fullscreen": false
    }]
  }
}
```

### 4. **Environment Variables**
Pass environment variables to containers:

```bash
# In docker-tauri-wrapper.sh
docker run -d -p 8080:80 -e NODE_ENV=production my-app:latest
```

## 🔒 Security Considerations

- **Network Isolation**: Containers run in isolated networks
- **Port Binding**: Only bind to localhost (127.0.0.1)
- **Resource Limits**: Set memory/CPU limits for containers
- **Image Security**: Use official, trusted Docker images

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :8080
# Stop conflicting containers
docker ps | grep :8080
```

2. **Container Not Starting**
```bash
# Check container logs  
docker logs <container-id>
```

3. **Tauri Build Fails**
```bash
# Install system dependencies
sudo apt install libwebkit2gtk-4.0-dev libgtk-3-dev
```

### Debug Mode

Enable debug mode in the wrapper:
```bash
DEBUG=1 ./docker-tauri-wrapper.sh nginx:alpine 8080 80
```

## 📖 Examples

### Example 1: Nginx Static Site
```bash
./docker-tauri-wrapper.sh nginx:alpine 8080 80
```

### Example 2: Node.js Application  
```bash
./docker-tauri-wrapper.sh node:18-alpine 3000 3000
```

### Example 3: Custom Application
```bash
# Build your app first
docker build -t my-web-app .

# Run as Tauri app
./docker-tauri-wrapper.sh my-web-app:latest 8080 80
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b docker-integration`
3. Make changes and test
4. Submit pull request

## 📜 License

This project is licensed under MIT License - see LICENSE file for details.

---

**Need help?** Check the main README or open an issue on GitHub.
