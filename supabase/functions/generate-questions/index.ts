import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { technologies, industry } = await req.json();

    if (!technologies || !Array.isArray(technologies) || technologies.length === 0) {
      return new Response(
        JSON.stringify({ error: "technologies array is required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY");
    if (!GEMINI_API_KEY) {
      return new Response(
        JSON.stringify({ error: "GEMINI_API_KEY not configured" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const techList = technologies.join(", ");
    const prompt = `You are a technical assessment engine. Generate exactly 30 multiple-choice questions to assess skill level for: ${techList}. Industry context: ${industry}. Return ONLY a valid JSON array, no markdown, no explanation. Each object must have: "q" (string question), "options" (array of exactly 4 strings), "answer" (0-3 index of correct answer), "technology" (which tech from the list this question covers). Mix questions evenly across all selected technologies. Vary difficulty: some beginner, some intermediate, some advanced. Make wrong answers plausible but clearly incorrect to someone who knows the topic.`;

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }),
      }
    );

    if (!response.ok) {
      const errText = await response.text();
      return new Response(
        JSON.stringify({ error: `Gemini API error: ${response.status}`, details: errText }),
        { status: 502, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    let text = data.candidates[0].content.parts[0].text;

    // Strip markdown fences if present
    text = text.replace(/^```json\s*/i, "").replace(/\s*```$/i, "").trim();

    const questions = JSON.parse(text);

    return new Response(
      JSON.stringify({ questions }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (e) {
    return new Response(
      JSON.stringify({ error: e.message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
