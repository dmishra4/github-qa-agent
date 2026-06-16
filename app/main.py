from fastapi import FastAPI
from app.agent import analyze_repo

app = FastAPI()


@app.get("/")
def home():
    return { 
        "message": "GitHub QA Agent Running"
    }


@app.post("/analyze")
def analyze(owner: str, repo: str):

    result = analyze_repo(owner, repo)

    return result