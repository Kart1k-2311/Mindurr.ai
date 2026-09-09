-- ==============================================================================
-- 009_profile_and_roadmap_migration.sql
-- Mindurr.ai: Full Skill Profile & Roadmap Schema Migration for Supabase
-- Run this in your Supabase Dashboard SQL Editor (SQL Editor -> New Query -> Run)
-- ==============================================================================

-- 1. Ensure goal column exists on skill_profiles
ALTER TABLE IF EXISTS public.skill_profiles 
  ADD COLUMN IF NOT EXISTS goal text;

-- 2. Ensure languages and technologies have defaults if empty
ALTER TABLE IF EXISTS public.skill_profiles 
  ALTER COLUMN languages SET DEFAULT '{}',
  ALTER COLUMN technologies SET DEFAULT '{}',
  ALTER COLUMN scores SET DEFAULT '{}'::jsonb;

-- 3. Ensure user_id unique constraint exists for upsert ON CONFLICT (user_id)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'skill_profiles_user_id_key'
  ) THEN
    ALTER TABLE public.skill_profiles ADD CONSTRAINT skill_profiles_user_id_key UNIQUE (user_id);
  END IF;
EXCEPTION
  WHEN others THEN NULL;
END $$;

-- 4. Enable Row Level Security and establish policies on skill_profiles
ALTER TABLE public.skill_profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own skill profile" ON public.skill_profiles;
DROP POLICY IF EXISTS "Users can insert own skill profile" ON public.skill_profiles;
DROP POLICY IF EXISTS "Users can update own skill profile" ON public.skill_profiles;
DROP POLICY IF EXISTS "Users can delete own skill profile" ON public.skill_profiles;

CREATE POLICY "Users can view own skill profile"
  ON public.skill_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own skill profile"
  ON public.skill_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own skill profile"
  ON public.skill_profiles FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own skill profile"
  ON public.skill_profiles FOR DELETE
  USING (auth.uid() = user_id);

-- 5. Create learning_roadmaps table if not exists
CREATE TABLE IF NOT EXISTS public.learning_roadmaps (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    skill_profile_id uuid REFERENCES public.skill_profiles(id) ON DELETE SET NULL,
    target_role text NOT NULL,
    target_industry text NOT NULL,
    overall_gap_summary text,
    total_estimated_weeks integer DEFAULT 12,
    status text DEFAULT 'in_progress',
    steps jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- 6. Enable Row Level Security and establish policies on learning_roadmaps
ALTER TABLE public.learning_roadmaps ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can insert own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can update own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can delete own learning roadmap" ON public.learning_roadmaps;

CREATE POLICY "Users can view own learning roadmap"
    ON public.learning_roadmaps FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own learning roadmap"
    ON public.learning_roadmaps FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own learning roadmap"
    ON public.learning_roadmaps FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own learning roadmap"
    ON public.learning_roadmaps FOR DELETE
    USING (auth.uid() = user_id);

-- 7. Notify PostgREST to immediately refresh its schema cache
NOTIFY pgrst, 'reload schema';
