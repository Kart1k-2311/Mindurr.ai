-- 008_learning_roadmaps.sql
-- Table to store AI-generated personalized learning roadmaps

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

-- Enable Row Level Security
ALTER TABLE public.learning_roadmaps ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any to prevent conflicts
DROP POLICY IF EXISTS "Users can view own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can insert own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can update own learning roadmap" ON public.learning_roadmaps;
DROP POLICY IF EXISTS "Users can delete own learning roadmap" ON public.learning_roadmaps;

-- RLS Policies for authenticated users
CREATE POLICY "Users can view own learning roadmap"
    ON public.learning_roadmaps FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own learning roadmap"
    ON public.learning_roadmaps FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own learning roadmap"
    ON public.learning_roadmaps FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own learning roadmap"
    ON public.learning_roadmaps FOR DELETE
    USING (auth.uid() = user_id);
