# 🛰️ Deployment Guide

## Option 1: Local (Docker)
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Run `docker-compose up --build`.
3. Your app is live at `http://localhost:3000`.

## Option 2: Cloud (Vercel + Supabase)
1. **Database**: Create a project on [Supabase.com](https://supabase.com).
2. **Frontend**: Push this code to GitHub and connect it to [Vercel](https://vercel.com).
3. **Environment Variables**: Add your `SUPABASE_URL` and `SUPABASE_ANON_KEY` to Vercel.
