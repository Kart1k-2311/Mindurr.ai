-- ==============================================================================
-- Migration: 010_recruiter_profiles.sql
-- Description: Recruiter profiles schema with verified_status and strict RLS policies.
-- ==============================================================================

-- 1. Create table if not exists
CREATE TABLE IF NOT EXISTS public.recruiter_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  company_name TEXT,
  verified_status BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Add missing columns idempotently if table already existed
ALTER TABLE public.recruiter_profiles ADD COLUMN IF NOT EXISTS verified_status BOOLEAN DEFAULT false;
ALTER TABLE public.recruiter_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.recruiter_profiles ENABLE ROW LEVEL SECURITY;

-- 4. Drop old policies to ensure clean idempotent re-runs
DROP POLICY IF EXISTS "Recruiters can view own profile" ON public.recruiter_profiles;
DROP POLICY IF EXISTS "Recruiters can insert own profile" ON public.recruiter_profiles;
DROP POLICY IF EXISTS "Recruiters can update own profile" ON public.recruiter_profiles;
DROP POLICY IF EXISTS "Recruiters can delete own profile" ON public.recruiter_profiles;

-- 5. Strict RLS Policies for authenticated users
CREATE POLICY "Recruiters can view own profile"
  ON public.recruiter_profiles FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Recruiters can insert own profile"
  ON public.recruiter_profiles FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Recruiters can update own profile"
  ON public.recruiter_profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Recruiters can delete own profile"
  ON public.recruiter_profiles FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- 6. Trigger for automatic updated_at timestamp updates
CREATE OR REPLACE FUNCTION update_recruiter_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_recruiter_profiles_updated_at ON public.recruiter_profiles;
CREATE TRIGGER trg_recruiter_profiles_updated_at
  BEFORE UPDATE ON public.recruiter_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_recruiter_profile_timestamp();
