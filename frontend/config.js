// Mindurr.ai shared frontend config + Supabase auth helpers

// Backend API base URL (kept for optional local server usage, but frontend works 100% directly with Supabase)
const API_BASE = window.MINDURR_API_BASE || "http://127.0.0.1:8000";

const SUPABASE_URL = "https://xrxstghlyyergkuvqlaw.supabase.co";
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyeHN0Z2hseXllcmdrdXZxbGF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg4Njg1NTUsImV4cCI6MjEwNDQ0NDU1NX0.4bRp8FFRqPoM-Sos8InAdUsXEcQFnPJJB87_6OunPsQ'
// Mindurr.ai shared frontend config + Supabase auth helpers
// Safely initialize client without throwing a re-declaration error
let supabaseClient = null;
try {
    if (window.supabase && typeof window.supabase.createClient === 'function') {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
            auth: {
                storage: window.localStorage,
                persistSession: true,
                autoRefreshToken: true,
                detectSessionInUrl: true
            }
        });
        window.supabaseClient = supabaseClient;
    }
} catch (e) {
    console.error("Failed to initialize Supabase client:", e);
}

if (!supabaseClient && typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
        const el = document.createElement('div');
        el.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#ba1a1a;color:#fff;padding:12px 16px;font:600 14px/1.4 Inter,sans-serif;';
        el.textContent = 'Mindurr: Supabase client failed to load. Check browser console.';
        document.body.appendChild(el);
    });
}

function saveSessionLocally(session, role) {
    if (!session) return;
    try {
        if (session.access_token) localStorage.setItem('mindurr_token', session.access_token);
        if (session.user) {
            localStorage.setItem('mindurr_user', JSON.stringify(session.user));
            const userRole = session.user.user_metadata?.role || role;
            if (userRole) localStorage.setItem('mindurr_role', userRole);
        }
        localStorage.setItem('mindurr_session', JSON.stringify(session));
    } catch (e) {
        console.warn('saveSessionLocally warning:', e);
    }
}

function clearLocalSession() {
    try {
        localStorage.removeItem('mindurr_token');
        localStorage.removeItem('mindurr_user');
        localStorage.removeItem('mindurr_session');
        localStorage.removeItem('mindurr_role');
        localStorage.removeItem('mindurr_has_profile');
    } catch (e) {
        console.warn('clearLocalSession warning:', e);
    }
}

async function getSessionWithRetry(maxRetries = 3, delayMs = 120) {
    if (!supabaseClient) return null;
    for (let i = 0; i < maxRetries; i++) {
        try {
            const { data } = await supabaseClient.auth.getSession();
            if (data?.session?.user) {
                saveSessionLocally(data.session);
                return data.session;
            }
        } catch (e) {
            console.warn('getSession error:', e);
        }
        if (i < maxRetries - 1) {
            await new Promise(r => setTimeout(r, delayMs));
        }
    }
    return null;
}

async function getAuthenticatedProfile() {
    const session = await getSessionWithRetry();
    if (!session) {
        const urlRole = localStorage.getItem('mindurr_role') || (window.location.pathname.includes('recruiter') ? 'recruiter' : '');
        const target = urlRole ? `login_register.html?role=${encodeURIComponent(urlRole)}` : 'login_register.html';
        window.location.href = target;
        return null;
    }
    const role = session.user?.user_metadata?.role || localStorage.getItem('mindurr_role') || 'student';
    return { session, user: session.user, role };
}

async function routeUserPostLogin(user, fallbackRole) {
    if (!user) {
        user = await (await getSessionWithRetry())?.user;
        if (!user) {
            window.location.href = 'login_register.html';
            return;
        }
    }

    let urlRole = null;
    try {
        const urlParams = new URLSearchParams(window.location.search);
        urlRole = urlParams.get('role');
    } catch(e) {}

    let role = user.user_metadata?.role || fallbackRole || urlRole || localStorage.getItem('mindurr_role') || 'student';
    localStorage.setItem('mindurr_role', role);

    if (role === 'recruiter') {
        window.location.href = 'recruiter_dashboard.html';
        return;
    }

    // Check if profile exists in localStorage or Supabase
    if (localStorage.getItem('mindurr_has_profile') === 'true') {
        window.location.href = 'profile.html';
        return;
    }

    try {
        if (supabaseClient && user.id) {
            const { data: skillProfile } = await supabaseClient
                .from('skill_profiles')
                .select('id, total_score')
                .eq('user_id', user.id)
                .maybeSingle();

            if (skillProfile && skillProfile.total_score !== null) {
                localStorage.setItem('mindurr_has_profile', 'true');
                window.location.href = 'profile.html';
                return;
            }
        }
    } catch (e) {
        console.warn('Could not check skill profile:', e);
    }

    window.location.href = 'assessment.html';
}

async function logout() {
    clearLocalSession();
    if (supabaseClient) {
        try { await supabaseClient.auth.signOut(); } catch (e) {}
    }
    window.location.href = 'login_register.html?action=logout';
}