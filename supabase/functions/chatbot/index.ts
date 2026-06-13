import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { GoogleGenerativeAI } from "https://esm.sh/@google/genai@0.21.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// 1. Initialize API Clients
const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const geminiApiKey = Deno.env.get("GEMINI_API_KEY") ?? "";

const supabase = createClient(supabaseUrl, supabaseServiceKey);
const genAI = new GoogleGenerativeAI(geminiApiKey);

// 2. Define the System Prompt (From User Requirement)
const SYSTEM_PROMPT = `
You are the official AI Assistant for IIREES (Institute for Innovation and Research in Earth and Environmental Sciences).
The chatbot brand name is "Ask Your Geologist".

IMPORTANT:
Do not introduce yourself as "Ask Your Geologist".
Instead introduce yourself as: "👋 Welcome to IIREES! I'm your AI Assistant and research guide."

Your purpose is to assist visitors, students, researchers, educators, professionals, and the general public.
You help users with: Research opportunities, Programs and workshops, Internships, Career opportunities, Events, Field programs, Outreach activities, Earth Science, Geology, Environmental Science, GIS, Remote Sensing, Planetary Science, Space Science, Newsletter subscriptions, Program manager callback requests.

PERSONALITY: Be Friendly, Professional, Helpful, Educational, Encouraging, Conversational. Avoid Robotic responses, Overly technical language, Very short/long answers.

KNOWLEDGE RULES: Always use information available in the knowledge base. Never hallucinate or invent program fees, dates, schedules, contact info, or eligibility.
If info is unavailable, say: "I couldn't find that information in the current IIREES knowledge base. Would you like me to connect you with a Program Manager for further assistance?"

LEAD GENERATION:
- Newsletter: Ask if they want to subscribe to receive updates. If they agree, collect Name, Email, Area of Interest.
- Callback: If they show strong interest (joining, applying, registration, fees), ask if they want a Program Manager to contact them. Collect Full Name, Email, Phone, Area of Interest, Preferred Contact Time.
`;

// 3. Define Tools for Gemini
const tools = [
  {
    functionDeclarations: [
      {
        name: "subscribe_newsletter",
        description: "Subscribes a user to the IIREES newsletter.",
        parameters: {
          type: "OBJECT",
          properties: {
            full_name: { type: "STRING", description: "User's full name" },
            email: { type: "STRING", description: "User's email address" },
            area_of_interest: { type: "STRING", description: "Specific field of interest (e.g., Geology, GIS)" }
          },
          required: ["full_name", "email"]
        }
      },
      {
        name: "request_callback",
        description: "Requests a callback from an IIREES Program Manager.",
        parameters: {
          type: "OBJECT",
          properties: {
            full_name: { type: "STRING", description: "User's full name" },
            email: { type: "STRING", description: "User's email address" },
            phone_number: { type: "STRING", description: "User's phone number" },
            area_of_interest: { type: "STRING", description: "Area of interest" },
            preferred_contact_time: { type: "STRING", description: "Best time to call" }
          },
          required: ["full_name", "email", "phone_number"]
        }
      }
    ]
  }
];

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    const { message, history = [] } = await req.json();

    // A. Generate Embedding for the query (RAG)
    const embeddingModel = genAI.getGenerativeModel({ model: "text-embedding-004" });
    const embResp = await embeddingModel.embedContent(message);
    const queryEmbedding = embResp.embedding.values;

    // B. Search Knowledge Base in Supabase
    const { data: knowledge, error: searchError } = await supabase.rpc("match_knowledge", {
      query_embedding: queryEmbedding,
      match_threshold: 0.5, // Adjust as needed
      match_count: 3
    });

    if (searchError) throw searchError;

    const context = knowledge?.map((k: any) => \`[\${k.title}]: \${k.content}\`).join("\n\n") || "No specific knowledge found.";

    // C. Call Gemini with System Prompt, Context, and Tools
    const model = genAI.getGenerativeModel({ 
      model: "gemini-1.5-flash",
      systemInstruction: SYSTEM_PROMPT,
      tools: tools
    });

    const chat = model.startChat({
      history: history.map((h: any) => ({
        role: h.role === "user" ? "user" : "model",
        parts: [{ text: h.content }]
      })),
    });

    // Provide the retrieved context as a hidden message or part of the user input
    const promptWithContext = \`CONTEXT FROM KNOWLEDGE BASE:\\n\${context}\\n\\nUSER MESSAGE: \${message}\`;

    let result = await chat.sendMessage(promptWithContext);
    let responseText = result.response.text();

    // D. Handle Tool Calls (Function Calling)
    const call = result.response.functionCalls()?.[0];
    if (call) {
      if (call.name === "subscribe_newsletter") {
        const { error } = await supabase.from("newsletter_subscribers").insert(call.args);
        if (error) console.error("Newsletter Error:", error);
        
        result = await chat.sendMessage([{
          functionResponse: {
            name: "subscribe_newsletter",
            response: { content: error ? "Error saving subscription." : "Newsletter subscription request has been submitted." }
          }
        }]);
      } else if (call.name === "request_callback") {
        const { error } = await supabase.from("callback_requests").insert(call.args);
        if (error) console.error("Callback Error:", error);

        result = await chat.sendMessage([{
          functionResponse: {
            name: "request_callback",
            response: { content: error ? "Error saving callback request." : "Your callback request has been submitted. A Program Manager will contact you soon." }
          }
        }]);
      }
      responseText = result.response.text();
    }

    return new Response(JSON.stringify({ response: responseText }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error(error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
