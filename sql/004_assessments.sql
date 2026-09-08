-- Assessment attempts are written by the FastAPI service role only.
-- The answer key stays in this table and is never returned by the API.
CREATE TABLE IF NOT EXISTS public.assessments (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  industry text NOT NULL,
  languages text[] NOT NULL,
  technologies text[] NOT NULL,
  questions jsonb NOT NULL DEFAULT '[]'::jsonb,
  submitted_answers jsonb NOT NULL DEFAULT '[]'::jsonb,
  status text NOT NULL DEFAULT 'generating',
  score numeric(5, 2),
  result jsonb,
  started_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  submitted_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  CONSTRAINT assessments_status_check CHECK (status IN ('generating', 'in_progress', 'submitted', 'failed')),
  CONSTRAINT assessments_questions_array_check CHECK (jsonb_typeof(questions) = 'array'),
  CONSTRAINT assessments_answers_array_check CHECK (jsonb_typeof(submitted_answers) = 'array'),
  CONSTRAINT assessments_score_check CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);

CREATE INDEX IF NOT EXISTS assessments_user_started_idx
  ON public.assessments (user_id, started_at DESC);

ALTER TABLE public.assessments ENABLE ROW LEVEL SECURITY;

-- Assessment records contain the answer key, so browser roles must not access them directly.
REVOKE ALL ON TABLE public.assessments FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE public.assessments TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.skill_profiles TO service_role;
