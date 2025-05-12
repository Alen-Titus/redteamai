import os
import requests
import json
import re

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def fetch_exploitdb_data(exploitdb_id):
    # Try to read from local exploitdb clone
    local_base_path = r"C:\Users\alent\Desktop\db\exploitdb\exploits"
    for root, _, files in os.walk(local_base_path):
        for file in files:
            if exploitdb_id in file:
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
    # Fallback to online if not found locally
    url = f"https://www.exploit-db.com/raw/{exploitdb_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch data for ID {exploitdb_id}. HTTP Status: {response.status_code}")

def get_ollama_models():
    try:
        output = os.popen("ollama list").read()
        model_lines = [line.strip() for line in output.strip().split('\n')[1:] if line.strip()]
        models = [line.split()[0] for line in model_lines]
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def select_ollama_model(models):
    print("\nAvailable Ollama models:")
    for idx, model in enumerate(models, 1):
        print(f"  {idx}. {model}")
    user_input = input("\nEnter the number or name of the model to use (press Enter for default [1]): ").strip()
    if user_input == "":
        return models[0]
    elif user_input.isdigit() and 1 <= int(user_input) <= len(models):
        return models[int(user_input) - 1]
    elif user_input in models:
        return user_input
    else:
        print("Invalid selection. Using default.")
        return models[0]

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def send_to_ollama(prompt, model):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"Error sending to Ollama: {e}"

def build_prompt(exploit_description):
    return f"""
You are an advanced red team operator creating weaponized PowerShell exploit scripts for automated remote execution.

Context:
- You are targeting a vulnerable Windows machine.
- The goal is to fully exploit the described vulnerability using PowerShell only.
- You already have valid credentials to authenticate remotely.

Requirements:
1. Carefully analyze the following exploit or CVE description.
2. Generate a **fully functional PowerShell script** that:
   - Connects remotely to the target using provided credentials:
     - Target IP: 192.168.1.46
     - Username: alent
     - Password: penguin123
   - Exploits the vulnerability effectively and cleanly.
   - Drops payloads, invokes APIs, or manipulates services/registry as needed.
   - Requires **no manual editing** — it should be copy-paste ready.
3. Include all required:
   - Imports (`Add-Type`, `System.Net`, `Invoke-WebRequest`, etc.)
   - File/payload handling (e.g., download/upload encoded payloads)
   - Execution logic (e.g., privilege escalation, persistence, exfiltration)
4. Ensure:
   - Code is stealthy and minimal where possible.
   - Actions are commented clearly to explain each step.
   - Error handling is present to avoid crashing on execution.

Output Format:
- First: a **short summary** of how the exploit works.
- Then: a **clean, fully usable PowerShell script**, formatted as a code block.
- Do **not** include disclaimers, markdown annotations, or extra text.

Here is the vulnerability description to work with:
\"\"\"{exploit_description}\"\"\"
"""

def generate_exploit_script(exploitdb_id, model):
    print(f"\nFetching Exploit-DB data for ID {exploitdb_id}...")
    cve_description = fetch_exploitdb_data(exploitdb_id)
    print("Data fetched.\n")

    prompt = build_prompt(cve_description)
    print(f"Sending prompt to Ollama using model: {model}...\n")

    response = send_to_ollama(prompt, model)

    print("\n\n--- GENERATED OUTPUT ---\n")
    print(response)

    safe_model = sanitize_filename(model)
    filename = f"exploit_{exploitdb_id}_{safe_model}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"\nSaved to {filename}")

if __name__ == "__main__":
    exploitdb_id = input("Enter Exploit-DB ID (e.g., 51066): ").strip()
    available_models = get_ollama_models()
    if not available_models:
        print("No Ollama models available.")
        exit(1)
    model_name = select_ollama_model(available_models)
    generate_exploit_script(exploitdb_id, model=model_name)
