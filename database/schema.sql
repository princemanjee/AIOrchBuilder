-- AIOrchBuilder: Core Database Schema (RBAC & Audit)
-- Designed for Supabase / PostgreSQL

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. ENUMS
CREATE TYPE user_role AS ENUM ('ADMIN', 'DEVELOPER', 'VIEWER');
CREATE TYPE task_status AS ENUM ('PENDING', 'IN_PROGRESS', 'FINISHED', 'BLOCKED');
CREATE TYPE task_phase AS ENUM ('01_ANALYSIS', '02_BLUEPRINT', '03_AGENT_SPAwn', '04_BUILD', '05_VALIDATION', '06_REFINEMENT');

-- 3. TABLES

-- Profiles (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  role user_role DEFAULT 'DEVELOPER',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects
CREATE TABLE IF NOT EXISTS public.projects (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  satellite_url TEXT,
  satellite_key TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  owner_id UUID REFERENCES public.profiles(id)
);

-- Tasks (The core of the SDLC tracker)
CREATE TABLE IF NOT EXISTS public.tasks (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  phase task_phase NOT NULL,
  status task_status DEFAULT 'PENDING',
  agent_assigned TEXT[], -- Array of agent names (e.g., ['AGENT_UI', 'ORCHESTRATOR'])
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Audit Logs (Real-time telemetry)
CREATE TABLE IF NOT EXISTS public.agent_audit_logs (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT DEFAULT 'INFO', -- INFO, WARNING, ERROR, SUCCESS
  metadata JSONB, -- For raw output or step IDs
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. ROW LEVEL SECURITY (RLS) policies

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_audit_logs ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can view all profiles but only update their own
CREATE POLICY "Public profiles are viewable by everyone." ON public.profiles
  FOR SELECT USING (true);

CREATE POLICY "Users can update own profile." ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Projects & Tasks: Only admins/owners can delete/manage; all authenticated users can view
CREATE POLICY "Projects viewable by authenticated users" ON public.projects
  FOR SELECT TO authenticated USING (true);

CREATE POLICY "Admins have full access to projects" ON public.projects
  FOR ALL TO authenticated USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'ADMIN')
  );

-- 5. TRIGGERS & FUNCTIONS

-- Automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, role)
  VALUES (new.id, new.raw_user_meta_data->>'full_name', 'ADMIN'); -- First user is always ADMIN for single-user power mode
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
