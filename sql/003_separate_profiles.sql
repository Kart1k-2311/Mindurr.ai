-- Drop the shared profiles table
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user();
DROP TABLE IF EXISTS profiles;

-- Student profiles table
CREATE TABLE IF NOT EXISTS student_profiles (
  id uuid REFERENCES auth.users PRIMARY KEY,
  full_name text,
  email text,
  created_at timestamp DEFAULT now()
);

ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own profile"
  ON student_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Students can insert own profile"
  ON student_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Students can update own profile"
  ON student_profiles FOR UPDATE
  USING (auth.uid() = id);

-- Recruiter profiles table
CREATE TABLE IF NOT EXISTS recruiter_profiles (
  id uuid REFERENCES auth.users PRIMARY KEY,
  full_name text,
  email text,
  company text,
  created_at timestamp DEFAULT now()
);

ALTER TABLE recruiter_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Recruiters can view own profile"
  ON recruiter_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Recruiters can insert own profile"
  ON recruiter_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Recruiters can update own profile"
  ON recruiter_profiles FOR UPDATE
  USING (auth.uid() = id);

-- Allow recruiters to view student profiles (for hiring)
CREATE POLICY "Recruiters can view all student profiles"
  ON student_profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM recruiter_profiles WHERE id = auth.uid()
    )
  );

-- Allow recruiters to view all skill profiles (for hiring)
CREATE POLICY "Recruiters can view all skill profiles"
  ON skill_profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM recruiter_profiles WHERE id = auth.uid()
    )
  );

-- Trigger function: create appropriate profile based on role
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
DECLARE
  user_role text;
BEGIN
  user_role := COALESCE(NEW.raw_user_meta_data->>'role', 'student');

  IF user_role = 'recruiter' THEN
    INSERT INTO public.recruiter_profiles (id, full_name, email)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.email);
  ELSE
    INSERT INTO public.student_profiles (id, full_name, email)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.email);
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
