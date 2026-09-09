-- Add goal column to skill_profiles (selected during assessment)
ALTER TABLE skill_profiles ADD COLUMN IF NOT EXISTS goal text;