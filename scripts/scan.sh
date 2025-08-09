# security/scan.sh
#!/bin/bash

# Scan Docker images
trivy image tauridock:latest

# Scan dependencies
safety check -r requirements.txt

# Scan code for vulnerabilities
bandit -r tauri_builder.py

# Check for secrets
gitleaks detect