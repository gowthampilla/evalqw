import ollama
import requests
import json

# The unstructured human request
USER_GOAL = "Delete all users who are still on the 'legacy' plan type."

def generate_structured_action():
    print(f"👤 User Request: {USER_GOAL}")
    print("🧠 Llama is synthesizing the Structured Action Package...\n")

    prompt = f"""
    You are an Enterprise AI Database Agent. Convert the user's goal into a strict JSON structured action object.
    Goal: {USER_GOAL}
    
    You MUST return ONLY valid JSON matching this exact structure, with no markdown, no backticks, and no explanations:
    {{
        "intent": "Brief description of the business goal",
        "target_system": "postgres_users_table",
        "requested_write": "The exact SQL query to execute",
        "scope": "single_record" | "mass_update" | "mass_delete",
        "confidence": <float between 0.0 and 1.0 representing your certainty>
    }}
    """

    # Hit the local Llama model
    response = ollama.generate(model='qwen2.5:7b', prompt=prompt)
    raw_output = response['response'].strip()
    
    # Strip markdown if Llama hallucinates code blocks
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:-3].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[3:-3].strip()

    try:
        # Parse the string into a real Python dictionary (The Action Object)
        structured_action = json.loads(raw_output)
        
        print("✅ Structured Action Generated Successfully:")
        print(json.dumps(structured_action, indent=2))
        
        # NOTE: The FastAPI proxy will temporarily reject this because it's expecting 
        # {"agent_name": "...", "sql_query": "..."}. We will fix the proxy next.
        
        # bouncer_resp = requests.post("http://127.0.0.1:8000/v1/proxy", json=structured_action)
        # print(f"\n🛡️ Governor Response: {bouncer_resp.json()}")

    except Exception as e:
        print(f"❌ Execution Blocked: Llama failed to generate valid structured JSON. Error: {e}")
        print(f"Raw output was: {raw_output}")

if __name__ == "__main__":
    generate_structured_action()