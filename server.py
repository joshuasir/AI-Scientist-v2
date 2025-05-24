from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import subprocess
import json
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["*"] for all origins (not safe in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class IdeaInput(BaseModel):
    Title: str
    Keyword: str
    Abstract: str

@app.post("/submit-idea")
async def submit_idea(idea: IdeaInput):
    # Create filename with current timestamp
    timestamp = int(time.time())
    safe_title = idea.Title.replace(" ", "_")
    filename = f"{safe_title}_{timestamp}"
    md_path = f"ai_scientist/ideas/{filename}.md"
    js_path = f"ai_scientist/ideas/{filename}.json"

    # Ensure the directory exists
    os.makedirs("ai_scientist/ideas", exist_ok=True)

    # Write the Markdown file
    with open(md_path, "w") as f:
        f.write(f"# Title: {idea.Title}\n\n")
        f.write(f"## Keywords\n{idea.Keyword}\n\n")
        f.write(f"## TL;DR\n{idea.Abstract}\n\n")
        f.write(f"## Abstract\n{idea.Abstract}\n")

    # Run the ideation script
    try:
        subprocess.run([
            "python3",
            "ai_scientist/perform_ideation_temp_free.py",
            "--workshop-file", md_path,
            "--model", "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            "--max-num-generations", "2",
            "--num-reflections", "5"
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {str(e)}")

    # Wait for the .js output file to be written (timeout after 15s)
    for _ in range(60):
        if os.path.exists(js_path):
            break
        time.sleep(0.5)
    else:
        raise HTTPException(status_code=500, detail="Output file was not generated in time.")

    # Read and parse the output file
    try:
        with open(js_path, "r") as f:
            ideas = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read output file: {str(e)}")

    return ideas
