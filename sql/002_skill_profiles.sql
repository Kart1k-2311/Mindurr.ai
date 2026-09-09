CREATE TABLE IF NOT EXISTS skill_profiles (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users NOT NULL,
  goal text,
  industry text NOT NULL,
  languages text[] NOT NULL,
  technologies text[] NOT NULL,
  scores jsonb NOT NULL DEFAULT '{}',
  total_score numeric NOT NULL DEFAULT 0,
  ai_insights jsonb,
  completed_at timestamp DEFAULT now(),
  UNIQUE(user_id)
);

ALTER TABLE skill_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own skill profile"
  ON skill_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own skill profile"
  ON skill_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own skill profile"
  ON skill_profiles FOR UPDATE
  USING (auth.uid() = user_id);