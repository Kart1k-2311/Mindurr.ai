CREATE TABLE IF NOT EXISTS recruiter_profiles (
  id uuid REFERENCES auth.users PRIMARY KEY,
  company_name text,
  company_website text,
  position text,
  created_at timestamp DEFAULT now()
);

-- RLS: recruiters can view/update their own profile
ALTER TABLE recruiter_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Recruiters can view own profile"
  ON recruiter_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Recruiters can update own profile"
  ON recruiter_profiles FOR UPDATE
  USING (auth.uid() = id);