-- ==============================================================================
-- Supabase SQL Setup: recruiter_profiles
-- ==============================================================================

-- Create the recruiter_profiles table
CREATE TABLE IF NOT EXISTS public.recruiter_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  company_name TEXT,
  verified_status BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.recruiter_profiles ENABLE ROW LEVEL SECURITY;

-- Clean up any existing policies
DROP POLICY IF EXISTS "Recruiters can select their own profile" ON public.recruiter_profiles;
DROP POLICY IF EXISTS "Recruiters can insert their own profile" ON public.recruiter_profiles;
DROP POLICY IF EXISTS "Recruiters can update their own profile" ON public.recruiter_profiles;

-- RLS Policy: Allow users to view/select their own recruiter profile
CREATE POLICY "Recruiters can select their own profile"
  ON public.recruiter_profiles FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- RLS Policy: Allow users to create their own recruiter profile
CREATE POLICY "Recruiters can insert their own profile"
  ON public.recruiter_profiles FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- RLS Policy: Allow users to update their own recruiter profile
CREATE POLICY "Recruiters can update their own profile"
  ON public.recruiter_profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);
