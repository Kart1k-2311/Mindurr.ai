# Student Auth + Assessment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build student account creation via Supabase Auth and a 4-step assessment wizard that generates a skill profile.

**Architecture:** Client-side Supabase Auth for signup/login. Single-page HTML wizard for the assessment flow. Static question bank in JS. Results saved to Supabase `skill_profiles` table.

**Tech Stack:** HTML5, Tailwind CSS (CDN), Supabase JS SDK (CDN), Vanilla JS (ES6+), Supabase PostgreSQL

## Global Constraints
- Solaris Design System (cream/yellow palette, Geist + Inter fonts)
- Supabase JS SDK v2 via CDN (`https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`)
- Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- No build tools, no npm, no frameworks — plain HTML/JS files
- All Supabase credentials placeholder until user provides real values

---

## File Structure

| File | Purpose |
|------|---------|
| `frontend/assessment.html` | **CREATE** — 4-step assessment wizard |
| `frontend/Student_Login_code.html` | **MODIFY** — wire real Supabase creds, add post-login redirect |
| `sql/001_profiles.sql` | **CREATE** — profiles table + trigger |
| `sql/002_skill_profiles.sql` | **CREATE** — skill_profiles table |

---

### Task 1: Supabase SQL Schema

**Files:**
- Create: `sql/001_profiles.sql`
- Create: `sql/002_skill_profiles.sql`

**Interfaces:**
- Produces: `profiles` table, `skill_profiles` table, `handle_new_user()` trigger function

- [ ] **Step 1: Create profiles table SQL**

```sql
-- sql/001_profiles.sql
CREATE TABLE IF NOT EXISTS profiles (
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

-- Only fire if not already exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

- [ ] **Step 2: Create skill_profiles table SQL**

```sql
-- sql/002_skill_profiles.sql
CREATE TABLE IF NOT EXISTS skill_profiles (
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

-- RLS: users can only read/write their own profile
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
```

- [ ] **Step 3: Commit**

```bash
git add sql/001_profiles.sql sql/002_skill_profiles.sql
git commit -m "feat: add profiles and skill_profiles schema"
```

---

### Task 2: Wire Student_Login_code.html with Real Supabase

**Files:**
- Modify: `frontend/Student_Login_code.html`

**Interfaces:**
- Consumes: Supabase project URL + anon key (user provides)
- Produces: Working signup/login, redirect to `assessment.html` after auth

- [ ] **Step 1: Replace placeholder Supabase credentials**

In `frontend/Student_Login_code.html`, find and replace:
```js
// OLD
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';

// NEW — user must replace with real values
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
```

Keep as placeholders for now — user fills in via Supabase dashboard.

- [ ] **Step 2: Add redirect logic after login**

In the `checkUser()` function, after detecting a logged-in user, add redirect logic:

```js
async function checkUser() {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
        // Check if user has a skill profile
        const { data: profile } = await supabase
            .from('skill_profiles')
            .select('id')
            .eq('user_id', user.id)
            .single();

        if (profile) {
            // Has profile — go to dashboard (future)
            // window.location.href = 'dashboard.html';
        } else {
            // No profile — go to assessment
            window.location.href = 'assessment.html';
        }
    }
}
```

- [ ] **Step 3: Add redirect after signup**

In the signup form handler, after successful signup, redirect to assessment:

```js
// Inside signupForm submit handler, after successful signUp
const { error } = await supabase.auth.signUp({ email, password });
if (error) alert(error.message);
else {
    alert("Registration successful! Please check your email.");
    window.location.href = 'assessment.html';
}
```

- [ ] **Step 4: Test manually**

1. Open `Student_Login_code.html` in browser
2. Sign up with a new email
3. Verify redirect to `assessment.html`
4. Log out, log back in
5. Verify redirect to `assessment.html` (no skill profile yet)

- [ ] **Step 5: Commit**

```bash
git add frontend/Student_Login_code.html
git commit -m "feat: wire student auth with Supabase redirect to assessment"
```

---

### Task 3: Assessment Wizard — HTML Structure + Step 1 (Industry Selection)

**Files:**
- Create: `frontend/assessment.html`

**Interfaces:**
- Consumes: Supabase JS SDK (CDN), Tailwind CSS (CDN), Solaris Design System tokens
- Produces: `assessment.html` with working Step 1

- [ ] **Step 1: Create base HTML with Solaris Design System**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>Mindurr | Skill Assessment</title>
    <link href="https://fonts.googleapis.com/css2?family=geist:wght@100..900&family=inter:wght@100..900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        "background": "#fcfae6",
                        "primary": "#785a00",
                        "on-surface": "#1c1917",
                        "on-surface-variant": "#44403c",
                        "surface": "#fefce8",
                        "surface-container-low": "#f6f4e1",
                        "surface-container-lowest": "#ffffff",
                        "primary-container": "#eab308",
                        "on-primary-container": "#604700",
                        "secondary": "#885123",
                        "tertiary": "#00658e",
                        "outline": "#a8a29e",
                        "outline-variant": "#d6d3d1",
                        "inverse-surface": "#313124",
                        "inverse-on-surface": "#f3f2de"
                    },
                    fontFamily: {
                        "display": ["geist"],
                        "body": ["inter"]
                    }
                }
            }
        };
    </script>
    <style>
        ::-webkit-scrollbar { display: none; }
        .hidden { display: none !important; }
        .step-card { transition: all 0.3s ease; }
        .step-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px -4px rgba(66, 32, 6, 0.09); }
        .step-card.selected { border-color: var(--primary-container); background-color: #fef9c3; }
        .progress-fill { transition: width 0.4s ease; }
    </style>
</head>
<body class="bg-background font-body text-on-surface antialiased min-h-screen">
    <!-- Content goes here -->
    <script>
        // Supabase init + wizard logic goes here
    </script>
</body>
</html>
```

- [ ] **Step 2: Add wizard container HTML**

Inside `<body>`, add the main container:

```html
<main class="pt-24 pb-16 min-h-screen flex flex-col items-center px-6">
    <div class="w-full max-w-2xl">
        <!-- Header -->
        <div class="text-center mb-10">
            <span class="text-[11px] font-bold text-primary tracking-widest uppercase block mb-2">Skill Profiling</span>
            <h1 class="text-3xl font-extrabold tracking-tight" id="wizard-title">Select Your Industry</h1>
            <p class="text-on-surface-variant mt-2 text-sm" id="wizard-subtitle">Choose the field you want to be assessed in.</p>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-outline-variant/30 rounded-full h-2 mb-10">
            <div class="bg-primary-container h-2 rounded-full progress-fill" id="progress-bar" style="width: 25%"></div>
        </div>

        <!-- Step Containers (shown/hidden) -->
        <div id="step-1" class="step-content"><!-- Industry cards --></div>
        <div id="step-2" class="step-content hidden"><!-- Language cards --></div>
        <div id="step-3" class="step-content hidden"><!-- Technology cards --></div>
        <div id="step-4" class="step-content hidden"><!-- Assessment --></div>
        <div id="step-results" class="step-content hidden"><!-- Results --></div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-10" id="nav-buttons">
            <button class="btn-secondary hidden" id="prev-btn">Back</button>
            <button class="btn-primary ml-auto" id="next-btn" disabled>Next</button>
        </div>
    </div>
</main>
```

- [ ] **Step 3: Add Step 1 industry cards HTML**

Inside `#step-1`:

```html
<div class="grid grid-cols-2 gap-4" id="industry-grid">
    <!-- Populated by JS -->
</div>
```

- [ ] **Step 4: Add industry data + render Step 1 in JS**

Inside `<script>`:

```js
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const INDUSTRIES = {
    frontend: { label: 'Frontend', icon: 'language', desc: 'Web UIs, components, browsers' },
    backend: { label: 'Backend', icon: 'dns', desc: 'APIs, servers, databases' },
    devops: { label: 'DevOps', icon: 'cloud', desc: 'Infrastructure, CI/CD, containers' },
    data_science: { label: 'Data Science', icon: 'analytics', desc: 'ML, stats, data pipelines' },
    mobile: { label: 'Mobile', icon: 'smartphone', desc: 'iOS, Android, cross-platform' },
    fullstack: { label: 'Full-Stack', icon: 'terminal', desc: 'End-to-end web development' }
};

let state = { step: 1, industry: null, languages: [], technologies: [], questions: [], answers: {} };

function renderIndustries() {
    const grid = document.getElementById('industry-grid');
    grid.innerHTML = Object.entries(INDUSTRIES).map(([key, ind]) => `
        <button data-industry="${key}"
            class="step-card text-left p-5 rounded-xl border-2 border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container transition-all">
            <span class="material-symbols-outlined text-primary text-2xl mb-2">${ind.icon}</span>
            <h3 class="font-bold text-on-surface">${ind.label}</h3>
            <p class="text-xs text-on-surface-variant mt-1">${ind.desc}</p>
        </button>
    `).join('');

    grid.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            grid.querySelectorAll('button').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            state.industry = btn.dataset.industry;
            document.getElementById('next-btn').disabled = false;
        });
    });
}

renderIndustries();
```

- [ ] **Step 5: Add navigation button styling**

Add to `<style>`:

```css
.btn-primary {
    background-color: #eab308;
    color: #422006;
    font-weight: 700;
    padding: 10px 28px;
    border-radius: 9999px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.15s ease;
}
.btn-primary:hover { background-color: #dfa806; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary {
    background-color: transparent;
    color: var(--on-surface-variant);
    font-weight: 700;
    padding: 10px 28px;
    border-radius: 9999px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid var(--outline-variant);
}
.btn-secondary:hover { background-color: var(--surface-container-low); }
```

- [ ] **Step 6: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: assessment wizard step 1 - industry selection"
```

---

### Task 4: Assessment Wizard — Step 2 (Language Selection)

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: `state.industry` from Step 1
- Produces: `state.languages` array

- [ ] **Step 1: Add language data to INDUSTRIES**

Update the `INDUSTRIES` object to include languages and technologies:

```js
const INDUSTRIES = {
    frontend: {
        label: 'Frontend', icon: 'language', desc: 'Web UIs, components, browsers',
        languages: ['JavaScript', 'TypeScript', 'HTML/CSS'],
        technologies: {
            'JavaScript': ['React', 'Vue.js', 'Angular', 'Next.js', 'Svelte'],
            'TypeScript': ['React', 'Angular', 'Next.js'],
            'HTML/CSS': ['Tailwind CSS', 'SASS/SCSS', 'Bootstrap']
        }
    },
    backend: {
        label: 'Backend', icon: 'dns', desc: 'APIs, servers, databases',
        languages: ['Python', 'JavaScript', 'Java', 'Go', 'Rust'],
        technologies: {
            'Python': ['Django', 'FastAPI', 'Flask', 'Celery'],
            'JavaScript': ['Express.js', 'NestJS', 'Fastify'],
            'Java': ['Spring Boot', 'Micronaut'],
            'Go': ['Gin', 'Echo', 'Fiber'],
            'Rust': ['Actix Web', 'Axum']
        }
    },
    devops: {
        label: 'DevOps', icon: 'cloud', desc: 'Infrastructure, CI/CD, containers',
        languages: ['Python', 'Bash', 'Go'],
        technologies: {
            'Python': ['Docker', 'Kubernetes', 'Terraform', 'Ansible'],
            'Bash': ['Docker', 'Linux Administration', 'CI/CD'],
            'Go': ['Docker', 'Kubernetes', 'Terraform']
        }
    },
    data_science: {
        label: 'Data Science', icon: 'analytics', desc: 'ML, stats, data pipelines',
        languages: ['Python', 'R', 'SQL'],
        technologies: {
            'Python': ['Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch'],
            'R': ['ggplot2', 'dplyr', 'Shiny'],
            'SQL': ['PostgreSQL', 'MySQL', 'BigQuery']
        }
    },
    mobile: {
        label: 'Mobile', icon: 'smartphone', desc: 'iOS, Android, cross-platform',
        languages: ['JavaScript', 'Dart', 'Kotlin', 'Swift'],
        technologies: {
            'JavaScript': ['React Native', 'Expo'],
            'Dart': ['Flutter'],
            'Kotlin': ['Android Jetpack Compose'],
            'Swift': ['SwiftUI', 'UIKit']
        }
    },
    fullstack: {
        label: 'Full-Stack', icon: 'terminal', desc: 'End-to-end web development',
        languages: ['JavaScript', 'TypeScript', 'Python'],
        technologies: {
            'JavaScript': ['React', 'Node.js', 'Express.js', 'Next.js'],
            'TypeScript': ['React', 'Next.js', 'NestJS'],
            'Python': ['Django', 'FastAPI', 'Flask']
        }
    }
};
```

- [ ] **Step 2: Add Step 2 language cards HTML**

Inside `#step-2`:

```html
<div class="grid grid-cols-2 gap-3" id="language-grid">
    <!-- Populated by JS -->
</div>
<p class="text-xs text-on-surface-variant mt-4 text-center">Select at least one language you know.</p>
```

- [ ] **Step 3: Add renderLanguages function**

```js
function renderLanguages() {
    const grid = document.getElementById('language-grid');
    const langs = INDUSTRIES[state.industry].languages;
    grid.innerHTML = langs.map(lang => `
        <button data-lang="${lang}"
            class="step-card text-left p-4 rounded-xl border-2 border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container transition-all">
            <h3 class="font-bold text-on-surface text-sm">${lang}</h3>
        </button>
    `).join('');

    grid.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('selected');
            state.languages = [...grid.querySelectorAll('.selected')].map(b => b.dataset.lang);
            document.getElementById('next-btn').disabled = state.languages.length === 0;
        });
    });
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: assessment wizard step 2 - language selection"
```

---

### Task 5: Assessment Wizard — Step 3 (Technology Selection)

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: `state.industry`, `state.languages` from Steps 1-2
- Produces: `state.technologies` array

- [ ] **Step 1: Add Step 3 technology cards HTML**

Inside `#step-3`:

```html
<div class="grid grid-cols-2 gap-3" id="tech-grid">
    <!-- Populated by JS -->
</div>
<p class="text-xs text-on-surface-variant mt-4 text-center">Select at least one technology you're familiar with.</p>
```

- [ ] **Step 2: Add renderTechnologies function**

```js
function renderTechnologies() {
    const grid = document.getElementById('tech-grid');
    const techMap = INDUSTRIES[state.industry].technologies;
    const techs = new Set();
    state.languages.forEach(lang => {
        (techMap[lang] || []).forEach(t => techs.add(t));
    });

    grid.innerHTML = [...techs].map(tech => `
        <button data-tech="${tech}"
            class="step-card text-left p-4 rounded-xl border-2 border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container transition-all">
            <h3 class="font-bold text-on-surface text-sm">${tech}</h3>
        </button>
    `).join('');

    grid.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('selected');
            state.technologies = [...grid.querySelectorAll('.selected')].map(b => b.dataset.tech);
            document.getElementById('next-btn').disabled = state.technologies.length === 0;
        });
    });
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: assessment wizard step 3 - technology selection"
```

---

### Task 6: Assessment Wizard — Static Question Bank

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Produces: `QUESTIONS` object keyed by technology name

- [ ] **Step 1: Add question bank JS object**

Add a comprehensive question bank. Each technology gets 5-8 questions (enough to reach 25-30 total across selected technologies):

```js
const QUESTIONS = {
    'React': [
        { q: 'What hook is used for side effects in React?', options: ['useState', 'useEffect', 'useRef', 'useMemo'], answer: 1 },
        { q: 'What does JSX compile to?', options: ['HTML', 'React.createElement()', 'DOM nodes', 'Virtual DOM'], answer: 1 },
        { q: 'Which prop causes a component to re-render?', options: ['key', 'ref', 'state change', 'className'], answer: 2 },
        { q: 'What is the virtual DOM?', options: ['A copy of the real DOM', 'A browser API', 'A CSS framework', 'A database'], answer: 0 },
        { q: 'Which method prevents unnecessary re-renders?', options: ['componentDidMount', 'React.memo', 'render', 'componentWillUpdate'], answer: 1 },
        { q: 'What does useCallback return?', options: ['A memoized value', 'A memoized function', 'A new component', 'A DOM node'], answer: 1 },
        { q: 'What is prop drilling?', options: ['Passing props through many layers', 'Using refs', 'Using context', 'Using Redux'], answer: 0 },
        { q: 'Which hook manages form input state?', options: ['useEffect', 'useReducer', 'useState', 'useContext'], answer: 2 }
    ],
    'Python': [
        { q: 'What is a decorator in Python?', options: ['A function that modifies another function', 'A class', 'A variable', 'A loop'], answer: 0 },
        { q: 'What does "self" refer to?', options: ['The class itself', 'The current instance', 'The parent class', 'The module'], answer: 1 },
        { q: 'Which keyword defines a generator?', options: ['return', 'yield', 'async', 'await'], answer: 1 },
        { q: 'What is a list comprehension?', options: ['A way to create lists concisely', 'A type of loop', 'A function', 'A class'], answer: 0 },
        { q: 'What does *args allow?', options: ['Keyword arguments', 'Variable positional arguments', 'Variable keyword arguments', 'No arguments'], answer: 1 },
        { q: 'What is the GIL?', options: ['Global Interface Layer', 'Global Interpreter Lock', 'General Input Loop', 'Generic Import Loader'], answer: 1 },
        { q: 'Which module handles HTTP requests?', options: ['os', 'sys', 'requests', 'json'], answer: 2 },
        { q: 'What is a lambda function?', options: ['An anonymous function', 'A named function', 'A class method', 'A generator'], answer: 0 }
    ],
    'TypeScript': [
        { q: 'What is TypeScript?', options: ['A superset of JavaScript', 'A new language', 'A framework', 'A library'], answer: 0 },
        { q: 'What does the "interface" keyword do?', options: ['Creates a class', 'Defines a contract', 'Imports a module', 'Exports a function'], answer: 1 },
        { q: 'What is a generic type?', options: ['A type that takes parameters', 'Any type', 'A number type', 'A string type'], answer: 0 },
        { q: 'What is the "any" type?', options: ['Type-safe escape hatch', 'Unknown type', 'Never type', 'Null type'], answer: 0 },
        { q: 'What does "enum" define?', options: ['A function', 'A set of named constants', 'A class', 'An array'], answer: 1 },
        { q: 'What is type assertion?', options: ['Telling compiler the type', 'Creating a type', 'Deleting a type', 'Importing a type'], answer: 0 },
        { q: 'What does "readonly" do?', options: ['Makes a property immutable', 'Deletes a property', 'Copies a property', 'Hides a property'], answer: 0 }
    ],
    'JavaScript': [
        { q: 'What is a closure?', options: ['A function with access to outer scope', 'A loop', 'A class', 'A module'], answer: 0 },
        { q: 'What does "===" check?', options: ['Value only', 'Value and type', 'Reference only', 'Neither'], answer: 1 },
        { q: 'What is the event loop?', options: ['A for loop', 'A mechanism for async operations', 'A recursion pattern', 'A DOM API'], answer: 1 },
        { q: 'What does Array.map() return?', options: ['The original array', 'A new array', 'undefined', 'A boolean'], answer: 1 },
        { q: 'What is "hoisting"?', options: ['Moving declarations to top', 'Deleting variables', 'Creating classes', 'Importing modules'], answer: 0 },
        { q: 'What does Promise.resolve() do?', options: ['Rejects a promise', 'Creates a resolved promise', 'Cancels a promise', 'Waits for a promise'], answer: 1 },
        { q: 'What is destructuring?', options: ['Extracting values from objects/arrays', 'Destroying variables', 'Creating objects', 'Merging arrays'], answer: 0 }
    ],
    'Vue.js': [
        { q: 'What is a Vue component?', options: ['A reusable UI piece', 'A database table', 'An API endpoint', 'A CSS file'], answer: 0 },
        { q: 'What does v-bind do?', options: ['Binds data to attributes', 'Creates events', 'Loops through data', 'Conditionally renders'], answer: 0 },
        { q: 'What is the Composition API?', options: ['A way to organize component logic', 'A CSS framework', 'A routing library', 'A build tool'], answer: 0 },
        { q: 'What does v-model create?', options: ['Two-way data binding', 'One-way binding', 'Event listener', 'Computed property'], answer: 0 },
        { q: 'What are Vue lifecycle hooks?', options: ['Points in component lifecycle', 'CSS animations', 'API calls', 'Database queries'], answer: 0 }
    ],
    'Django': [
        { q: 'What is Django ORM?', options: ['Object-Relational Mapper', 'Online Resource Manager', 'Output Response Model', 'Open Runtime Module'], answer: 0 },
        { q: 'What is a Django migration?', options: ['Database schema change', 'File upload', 'User redirect', 'CSS transform'], answer: 0 },
        { q: 'What does models.Model provide?', options: ['Base class for database models', 'HTML templates', 'CSS styles', 'JavaScript functions'], answer: 0 },
        { q: 'What is Django REST Framework?', options: ['Library for building APIs', 'A database', 'A CSS framework', 'A testing tool'], answer: 0 },
        { q: 'What is a Django view?', options: ['A function/class handling requests', 'An HTML file', 'A database table', 'A JavaScript file'], answer: 0 }
    ],
    'FastAPI': [
        { q: 'What is FastAPI built on?', options: ['Starlette and Pydantic', 'Django and Flask', 'Express and Node', 'Spring and Java'], answer: 0 },
        { q: 'What does @app.get() do?', options: ['Defines a GET route', 'Creates a database', 'Uploads a file', 'Deletes a resource'], answer: 0 },
        { q: 'What is Pydantic used for?', options: ['Data validation', 'HTML rendering', 'CSS styling', 'File management'], answer: 0 },
        { q: 'What is async in FastAPI?', options: ['Asynchronous request handling', 'Database sync', 'File upload', 'User authentication'], answer: 0 },
        { q: 'What does dependency injection provide?', options: ['Shared resources to routes', 'Database connections only', 'HTML templates', 'CSS styles'], answer: 0 }
    ],
    'Node.js': [
        { q: 'What is Node.js?', options: ['JavaScript runtime', 'A database', 'A CSS framework', 'An IDE'], answer: 0 },
        { q: 'What does npm do?', options: ['Package management', 'File editing', 'Database queries', 'HTML rendering'], answer: 0 },
        { q: 'What is Express.js?', options: ['Web framework for Node', 'A database', 'A testing tool', 'A CSS library'], answer: 0 },
        { q: 'What is middleware?', options: ['Functions that process requests', 'Database tables', 'HTML files', 'CSS styles'], answer: 0 },
        { q: 'What does require() do?', options: ['Imports modules', 'Exports data', 'Creates files', 'Deletes files'], answer: 0 }
    ],
    'Next.js': [
        { q: 'What is Next.js?', options: ['React framework with SSR', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is server-side rendering?', options: ['Rendering on the server', 'Rendering in browser', 'CSS rendering', 'Database rendering'], answer: 0 },
        { q: 'What are API routes in Next.js?', options: ['Backend endpoints in a React app', 'Frontend routes only', 'Database queries', 'CSS files'], answer: 0 },
        { q: 'What is static generation?', options: ['Pre-rendering at build time', 'Runtime rendering', 'Database queries', 'File uploads'], answer: 0 }
    ],
    'Angular': [
        { q: 'What is Angular?', options: ['A platform for building apps', 'A database', 'A CSS framework', 'A testing tool'], answer: 0 },
        { q: 'What is a component in Angular?', options: ['A class with a template', 'A database table', 'An API endpoint', 'A CSS file'], answer: 0 },
        { q: 'What does @NgModule do?', options: ['Defines a module', 'Creates a component', 'Handles events', 'Styles elements'], answer: 0 },
        { q: 'What is dependency injection?', options: ['Providing dependencies to classes', 'Creating databases', 'Styling elements', 'Testing code'], answer: 0 },
        { q: 'What is RxJS in Angular?', options: ['Reactive programming library', 'A database', 'A CSS framework', 'A testing tool'], answer: 0 }
    ],
    'Svelte': [
        { q: 'What is Svelte?', options: ['A compiler-based UI framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does $: do in Svelte?', options: ['Creates reactive declarations', 'Imports modules', 'Defines classes', 'Exports functions'], answer: 0 },
        { q: 'What is the store in Svelte?', options: ['Reactive state management', 'A database', 'A CSS framework', 'A testing tool'], answer: 0 }
    ],
    'Tailwind CSS': [
        { q: 'What is Tailwind CSS?', options: ['A utility-first CSS framework', 'A JavaScript library', 'A database', 'An API'], answer: 0 },
        { q: 'What does "flex" do?', options: ['Sets display: flex', 'Creates a function', 'Imports a module', 'Defines a variable'], answer: 0 },
        { q: 'How do you add hover styles?', options: ['hover:', 'on-hover:', 'mouse:', 'pointer:'], answer: 0 },
        { q: 'What is a Tailwind config?', options: ['Customization file for Tailwind', 'A database', 'An API endpoint', 'A CSS file'], answer: 0 }
    ],
    'SASS/SCSS': [
        { q: 'What is SASS?', options: ['A CSS preprocessor', 'A JavaScript library', 'A database', 'An API'], answer: 0 },
        { q: 'What does nesting do?', options: ['Organizes CSS hierarchically', 'Creates loops', 'Defines functions', 'Imports modules'], answer: 0 },
        { q: 'What is a mixin?', options: ['Reusable CSS patterns', 'A database table', 'An API endpoint', 'A JavaScript function'], answer: 0 }
    ],
    'Bootstrap': [
        { q: 'What is Bootstrap?', options: ['A CSS framework', 'A JavaScript runtime', 'A database', 'An API'], answer: 0 },
        { q: 'What does "col-md-6" do?', options: ['Creates a 6-column width on medium screens', 'Sets font size', 'Creates a row', 'Adds padding'], answer: 0 }
    ],
    'Express.js': [
        { q: 'What is Express.js?', options: ['Web framework for Node.js', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does app.use() do?', options: ['Mounts middleware', 'Creates a route', 'Deletes files', 'Connects to database'], answer: 0 },
        { q: 'What is req.params?', options: ['URL parameters', 'Query strings', 'Body data', 'Headers only'], answer: 0 },
        { q: 'What does res.json() do?', options: ['Sends JSON response', 'Parses JSON', 'Creates JSON', 'Deletes JSON'], answer: 0 }
    ],
    'NestJS': [
        { q: 'What is NestJS?', options: ['A Node.js framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a decorator in NestJS?', options: ['Metadata for classes/methods', 'A CSS pattern', 'A database query', 'A loop'], answer: 0 },
        { q: 'What is dependency injection?', options: ['Providing dependencies automatically', 'Creating databases', 'Styling elements', 'Testing code'], answer: 0 }
    ],
    'Fastify': [
        { q: 'What is Fastify?', options: ['Fast web framework for Node', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What makes Fastify fast?', options: ['Serialization and schema validation', 'No features', 'Small file size', 'No dependencies'], answer: 0 }
    ],
    'Spring Boot': [
        { q: 'What is Spring Boot?', options: ['Java framework for microservices', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is @SpringBootApplication?', options: ['Main entry point annotation', 'A database', 'A CSS file', 'An HTML template'], answer: 0 },
        { q: 'What is Spring Data JPA?', options: ['Database access abstraction', 'A web framework', 'A testing tool', 'A CSS library'], answer: 0 }
    ],
    'Micronaut': [
        { q: 'What is Micronaut?', options: ['A microservice framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is compile-time DI?', options: ['Dependency injection at compile time', 'Runtime injection', 'Database queries', 'CSS processing'], answer: 0 }
    ],
    'Gin': [
        { q: 'What is Gin?', options: ['Go web framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does c.JSON() do?', options: ['Sends JSON response', 'Parses JSON', 'Creates JSON file', 'Deletes JSON'], answer: 0 }
    ],
    'Echo': [
        { q: 'What is Echo?', options: ['Go web framework', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Fiber': [
        { q: 'What is Fiber?', options: ['Go web framework inspired by Express', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Actix Web': [
        { q: 'What is Actix Web?', options: ['Rust web framework', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Axum': [
        { q: 'What is Axum?', options: ['Rust web framework', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Docker': [
        { q: 'What is a Docker container?', options: ['An isolated process environment', 'A virtual machine', 'A database', 'An API'], answer: 0 },
        { q: 'What does a Dockerfile define?', options: ['Image build instructions', 'Database schema', 'CSS styles', 'HTML templates'], answer: 0 },
        { q: 'What is docker-compose?', options: ['Multi-container orchestration', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a Docker image?', options: ['Blueprint for containers', 'A running process', 'A database', 'An API'], answer: 0 }
    ],
    'Kubernetes': [
        { q: 'What is a Pod?', options: ['Smallest deployable unit', 'A database', 'A CSS file', 'An API'], answer: 0 },
        { q: 'What is a Deployment?', options: ['Manages replica sets', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a Service in K8s?', options: ['Network endpoint for pods', 'A database', 'A CSS file', 'An HTML template'], answer: 0 },
        { q: 'What is kubectl?', options: ['Kubernetes CLI', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Terraform': [
        { q: 'What is Terraform?', options: ['Infrastructure as Code tool', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a .tf file?', options: ['Terraform configuration', 'A database', 'A CSS file', 'An HTML template'], answer: 0 },
        { q: 'What does terraform apply do?', options: ['Applies infrastructure changes', 'Deletes resources', 'Creates databases', 'Styles elements'], answer: 0 }
    ],
    'Ansible': [
        { q: 'What is Ansible?', options: ['Configuration management tool', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a playbook?', options: ['YAML file defining tasks', 'A database', 'A CSS file', 'An HTML template'], answer: 0 }
    ],
    'Linux Administration': [
        { q: 'What does chmod 755 do?', options: ['Sets file permissions', 'Creates files', 'Deletes files', 'Copies files'], answer: 0 },
        { q: 'What is systemctl?', options: ['Service management tool', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does grep do?', options: ['Searches text patterns', 'Copies files', 'Deletes files', 'Creates directories'], answer: 0 }
    ],
    'CI/CD': [
        { q: 'What is CI?', options: ['Continuous Integration', 'Computer Interface', 'Code Injection', 'Core Infrastructure'], answer: 0 },
        { q: 'What is CD?', options: ['Continuous Delivery/Deployment', 'Computer Database', 'Code Directory', 'Core Data'], answer: 0 },
        { q: 'What is a pipeline?', options: ['Automated build/test/deploy sequence', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'Pandas': [
        { q: 'What is a DataFrame?', options: ['2D labeled data structure', 'A database', 'A CSS file', 'An API'], answer: 0 },
        { q: 'What does df.head() do?', options: ['Shows first 5 rows', 'Deletes data', 'Creates tables', 'Styles data'], answer: 0 },
        { q: 'What is pandas used for?', options: ['Data manipulation and analysis', 'Web development', 'Mobile apps', 'Game development'], answer: 0 }
    ],
    'NumPy': [
        { q: 'What is NumPy?', options: ['Numerical computing library', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a NumPy array?', options: ['Homogeneous data structure', 'A database', 'A CSS file', 'An HTML template'], answer: 0 },
        { q: 'What does np.array() do?', options: ['Creates an array', 'Deletes data', 'Styles elements', 'Imports modules'], answer: 0 }
    ],
    'Scikit-learn': [
        { q: 'What is Scikit-learn?', options: ['Machine learning library', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a pipeline in sklearn?', options: ['Sequence of transforms and model', 'A database', 'A CSS file', 'An API'], answer: 0 },
        { q: 'What does train_test_split do?', options: ['Splits data for training/testing', 'Creates models', 'Styles data', 'Imports modules'], answer: 0 }
    ],
    'TensorFlow': [
        { q: 'What is TensorFlow?', options: ['Deep learning framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a tensor?', options: ['Multi-dimensional array', 'A database', 'A CSS file', 'An HTML template'], answer: 0 }
    ],
    'PyTorch': [
        { q: 'What is PyTorch?', options: ['Deep learning framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a torch.Tensor?', options: ['Multi-dimensional array with autograd', 'A database', 'A CSS file', 'An API'], answer: 0 },
        { q: 'What is autograd?', options: ['Automatic differentiation', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'ggplot2': [
        { q: 'What is ggplot2?', options: ['R plotting library', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is the grammar of graphics?', options: ['Layered approach to visualization', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'dplyr': [
        { q: 'What is dplyr?', options: ['R data manipulation library', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does filter() do?', options: ['Selects rows by condition', 'Deletes data', 'Creates tables', 'Styles elements'], answer: 0 }
    ],
    'Shiny': [
        { q: 'What is Shiny?', options: ['R web application framework', 'A database', 'A CSS framework', 'An API'], answer: 0 }
    ],
    'PostgreSQL': [
        { q: 'What is PostgreSQL?', options: ['Relational database', 'A CSS framework', 'An API', 'A testing tool'], answer: 0 },
        { q: 'What is a primary key?', options: ['Unique identifier for rows', 'A CSS property', 'An API endpoint', 'A JavaScript function'], answer: 0 },
        { q: 'What does JOIN do?', options: ['Combines rows from tables', 'Creates tables', 'Deletes data', 'Styles elements'], answer: 0 },
        { q: 'What is an index?', options: ['Speeds up data retrieval', 'Creates tables', 'Deletes data', 'Styles elements'], answer: 0 }
    ],
    'MySQL': [
        { q: 'What is MySQL?', options: ['Relational database', 'A CSS framework', 'An API', 'A testing tool'], answer: 0 },
        { q: 'What is a foreign key?', options: ['Links tables together', 'A CSS property', 'An API endpoint', 'A JavaScript function'], answer: 0 }
    ],
    'BigQuery': [
        { q: 'What is BigQuery?', options: ['Google\'s data warehouse', 'A CSS framework', 'An API', 'A testing tool'], answer: 0 },
        { q: 'What is BigQuery best for?', options: ['Analyzing large datasets', 'Web development', 'Mobile apps', 'Game development'], answer: 0 }
    ],
    'React Native': [
        { q: 'What is React Native?', options: ['Cross-platform mobile framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a bridge in React Native?', options: ['Connects JS to native modules', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'Expo': [
        { q: 'What is Expo?', options: ['Toolchain for React Native', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What does expo start do?', options: ['Starts development server', 'Creates database', 'Styles elements', 'Imports modules'], answer: 0 }
    ],
    'Flutter': [
        { q: 'What is Flutter?', options: ['Cross-platform UI toolkit', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a Widget in Flutter?', options: ['UI building block', 'A database', 'A CSS file', 'An API'], answer: 0 },
        { q: 'What language does Flutter use?', options: ['Dart', 'JavaScript', 'Python', 'Java'], answer: 0 }
    ],
    'Android Jetpack Compose': [
        { q: 'What is Jetpack Compose?', options: ['Android UI toolkit', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a composable?', options: ['A UI function', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'SwiftUI': [
        { q: 'What is SwiftUI?', options: ['Apple\'s declarative UI framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a View in SwiftUI?', options: ['A protocol for UI components', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'UIKit': [
        { q: 'What is UIKit?', options: ['Apple\'s imperative UI framework', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a UIViewController?', options: ['Manages a view hierarchy', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'Celery': [
        { q: 'What is Celery?', options: ['Distributed task queue', 'A database', 'A CSS framework', 'An API'], answer: 0 },
        { q: 'What is a Celery worker?', options: ['Process that executes tasks', 'A database', 'A CSS file', 'An API'], answer: 0 }
    ],
    'HTML/CSS': [
        { q: 'What does HTML stand for?', options: ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyper Transfer Markup Language'], answer: 0 },
        { q: 'What does CSS stand for?', options: ['Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style System', 'Colorful Style Sheets'], answer: 0 },
        { q: 'What is the box model?', options: ['Content, padding, border, margin', 'A database', 'An API', 'A JavaScript concept'], answer: 0 },
        { q: 'What does display: flex do?', options: ['Enables flexbox layout', 'Hides element', 'Creates a database', 'Imports a module'], answer: 0 }
    ],
    'SQL': [
        { q: 'What does SELECT do?', options: ['Retrieves data from tables', 'Creates tables', 'Deletes data', 'Updates data'], answer: 0 },
        { q: 'What does WHERE clause do?', options: ['Filters rows', 'Creates tables', 'Joins tables', 'Groups data'], answer: 0 },
        { q: 'What is a JOIN?', options: ['Combines rows from multiple tables', 'Creates tables', 'Deletes data', 'Updates data'], answer: 0 },
        { q: 'What does GROUP BY do?', options: ['Groups rows by column', 'Creates tables', 'Deletes data', 'Sorts data'], answer: 0 }
    ]
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: add static question bank for assessment"
```

---

### Task 7: Assessment Wizard — Step 4 (Take Assessment)

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: `QUESTIONS` bank, `state.technologies` from Step 3
- Produces: `state.answers` object

- [ ] **Step 1: Add Step 4 assessment HTML**

Inside `#step-4`:

```html
<div id="assessment-container">
    <!-- Populated by JS -->
</div>
<div class="flex justify-between items-center mt-6">
    <span class="text-sm text-on-surface-variant" id="question-counter">Question 1 of 25</span>
    <span class="text-sm font-bold text-primary" id="score-live">Score: 0/0</span>
</div>
```

- [ ] **Step 2: Add buildAssessment function**

```js
function buildAssessment() {
    const container = document.getElementById('assessment-container');
    state.questions = [];

    state.technologies.forEach(tech => {
        const qs = QUESTIONS[tech] || [];
        qs.forEach(q => {
            state.questions.push({ ...q, technology: tech });
        });
    });

    // Shuffle and take up to 30 questions
    state.questions = state.questions.sort(() => Math.random() - 0.5).slice(0, 30);
    state.answers = {};

    renderQuestion();
}

function renderQuestion() {
    const container = document.getElementById('assessment-container');
    const idx = Object.keys(state.answers).length;
    const total = state.questions.length;

    if (idx >= total) {
        showResults();
        return;
    }

    const q = state.questions[idx];
    document.getElementById('question-counter').textContent = `Question ${idx + 1} of ${total}`;
    document.getElementById('score-live').textContent = `Score: ${Object.values(state.answers).filter(a => a.correct).length}/${idx}`;

    container.innerHTML = `
        <div class="mb-4">
            <span class="text-[10px] font-bold text-tertiary uppercase tracking-widest">${q.technology}</span>
            <h3 class="text-lg font-bold mt-1">${q.q}</h3>
        </div>
        <div class="flex flex-col gap-3">
            ${q.options.map((opt, i) => `
                <button data-idx="${i}"
                    class="step-card text-left p-4 rounded-xl border-2 border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container transition-all text-sm">
                    ${opt}
                </button>
            `).join('')}
        </div>
    `;

    container.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            const answerIdx = parseInt(btn.dataset.idx);
            state.answers[idx] = { answer: answerIdx, correct: answerIdx === q.answer };

            // Show correct/wrong
            container.querySelectorAll('button').forEach((b, i) => {
                b.disabled = true;
                if (i === q.answer) b.classList.add('selected');
                else if (i === answerIdx && answerIdx !== q.answer) {
                    b.style.borderColor = '#ba1a1a';
                    b.style.backgroundColor = '#ffdad6';
                }
            });

            setTimeout(() => renderQuestion(), 800);
        });
    });
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: assessment wizard step 4 - question rendering"
```

---

### Task 8: Assessment Wizard — Results + Save to Supabase

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: `state.answers`, `state.questions`, `state.industry`, `state.languages`, `state.technologies`
- Produces: Supabase `skill_profiles` row, results display

- [ ] **Step 1: Add showResults function**

```js
function showResults() {
    document.getElementById('step-4').classList.add('hidden');
    document.getElementById('step-results').classList.remove('hidden');
    document.getElementById('nav-buttons').classList.add('hidden');

    // Calculate scores per technology
    const techScores = {};
    const techCounts = {};
    state.questions.forEach((q, idx) => {
        if (!techScores[q.technology]) { techScores[q.technology] = 0; techCounts[q.technology] = 0; }
        techCounts[q.technology]++;
        if (state.answers[idx]?.correct) techScores[q.technology]++;
    });

    const scores = {};
    let totalCorrect = 0, totalQuestions = 0;
    Object.keys(techScores).forEach(tech => {
        scores[tech] = Math.round((techScores[tech] / techCounts[tech]) * 100);
        totalCorrect += techScores[tech];
        totalQuestions += techCounts[tech];
    });

    const totalScore = Math.round((totalCorrect / totalQuestions) * 100);

    // Render results
    const container = document.getElementById('step-results');
    container.innerHTML = `
        <div class="text-center mb-8">
            <span class="material-symbols-outlined text-primary text-5xl mb-4">emoji_events</span>
            <h2 class="text-2xl font-extrabold">Assessment Complete!</h2>
            <p class="text-on-surface-variant mt-2">Here's your skill profile.</p>
        </div>

        <div class="bg-surface-container-lowest rounded-xl p-6 border border-outline-variant/30 mb-6">
            <div class="text-center">
                <span class="text-5xl font-extrabold text-primary">${totalScore}%</span>
                <p class="text-sm text-on-surface-variant mt-1">Overall Score</p>
            </div>
        </div>

        <div class="space-y-3">
            ${Object.entries(scores).map(([tech, score]) => `
                <div class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
                    <span class="font-bold text-sm">${tech}</span>
                    <div class="flex items-center gap-3">
                        <div class="w-24 h-2 bg-outline-variant/30 rounded-full overflow-hidden">
                            <div class="h-full bg-primary-container rounded-full" style="width: ${score}%"></div>
                        </div>
                        <span class="text-sm font-bold text-on-surface-variant w-10 text-right">${score}%</span>
                    </div>
                </div>
            `).join('')}
        </div>

        <div class="text-center mt-8">
            <button onclick="saveProfile()" class="btn-primary" id="save-btn">Save Profile & Continue</button>
        </div>
    `;

    // Store for saving
    state.scores = scores;
    state.totalScore = totalScore;
}

async function saveProfile() {
    const btn = document.getElementById('save-btn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { window.location.href = 'Student_Login_code.html'; return; }

    const { error } = await supabase.from('skill_profiles').upsert({
        user_id: user.id,
        industry: state.industry,
        languages: state.languages,
        technologies: state.technologies,
        scores: state.scores,
        total_score: state.totalScore
    }, { onConflict: 'user_id' });

    if (error) {
        alert('Error saving profile: ' + error.message);
        btn.disabled = false;
        btn.textContent = 'Save Profile & Continue';
    } else {
        // Redirect to dashboard (future) or back to home
        window.location.href = 'index.html';
    }
}
```

- [ ] **Step 2: Add "Save Profile & Continue" button styling**

Already covered by `.btn-primary` class from earlier.

- [ ] **Step 3: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: assessment results display + Supabase save"
```

---

### Task 9: Wire Navigation Logic (Step Transitions)

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: `state` object, all render functions
- Produces: Working Next/Back buttons, step transitions

- [ ] **Step 1: Add step transition logic**

```js
function goToStep(step) {
    document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`step-${step}`).classList.remove('hidden');

    const titles = {
        1: ['Select Your Industry', 'Choose the field you want to be assessed in.'],
        2: ['Select Languages', 'Pick the programming languages you know.'],
        3: ['Select Technologies', 'Choose frameworks and tools you\'re familiar with.'],
        4: ['Take Assessment', 'Answer questions about your selected technologies.']
    };

    document.getElementById('wizard-title').textContent = titles[step]?.[0] || '';
    document.getElementById('wizard-subtitle').textContent = titles[step]?.[1] || '';
    document.getElementById('progress-bar').style.width = `${step * 25}%`;

    // Show/hide nav buttons
    document.getElementById('prev-btn').classList.toggle('hidden', step === 1);
    document.getElementById('next-btn').disabled = true;

    // Update next button text
    const nextBtn = document.getElementById('next-btn');
    if (step === 3) nextBtn.textContent = 'Start Assessment';
    else if (step === 4) { document.getElementById('nav-buttons').classList.add('hidden'); }
    else nextBtn.textContent = 'Next';
}

// Navigation button handlers
document.getElementById('next-btn').addEventListener('click', () => {
    if (state.step === 1) { state.step = 2; renderLanguages(); }
    else if (state.step === 2) { state.step = 3; renderTechnologies(); }
    else if (state.step === 3) { state.step = 4; buildAssessment(); }
    goToStep(state.step);
});

document.getElementById('prev-btn').addEventListener('click', () => {
    state.step--;
    goToStep(state.step);
    if (state.step === 1) document.getElementById('next-btn').disabled = !state.industry;
    else if (state.step === 2) document.getElementById('next-btn').disabled = state.languages.length === 0;
    else if (state.step === 3) document.getElementById('next-btn').disabled = state.technologies.length === 0;
});

// Auth check on load
async function init() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { window.location.href = 'Student_Login_code.html'; return; }

    // Check if already assessed
    const { data: profile } = await supabase
        .from('skill_profiles')
        .select('id')
        .eq('user_id', user.id)
        .single();

    if (profile) {
        // Already assessed — redirect to dashboard (future)
        // window.location.href = 'dashboard.html';
    }
}

init();
```

- [ ] **Step 2: Test full flow**

1. Open `Student_Login_code.html`, log in
2. Redirect to `assessment.html`
3. Select industry → Next
4. Select languages → Next
5. Select technologies → Start Assessment
6. Answer questions → Submit
7. See results → Save Profile
8. Verify row in Supabase `skill_profiles` table

- [ ] **Step 3: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: wire wizard navigation and auth check"
```

---

### Task 10: Polish + Error Handling

**Files:**
- Modify: `frontend/assessment.html`

**Interfaces:**
- Consumes: all existing functions
- Produces: toast notifications, validation, loading states

- [ ] **Step 1: Add toast notification system**

```js
function showToast(message, type = 'info') {
    const colors = { info: 'bg-inverse-surface', error: 'bg-red-700', success: 'bg-green-700' };
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 ${colors[type]} text-white px-5 py-3 rounded-xl text-sm font-bold shadow-lg z-50`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}
```

- [ ] **Step 2: Add Supabase credential check**

At the top of `init()`:

```js
if (SUPABASE_URL === 'YOUR_SUPABASE_URL') {
    showToast('Please set your Supabase credentials in the code', 'error');
    return;
}
```

- [ ] **Step 3: Add validation before step transitions**

Update the Next button handler to validate:

```js
document.getElementById('next-btn').addEventListener('click', () => {
    if (state.step === 1 && !state.industry) {
        showToast('Please select an industry', 'error');
        return;
    }
    if (state.step === 2 && state.languages.length === 0) {
        showToast('Please select at least one language', 'error');
        return;
    }
    if (state.step === 3 && state.technologies.length === 0) {
        showToast('Please select at least one technology', 'error');
        return;
    }
    // ... rest of transition logic
});
```

- [ ] **Step 4: Add loading state for save**

Already handled in `saveProfile()` with button disable + text change.

- [ ] **Step 5: Final manual test**

Full flow test:
1. Sign up → redirect to assessment
2. Complete assessment → save profile
3. Log out → log back in → should NOT redirect to assessment (profile exists)
4. Error states: empty selections, Supabase errors

- [ ] **Step 6: Commit**

```bash
git add frontend/assessment.html
git commit -m "feat: add validation, toasts, and error handling"
```

---

## Summary

| Task | Deliverable |
|------|-------------|
| 1 | SQL schema (profiles + skill_profiles) |
| 2 | Student_Login_code.html wired with Supabase |
| 3 | assessment.html with Step 1 (industry) |
| 4 | Step 2 (languages) |
| 5 | Step 3 (technologies) |
| 6 | Static question bank |
| 7 | Step 4 (assessment questions) |
| 8 | Results display + Supabase save |
| 9 | Navigation logic + auth check |
| 10 | Polish + error handling |
