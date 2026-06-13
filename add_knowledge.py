import os
import google.generativeai as genai
from supabase import create_client, Client

# 1. Configuration - Replace with your actual keys or set as environment variables
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_SERVICE_KEY = "YOUR_SUPABASE_SERVICE_ROLE_KEY"

# Initialize Clients
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def add_to_knowledge_base(title, content, category="general"):
    """
    Adds a new piece of information to the IIREES knowledge base with a vector embedding.
    """
    print(f"Adding: {title}...")

    # A. Generate the Embedding using Gemini
    # IMPORTANT: Use 'text-embedding-004' to match the Edge Function logic
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=content,
        task_type="retrieval_document",
        title=title
    )
    embedding = result['embedding']

    # B. Insert into Supabase
    data = {
        "title": title,
        "content": content,
        "category": category,
        "embedding": embedding
    }

    response = supabase.table("knowledge_base").insert(data).execute()
    
    if response.data:
        print(f"Successfully added '{title}' to the knowledge base!")
    else:
        print(f"Error: {response}")

# --- Example Usage ---
if __name__ == "__main__":
    # Example 1: Research Opportunity
    add_to_knowledge_base(
        title="Deep Sea Exploration Program 2026",
        content="IIREES is launching a deep-sea exploration program in the Atlantic. Open to PhD students and post-docs. Applications close Dec 2025. Fee: $500 for equipment.",
        category="research"
    )

    # Example 2: Educational Topic
    add_to_knowledge_base(
        title="What is Remote Sensing?",
        content="Remote sensing is the process of detecting and monitoring the physical characteristics of an area by measuring its reflected and emitted radiation from a distance (typically from satellite or aircraft).",
        category="science"
    )
