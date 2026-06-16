# uvicorn main:app --reload --port 8001
import requests
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

def github_headers():
    token = os.getenv("GITHUB_TOKEN")

    if token:
        return {
            "Authorization": f"Bearer {token}"
        }

    return {}
def analyze_repo(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    commits = response.json()

    if not commits:
        return {
        "error": "Repository has no commits"
    }

    latest_commit = commits[0]

    latest_sha = latest_commit["sha"]

    details_url = (
        f"https://api.github.com/repos/{owner}/{repo}/commits/{latest_sha}"
    )

    response = requests.get(
        details_url,
        headers=github_headers(),
        timeout=20
    )
    response.raise_for_status()

    commit_details = response.json()

    diff_text = ""

    for file in commit_details["files"]:

        diff_text += f"\nFILE: {file['filename']}\n"
        diff_text += file.get("patch", "")
        diff_text += "\n\n"

    diff_text = diff_text[:50000]
    prompt = f"""
    You are an experienced QA Architect.

    Analyze the following GitHub code changes.

    Return ONLY valid JSON.

    {{
      "feature": "",
      "change_type": "",
      "risk_level": "",
      "impacted_modules": [],
      "test_areas": [],
      "recommended_test_types": []
    }}

    Code Changes:

    {diff_text}
    """

    result = llm.invoke(prompt)

    content = result.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        return json.loads(content)

    except Exception:
        return {
            "raw_response": result.content
        }