# File: backend/doc_engine.py
from typing import Dict, Any

class DocEngine:
    """
    Generates user-friendly documentation, deployment guides, and automation scripts.
    Focused on non-technical users.
    """
    
    def generate_readme(self, project_name: str, description: str) -> str:
        return f"""# 🚀 {project_name}

{description}

---

## 🛠️ Instant Start (No-Code Friendly)
We have provided an automated setup script to get you running in minutes.

1. **Open your terminal** (PowerShell on Windows, Terminal on Mac).
2. **Run the installer**:
   ```bash
   bash install.sh
   ```

## 📦 What's Included?
- **Frontend**: Next.js (Modern Web Interface)
- **Backend**: FastAPI (High-performance Logic)
- **Database**: Supabase SQL (Secure Persistence)
- **Container**: Docker (One-click deployment)

## 📖 Deployment Guide
Check `DEPLOY.md` for detailed instructions on hosting this app on the cloud.
"""

    def generate_deploy_guide(self) -> str:
        return """# 🛰️ Deployment Guide

## Option 1: Local (Docker)
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Run `docker-compose up --build`.
3. Your app is live at `http://localhost:3000`.

## Option 2: Cloud (Vercel + Supabase)
1. **Database**: Create a project on [Supabase.com](https://supabase.com).
2. **Frontend**: Push this code to GitHub and connect it to [Vercel](https://vercel.com).
3. **Environment Variables**: Add your `SUPABASE_URL` and `SUPABASE_ANON_KEY` to Vercel.
"""

    def generate_docker_compose(self, project_name: str) -> str:
        return f"""version: '3.8'
services:
  database:
    image: postgres:15
    environment:
      - POSTGRES_DB={project_name}_db
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
    ports:
      - "5432:5432"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - database
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PROJECT_NAME={project_name}
      - DATABASE_URL=postgresql://admin:secret@database:5432/{project_name}_db
    depends_on:
      - database
"""

    def generate_install_script(self) -> str:
        return """#!/bin/bash
echo "🚀 Starting AIOrch Automated Installer..."
echo "📦 Checking dependencies..."
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Error: Docker is not installed. Please install it first."
  exit 1
fi
echo "✅ Docker found."
echo "🏗️ Building the application swarm..."
docker-compose up --build -d
echo "✨ Success! Your app is running at http://localhost:3000"
"""

doc_engine = DocEngine()
