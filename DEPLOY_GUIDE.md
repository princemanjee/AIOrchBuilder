# File: DEPLOY_GUIDE.md

# 🚀 Cloud Deployment Guide: AIOrch Orchestrator

This guide outlines the steps to deploy the AIOrch Orchestrator on a Linux VPS (Ubuntu 22.04 LTS recommended).

## 1. Prerequisites

- A VPS with at least 4GB RAM and 2 CPUs.
- A domain name (optional but recommended for SSL).
- Docker and Docker Compose installed.

## 2. Environment Setup

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 3. Deployment via Docker Compose

Use the following `docker-compose.yml` to spin up the entire stack:

```yaml
version: "3.8"
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8001:8001"
    env_file: .env
    restart: always

  frontend:
    build:
      context: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8001
    depends_on:
      - backend
    restart: always
```

## 4. Reverse Proxy (Nginx + SSL)

We recommend using Nginx to handle SSL and proxy requests.

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
    }
}
```

## 5. Security Best Practices

1. **Firewall**: Ensure only ports 80 and 443 are open to the public.
2. **Secrets**: Never commit your `.env` file to version control.
3. **Database**: The Orchestrator uses Supabase as the Hub. Ensure your RLS policies are strictly enforced.

## 6. Ollama Integration (Remote)

To connect to a remote Ollama server:

1. Ensure the Ollama server is accessible via IP/URL.
2. Set the `OLLAMA_HOST` transparency in the AIOrch Admin Dashboard to your remote IP.
3. High-latency connections may require adjusting the "Agent Speed" to 'S' to allow for longer inference times.
