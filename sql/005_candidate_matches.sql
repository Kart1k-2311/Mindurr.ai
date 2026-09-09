CREATE TABLE IF NOT EXISTS candidate_matches (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  job_id uuid REFERENCES job_descriptions ON DELETE CASCADE NOT NULL,
  user_id uuid REFERENCES auth.users NOT NULL,
  match_score numeric NOT NULL,
  match_reasoning jsonb,
  created_at timestamp DEFAULT now(),
  UNIQUE(job_id, user_id)
);

-- RLS: recruiters can only see matches for their own jobs
ALTER TABLE candidate_matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Recruiters can view own matches"
  ON candidate_matches FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM job_descriptions
      WHERE job_descriptions.id = candidate_matches.job_id
        AND job_descriptions.recruiter_id = auth.uid()
    )
  );