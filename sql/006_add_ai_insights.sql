-- Add AI insights column to existing skill_profiles table
ALTER TABLE skill_profiles
  ADD COLUMN IF NOT EXISTS ai_insights jsonb;