# IIREES "Ask Your Geologist" Chatbot Deployment Guide

This repository contains the backend engine for the IIREES Chatbot, powered by Supabase and Google Gemini.

## 1. Database Setup
1. Go to your **Supabase Dashboard** -> **SQL Editor**.
2. Copy the contents of `supabase_schema.sql` and run it.
   - This enables `pgvector`, creates the necessary tables (`knowledge_base`, `newsletter_subscribers`, `callback_requests`), and sets up the `match_knowledge` function for semantic search.

## 2. Environment Variables
You need to set the following secrets in your Supabase project using the CLI or Dashboard:

```bash
supabase secrets set GEMINI_API_KEY=your_gemini_api_key
```

*Note: `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are automatically available in Edge Functions.*

## 3. Deployment
Deploy the chatbot function using the Supabase CLI:

```bash
supabase functions deploy chatbot --no-verify-jwt
```
*(We use `--no-verify-jwt` if you want to call this from a public website. Ensure you handle security accordingly).*

## 4. Populating the Knowledge Base
To make the "Hybrid" system work, you must add information to the `knowledge_base` table.
The `embedding` column must be populated using Gemini's `text-embedding-004` model (768 dimensions).

**Example Workflow:**
1. Text: "IIREES offers a summer internship in Geology for undergrads."
2. Generate Embedding: Use Gemini API to get the vector for this text.
3. Insert into DB: `INSERT INTO knowledge_base (title, content, embedding) VALUES (...)`

## 5. Frontend Integration
Call your Edge Function endpoint from your website:

```javascript
const response = await fetch('https://<project-ref>.supabase.co/functions/v1/chatbot', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <your-anon-key>'
  },
  body: JSON.stringify({
    message: "What research opportunities do you have?",
    history: [] // Pass previous messages here for conversation context
  })
});
const data = await response.json();
console.log(data.response);
```

## Features Implemented:
- **Hybrid Search:** Combines database knowledge (RAG) with AI reasoning.
- **Lead Generation:** Automatically captures Newsletter signups and Callback requests via AI "Tool Calling".
- **IIREES Persona:** Strictly follows the provided system prompt.
