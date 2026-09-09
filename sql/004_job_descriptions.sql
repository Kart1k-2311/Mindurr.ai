CREATE TABLE IF NOT EXISTS job_descriptions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  recruiter_id uuid REFERENCES auth.users NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  required_skills text[] DEFAULT '{}',
  experience_level text DEFAULT 'entry',
  created_at timestamp DEFAULT now()
);

-- RLS: recruiters can manage their own job postings.
-- Anon/authenticated users cannot read other recruiters' job descriptions.
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Recruiters can view own jobs"
  ON job_descriptions FOR SELECT
  USING (auth.uid() = recruiter_id);

CREATE POLICY "Recruiters can insert own jobs"
  ON job_descriptions FOR INSERT
  WITH CHECK (auth.uid() = recruiter_id);

CREATE POLICY "Recruiters can update own jobs"
  ON job_descriptions FOR UPDATE
  USING (auth.uid() = recruiter_id);