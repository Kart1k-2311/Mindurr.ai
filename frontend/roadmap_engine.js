/**
 * Mindurr.ai - Client-Side Skill Intelligence & Learning Roadmap Engine
 * Analyzes assessment gaps and creates personalized 3-5 step actionable learning roadmaps.
 * Operates directly on Supabase via frontend SDK without requiring a separate backend.
 */

// Curated resource directory mapped to technologies
const RESOURCE_CATALOG = {
    'React': [
        { title: 'React Official Interactive Docs', platform: 'React.dev', type: 'Docs', url: 'https://react.dev/learn' },
        { title: 'Full Stack Open: Deep Dive into Modern Web Development', platform: 'University of Helsinki', type: 'Course', url: 'https://fullstackopen.com/en/' },
        { title: 'React Performance & Patterns Guide', platform: 'Patterns.dev', type: 'Article', url: 'https://www.patterns.dev/react' }
    ],
    'TypeScript': [
        { title: 'TypeScript Handbook (Official)', platform: 'TypeScriptLang', type: 'Docs', url: 'https://www.typescriptlang.org/docs/handbook/intro.html' },
        { title: 'Total TypeScript Core Tutorials', platform: 'TotalTypeScript', type: 'Tutorial', url: 'https://www.totaltypescript.com/tutorials' },
        { title: 'TypeScript Exercises & Typing Challenges', platform: 'TypeHero', type: 'Interactive', url: 'https://typehero.dev' }
    ],
    'Next.js': [
        { title: 'Next.js App Router Official Course', platform: 'Nextjs.org', type: 'Interactive Course', url: 'https://nextjs.org/learn' },
        { title: 'Mastering Next.js Server Components', platform: 'Vercel Guides', type: 'Docs', url: 'https://vercel.com/guides' }
    ],
    'Python': [
        { title: 'The Python Tutorial (Official)', platform: 'Python.org', type: 'Docs', url: 'https://docs.python.org/3/tutorial/' },
        { title: 'Real Python In-Depth Tutorials & Paths', platform: 'RealPython', type: 'Course', url: 'https://realpython.com' },
        { title: 'Automate the Boring Stuff with Python', platform: 'FreeCodeCamp', type: 'Book & Video', url: 'https://automatetheboringstuff.com' }
    ],
    'FastAPI': [
        { title: 'FastAPI Tutorial - User Guide', platform: 'FastAPI Docs', type: 'Docs', url: 'https://fastapi.tiangolo.com/tutorial/' },
        { title: 'Building Production APIs with FastAPI & SQLAlchemy', platform: 'TestDriven.io', type: 'Guide', url: 'https://testdriven.io' }
    ],
    'Django': [
        { title: 'Writing Your First Django App', platform: 'Django Docs', type: 'Docs', url: 'https://docs.djangoproject.com/en/stable/intro/tutorial01/' },
        { title: 'Django for Beginners (Complete Guide)', platform: 'MDN Web Docs', type: 'Guide', url: 'https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django' }
    ],
    'Node.js': [
        { title: 'Node.js Developer Guide & Best Practices', platform: 'Nodejs.org', type: 'Docs', url: 'https://nodejs.org/en/learn' },
        { title: 'The Odin Project: NodeJS Course', platform: 'The Odin Project', type: 'Curriculum', url: 'https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs' }
    ],
    'Docker': [
        { title: 'Docker Getting Started Official Guide', platform: 'Docker Docs', type: 'Interactive', url: 'https://docs.docker.com/get-started/' },
        { title: 'Docker & Containers for Beginners', platform: 'FreeCodeCamp', type: 'Course', url: 'https://www.freecodecamp.org/news/what-is-docker-used-for-a-docker-container-tutorial-for-beginners/' }
    ],
    'SQL': [
        { title: 'SQLBolt - Interactive SQL Lessons', platform: 'SQLBolt', type: 'Interactive', url: 'https://sqlbolt.com' },
        { title: 'Use The Index, Luke! (SQL Performance Guide)', platform: 'UseTheIndexLuke', type: 'Guide', url: 'https://use-the-index-luke.com' }
    ],
    'JavaScript': [
        { title: 'Modern JavaScript Tutorial (info)', platform: 'JavaScript.info', type: 'Docs', url: 'https://javascript.info' },
        { title: 'JavaScript Algorithms and Data Structures', platform: 'FreeCodeCamp', type: 'Interactive', url: 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/' }
    ]
};

// Fallback resources for unspecified technologies
const DEFAULT_RESOURCES = [
    { title: 'Roadmap.sh Developer Guides', platform: 'Roadmap.sh', type: 'Curriculum', url: 'https://roadmap.sh' },
    { title: 'FreeCodeCamp Developer Curriculum', platform: 'FreeCodeCamp', type: 'Course', url: 'https://www.freecodecamp.org' },
    { title: 'DevDocs API Documentation Aggregator', platform: 'DevDocs', type: 'Docs', url: 'https://devdocs.io' }
];

/**
 * Generate a personalized 3-to-5 step learning roadmap based on assessment results.
 * @param {Object} profile - { user_id, goal, industry, languages, technologies, scores, total_score }
 * @returns {Object} Structured roadmap object
 */
function generatePersonalizedRoadmap(profile) {
    const scores = profile.scores || {};
    const technologies = profile.technologies && profile.technologies.length > 0
        ? profile.technologies
        : Object.keys(scores);
    const goal = profile.goal || 'upskill';
    const industry = profile.industry || 'software_engineering';
    const totalScore = Number(profile.total_score) || 0;

    // Rank technologies by lowest score first to address gaps
    const rankedTechs = technologies.slice().sort((a, b) => {
        const scoreA = scores[a] !== undefined ? scores[a] : 50;
        const scoreB = scores[b] !== undefined ? scores[b] : 50;
        return scoreA - scoreB;
    });

    const primaryWeakness = rankedTechs[0] || 'Core Principles';
    const secondaryWeakness = rankedTechs[1] || 'Modern Tooling';
    const primaryStrength = rankedTechs[rankedTechs.length - 1] || 'Basic Syntax';

    const weakScore = scores[primaryWeakness] !== undefined ? scores[primaryWeakness] : 45;
    const strongScore = scores[primaryStrength] !== undefined ? scores[primaryStrength] : 75;

    // Generate humanized gap analysis summary
    let gapSummary = '';
    if (totalScore < 50) {
        gapSummary = `Your assessment shows strong potential in foundational logic, but critical gaps in ${primaryWeakness} (${weakScore}%) and ${secondaryWeakness} are holding back your readiness for ${industry.replace('_', ' ')} roles. Prioritizing fundamentals and hands-on component lifecycle debugging will quickly boost your hireability.`;
    } else if (totalScore < 75) {
        gapSummary = `Solid base identified with good mastery in ${primaryStrength} (${strongScore}%). To achieve senior-level proficiency and meet top industry benchmarks for your goal (${goal.replace('_', ' ')}), focus on hardening architectural patterns, state orchestration, and testing in ${primaryWeakness}.`;
    } else {
        gapSummary = `Exceptional mastery across ${primaryStrength} and related stack (${totalScore}% overall). Your path to a top-tier role focuses on high-scale system design, advanced caching, edge deployments, and building an interview-grade portfolio project.`;
    }

    // Curate step 1: Eliminate Primary Gap
    const step1Resources = RESOURCE_CATALOG[primaryWeakness] || DEFAULT_RESOURCES;
    const step1 = {
        step_number: 1,
        title: `Remediate ${primaryWeakness} Fundamentals & Core Patterns`,
        duration_weeks: 3,
        focus: primaryWeakness,
        status: 'in_progress',
        description: `Deep-dive into ${primaryWeakness} core primitives. Turn your lowest scoring area (${weakScore}%) into a reliable strength through deliberate practice.`,
        skills_to_build: [
            `${primaryWeakness} Lifecycle & Fundamentals`,
            `Debugging common ${primaryWeakness} anti-patterns`,
            `Unit testing fundamental logic and edges`
        ],
        milestones: [
            { id: 'm1_1', text: `Read and replicate standard patterns in official ${primaryWeakness} documentation`, completed: false },
            { id: 'm1_2', text: `Complete 10 focused exercises solving edge-cases in ${primaryWeakness}`, completed: false },
            { id: 'm1_3', text: `Build a minimalist CLI or sandbox tool demonstrating error handling`, completed: false }
        ],
        project: {
            title: `${primaryWeakness} Sandbox Prototype`,
            description: `Build and deploy a functional, self-contained module demonstrating clean architecture and 100% test coverage.`
        },
        resources: step1Resources
    };

    // Curate step 2: Modern Tooling & Secondary Gap
    const step2Resources = RESOURCE_CATALOG[secondaryWeakness] || RESOURCE_CATALOG['TypeScript'] || DEFAULT_RESOURCES;
    const step2 = {
        step_number: 2,
        title: `Master ${secondaryWeakness} & Production Workflow`,
        duration_weeks: 3,
        focus: secondaryWeakness,
        status: 'pending',
        description: `Integrate ${secondaryWeakness} into your primary workflow. Learn how modern development teams scale codebases with types, linters, and CI.`,
        skills_to_build: [
            `${secondaryWeakness} Architecture`,
            `State management & asynchronous data fetching`,
            `Type safety and contract validation`
        ],
        milestones: [
            { id: 'm2_1', text: `Configure strict typing and linting rules across your development setup`, completed: false },
            { id: 'm2_2', text: `Implement asynchronous state fetching with robust error recovery`, completed: false },
            { id: 'm2_3', text: `Refactor legacy spaghetti code into modular, reusable components`, completed: false }
        ],
        project: {
            title: `Production-Ready Service Integration`,
            description: `Connect your application to a real cloud database (Supabase) with end-to-end data contracts and validation.`
        },
        resources: step2Resources
    };

    // Curate step 3: Performance, Testing & Security
    const step3 = {
        step_number: 3,
        title: `Performance Optimization, Testing & Hardening`,
        duration_weeks: 3,
        focus: 'Performance & Reliability',
        status: 'pending',
        description: `Shift from 'making it work' to 'making it scale'. Profile bottlenecks, eliminate memory leaks, and add automated regression test suites.`,
        skills_to_build: [
            `Lighthouse performance profiling and Core Web Vitals`,
            `End-to-end testing with Playwright or Cypress`,
            `Security best practices (XSS, CORS, Auth tokens, RLS)`
        ],
        milestones: [
            { id: 'm3_1', text: `Achieve 95+ score on web performance and accessibility audits`, completed: false },
            { id: 'm3_2', text: `Write integration tests covering critical user authentication & checkout paths`, completed: false },
            { id: 'm3_3', text: `Audit database queries for proper indexing and RLS security policies`, completed: false }
        ],
        project: {
            title: `Automated CI Pipeline & Benchmark Test`,
            description: `Set up GitHub Actions to run linters, typechecks, and automated tests on every pull request.`
        },
        resources: [
            { title: 'Web.dev Performance Guides (Google)', platform: 'Web.dev', type: 'Docs', url: 'https://web.dev/explore/fast' },
            { title: 'OWASP Top 10 Security Risks for Developers', platform: 'OWASP', type: 'Guide', url: 'https://owasp.org/www-project-top-ten/' }
        ]
    };

    // Curate step 4: Portfolio Capstone Aligned with Goal
    const goalTitleMap = {
        'job': 'Interview-Grade Production Capstone',
        'career_switch': 'Industry Transition Capstone Project',
        'upskill': 'Enterprise Scalable System Architecture',
        'portfolio': 'High-Impact Visual & Technical Showcase',
        'freelance': 'Commercial Client MVP & Billing Platform'
    };

    const step4 = {
        step_number: 4,
        title: goalTitleMap[goal] || 'End-to-End Capstone Project',
        duration_weeks: 3,
        focus: 'Portfolio & Career Readiness',
        status: 'pending',
        description: `Bring together ${primaryStrength}, ${primaryWeakness}, and ${secondaryWeakness} into an original, fully deployed application that proves your job readiness.`,
        skills_to_build: [
            `Full-lifecycle product design and deployment`,
            `Writing technical documentation and ADRs`,
            `Technical interview storytelling and code walkthrough`
        ],
        milestones: [
            { id: 'm4_1', text: `Deploy live application with custom domain and continuous deployment`, completed: false },
            { id: 'm4_2', text: `Author comprehensive README with architecture diagram, test instructions, and live demo`, completed: false },
            { id: 'm4_3', text: `Record a 3-minute video walkthrough explaining architectural tradeoffs made`, completed: false }
        ],
        project: {
            title: `Full-Stack SaaS Platform with Supabase`,
            description: `Build a complete application featuring authentication, real-time sync, automated notifications, and payment processing.`
        },
        resources: [
            { title: 'Awesome Software Architecture & System Design', platform: 'GitHub', type: 'Curriculum', url: 'https://github.com/donnemartin/system-design-primer' },
            { title: 'Tech Interview Handbook by Yangshun Tay', platform: 'TechInterviewHandbook', type: 'Guide', url: 'https://www.techinterviewhandbook.org/' }
        ]
    };

    return {
        user_id: profile.user_id,
        skill_profile_id: profile.id || null,
        target_role: profile.goal || 'Software Engineer',
        target_industry: profile.industry || 'Technology',
        overall_gap_summary: gapSummary,
        total_estimated_weeks: 12,
        status: 'in_progress',
        steps: [step1, step2, step3, step4]
    };
}

/**
 * Save or update a skill profile directly in Supabase.
 */
async function saveSkillProfileToSupabase(profileData) {
    if (!window.supabaseClient) {
        throw new Error('Supabase client is not initialized.');
    }

    let user = null;
    if (typeof getSessionWithRetry === 'function') {
        const session = await getSessionWithRetry();
        user = session?.user;
    }
    if (!user) {
        const { data } = await window.supabaseClient.auth.getUser();
        user = data?.user;
    }
    if (!user && profileData.user_id) {
        user = { id: profileData.user_id };
    }
    if (!user) {
        throw new Error('User is not authenticated.');
    }

    const goal = profileData.goal || 'general';
    // Embed goal inside scores._goal to guarantee persistence regardless of DB schema state
    const scoresWithGoal = {
        ...(profileData.scores || {}),
        _goal: goal
    };

    const payload = {
        user_id: user.id,
        goal: goal,
        industry: profileData.industry || 'technology',
        languages: Array.isArray(profileData.languages) ? profileData.languages : [],
        technologies: Array.isArray(profileData.technologies) ? profileData.technologies : [],
        scores: scoresWithGoal,
        total_score: Number(profileData.total_score) || 0,
        completed_at: new Date().toISOString()
    };

    let resultData = null;

    // Primary attempt: Upsert with goal column
    try {
        const { data, error } = await window.supabaseClient
            .from('skill_profiles')
            .upsert(payload, { onConflict: 'user_id' })
            .select()
            .maybeSingle();

        if (error) {
            console.warn('Upsert with goal column failed, retrying without goal column:', error.message);
            const fallbackPayload = { ...payload };
            delete fallbackPayload.goal;
            const retry = await window.supabaseClient
                .from('skill_profiles')
                .upsert(fallbackPayload, { onConflict: 'user_id' })
                .select()
                .maybeSingle();

            if (retry.error) {
                console.error('Base schema upsert also reported error:', retry.error);
                resultData = payload;
            } else {
                resultData = retry.data || payload;
            }
        } else {
            resultData = data || payload;
        }
    } catch (err) {
        console.warn('Falling back to base schema upsert:', err);
        const fallbackPayload = { ...payload };
        delete fallbackPayload.goal;
        try {
            const retry = await window.supabaseClient
                .from('skill_profiles')
                .upsert(fallbackPayload, { onConflict: 'user_id' })
                .select()
                .maybeSingle();
            resultData = retry.data || payload;
        } catch (e) {
            resultData = payload;
        }
    }

    // Always cache locally so profile.html can render instantly without network latency
    localStorage.setItem('mindurr_skill_profile', JSON.stringify(resultData));
    localStorage.setItem('mindurr_has_profile', 'true');

    return resultData;
}

/**
 * Generate and save personalized learning roadmap directly in Supabase.
 */
async function generateAndSaveRoadmapToSupabase(profileData) {
    if (!window.supabaseClient) {
        throw new Error('Supabase client is not initialized.');
    }

    let user = null;
    if (typeof getSessionWithRetry === 'function') {
        const session = await getSessionWithRetry();
        user = session?.user;
    }
    if (!user) {
        const { data } = await window.supabaseClient.auth.getUser();
        user = data?.user;
    }
    if (!user && profileData.user_id) {
        user = { id: profileData.user_id };
    }
    if (!user) {
        throw new Error('User is not authenticated.');
    }

    const roadmapData = generatePersonalizedRoadmap({
        ...profileData,
        user_id: user.id
    });

    const payload = {
        user_id: user.id,
        skill_profile_id: profileData.id || null,
        target_role: roadmapData.target_role,
        target_industry: roadmapData.target_industry,
        overall_gap_summary: roadmapData.overall_gap_summary,
        total_estimated_weeks: roadmapData.total_estimated_weeks,
        status: roadmapData.status,
        steps: roadmapData.steps,
        updated_at: new Date().toISOString()
    };

    try {
        const { data, error } = await window.supabaseClient
            .from('learning_roadmaps')
            .upsert(payload, { onConflict: 'user_id' })
            .select()
            .maybeSingle();

        if (error) {
            console.warn('Supabase learning_roadmaps save warning:', error);
            localStorage.setItem('mindurr_roadmap', JSON.stringify(payload));
            return payload;
        }

        const finalData = data || payload;
        localStorage.setItem('mindurr_roadmap', JSON.stringify(finalData));
        return finalData;
    } catch (err) {
        console.warn('Roadmap save warning:', err);
        localStorage.setItem('mindurr_roadmap', JSON.stringify(payload));
        return payload;
    }
}

/**
 * Fetch existing roadmap for the active authenticated user.
 */
async function fetchUserRoadmap() {
    if (!window.supabaseClient) return null;
    const { data: { user } } = await window.supabaseClient.auth.getUser();
    if (!user) return null;

    const { data, error } = await window.supabaseClient
        .from('learning_roadmaps')
        .select('*')
        .eq('user_id', user.id)
        .maybeSingle();

    if (error) {
        console.warn('Could not fetch learning roadmap from Supabase:', error);
        return null;
    }

    return data;
}

// Export functions to global scope
if (typeof window !== 'undefined') {
    window.generatePersonalizedRoadmap = generatePersonalizedRoadmap;
    window.saveSkillProfileToSupabase = saveSkillProfileToSupabase;
    window.generateAndSaveRoadmapToSupabase = generateAndSaveRoadmapToSupabase;
    window.fetchUserRoadmap = fetchUserRoadmap;
}
