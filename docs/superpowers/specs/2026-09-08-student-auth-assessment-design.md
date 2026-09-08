# Design Spec: Student Account Creation + Assessment System

## Overview

Two interconnected features for Mindurr.ai:
1. **Student Account Creation** — Supabase Auth client-side signup/login
2. **Assessment Wizard** — Single-page 4-step flow to build a skill profile

---

## Part 1: Student Account Creation

### Auth Approach
- Supabase Auth via JS SDK (client-side)
- No backend routes needed for auth
- Existing `Student_Login_code.html` has the UI — needs real Supabase credentials wired in

### Flow
1. User enters email + password on `Student_Login_code.html`
2. Supabase `signUp()` creates user in `auth.users`
3. On signup → auto-create row in `profiles` table via a Supabase database trigger
4. On login → check if user has a `skill_profiles` row
   - No → redirect to `assessment.html`
   - Yes → redirect to student dashboard (future)

### Supabase Tables

**`profiles`**
```sql
CREATE TABLE profiles (
  id uuid REFERENCES auth.users PRIMARY KEY,
  full_name text,
  email text,
  created_at timestamp DEFAULT now()
);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, email)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### Files to Modify
- `frontend/Student_Login_code.html` — replace `YOUR_SUPABASE_URL` / `YOUR_SUPABASE_ANON_KEY` with real values, add redirect logic after login

---

## Part 2: Assessment Wizard

### Architecture
Single HTML file (`assessment.html`) with 4 wizard steps, styled with Solaris Design System.

### Step 1 — Select Industry/Goal
User picks one industry from cards:
- Frontend, Backend, DevOps, Data Science, Mobile, Full-Stack

### Step 2 — Select Languages
Based on chosen industry, show relevant languages. User picks 1+.

### Step 3 — Select Technologies
Based on chosen languages + industry, show frameworks/tools. User picks 1+.

### Step 4 — Assessment
25-30 questions drawn from a static question bank, filtered to chosen technologies. Multiple-choice format.

### Industry → Language → Technology Mapping (Hardcoded JS)
```js
const INDUSTRIES = {
  frontend: {
    label: 'Frontend',
    languages: ['JavaScript', 'TypeScript', 'HTML/CSS'],
    technologies: {
      JavaScript: ['React', 'Vue.js', 'Angular', 'Next.js', 'Svelte'],
      TypeScript: ['React', 'Angular', 'Next.js'],
      'HTML/CSS': ['Tailwind CSS', 'SASS/SCSS', 'Bootstrap']
    }
  },
  backend: {
    label: 'Backend',
    languages: ['Python', 'JavaScript', 'Java', 'Go', 'Rust'],
    technologies: {
      Python: ['Django', 'FastAPI', 'Flask', 'Celery'],
      JavaScript: ['Express.js', 'NestJS', 'Fastify'],
      Java: ['Spring Boot', 'Micronaut'],
      Go: ['Gin', 'Echo', 'Fiber'],
      Rust: ['Actix Web', 'Axum']
    }
  },
  devops: {
    label: 'DevOps',
    languages: ['Python', 'Bash', 'Go'],
    technologies: {
      Python: ['Docker', 'Kubernetes', 'Terraform', 'Ansible'],
      Bash: ['Docker', 'Linux Administration', 'CI/CD'],
      Go: ['Docker', 'Kubernetes', 'Terraform']
    }
  },
  data_science: {
    label: 'Data Science',
    languages: ['Python', 'R', 'SQL'],
    technologies: {
      Python: ['Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch'],
      R: ['ggplot2', 'dplyr', 'Shiny'],
      SQL: ['PostgreSQL', 'MySQL', 'BigQuery']
    }
  },
  mobile: {
    label: 'Mobile',
    languages: ['JavaScript', 'Dart', 'Kotlin', 'Swift'],
    technologies: {
      JavaScript: ['React Native', 'Expo'],
      Dart: ['Flutter'],
      Kotlin: ['Android Jetpack Compose'],
      Swift: ['SwiftUI', 'UIKit']
    }
  },
  fullstack: {
    label: 'Full-Stack',
    languages: ['JavaScript', 'TypeScript', 'Python'],
    technologies: {
      JavaScript: ['React', 'Node.js', 'Express.js', 'Next.js'],
      TypeScript: ['React', 'Next.js', 'NestJS'],
      Python: ['Django', 'FastAPI', 'Flask']
    }
  }
};
```

### Question Bank Structure
```js
const QUESTIONS = {
  'React': [
    {
      q: 'What hook is used for side effects in React?',
      options: ['useState', 'useEffect', 'useRef', 'useMemo'],
      answer: 1
    },
    // ... questions per technology
  ],
  'Python': [ ... ],
  // etc.
};
```

### Scoring Logic
- Each question: 1 point for correct answer
- Per-technology score: `(correct / total) * 100`
- Total profile score: average of all per-technology scores
- Score breakdown stored as JSONB in Supabase

### Supabase Table

**`skill_profiles`**
```sql
CREATE TABLE skill_profiles (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users NOT NULL,
  industry text NOT NULL,
  languages text[] NOT NULL,
  technologies text[] NOT NULL,
  scores jsonb NOT NULL DEFAULT '{}',
  total_score numeric NOT NULL DEFAULT 0,
  completed_at timestamp DEFAULT now(),
  UNIQUE(user_id)
);
```

### User Flow
1. User logs in → redirected to `assessment.html`
2. Step 1: picks industry → "Next"
3. Step 2: picks languages → "Next"
4. Step 3: picks technologies → "Start Assessment"
5. Step 4: answers 25-30 questions → "Submit"
6. Results page: shows per-technology scores + total score
7. Data saved to `skill_profiles` in Supabase
8. Redirect to student dashboard (future)

### Files to Create
- `frontend/assessment.html` — the full wizard page

### Files to Modify
- `frontend/Student_Login_code.html` — add redirect to assessment after login

---

## Error Handling
- Supabase auth errors → displayed inline on login form
- Assessment submit failure → toast notification, retry
- Empty selections → validation before advancing steps
- Already assessed → redirect to dashboard, not assessment

## Future Considerations
- Timer for assessment
- Retake assessment
- Recruiter view of skill profiles
- Admin panel to manage question bank
