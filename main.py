import os
import json
import base64
import random
import requests
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image

app = FastAPI()

# --- Configuration ---
# Gemini Configuration
GEMINI_API_KEY = "AIzaSyDcbaMbFXUkr_XnD-48HGQ4nuFx9YRCo9E"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# LeanCloud Configuration
LC_APP_ID = "nFidWX8hhSHJOh7KRWO2a2Yg-gzGzoHsz"
LC_APP_KEY = "eDvvAo2y5GPJkorc0dWkXA7y"
LC_MASTER_KEY = "atFxMn6yoq5IBGcvLzzPOCKg"
LC_SERVER_URL = "https://nfidwx8h.lc-cn-n1-shared.com"

# Answers Data
PROBLEM_ANSWERS = {
    "2025 II-Q1": "468", "2025 II-Q2": "049", "2025 II-Q3": "082", "2025 II-Q4": "106", "2025 II-Q5": "336",
    "2025 II-Q6": "293", "2025 II-Q7": "237", "2025 II-Q8": "610", "2025 II-Q9": "149", "2025 II-Q10": "907",
    "2025 II-Q11": "113", "2025 II-Q12": "019", "2025 II-Q13": "248", "2025 II-Q14": "104", "2025 II-Q15": "240",
    "2025 I-Q1": "070", "2025 I-Q2": "588", "2025 I-Q3": "016", "2025 I-Q4": "117", "2025 I-Q5": "279",
    "2025 I-Q6": "504", "2025 I-Q7": "821", "2025 I-Q8": "077", "2025 I-Q9": "062", "2025 I-Q10": "081",
    "2025 I-Q11": "259", "2025 I-Q12": "510", "2025 I-Q13": "204", "2025 I-Q14": "060", "2025 I-Q15": "735"
}

IMAGE_FOLDER = "/Users/binli/Desktop/Work/AI Tools/Math Planning/AIME Problem Sorting/images"

class LeanCloudClient:
    def __init__(self):
        self.headers = {
            "X-LC-Id": LC_APP_ID,
            "X-LC-Key": LC_APP_KEY, # Use App Key for general access, Master Key if needed for privileged ops
            "Content-Type": "application/json"
        }
        # Use Master Key for writing if needed, but App Key should suffice if ACL allows. 
        # Given "MasterKey" was provided, we can use it to bypass ACL issues.
        self.master_headers = {
             "X-LC-Id": LC_APP_ID,
             "X-LC-Key": f"{LC_MASTER_KEY},master",
             "Content-Type": "application/json"
        }
        self.base_url = f"{LC_SERVER_URL}/1.1/classes/AIMEProblem"

    def get_problem_by_filename(self, filename: str) -> Optional[Dict]:
        # Query for existing filename
        params = {
            "where": json.dumps({"filename": filename}),
            "limit": 1
        }
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            return results[0] if results else None
        except Exception as e:
            print(f"LeanCloud Get Error: {e}")
            return None

    def get_all_problems(self) -> List[Dict]:
        try:
            # Simple fetch all (limit 1000 default usually 100)
            # For now, just fetching 100 is likely enough for the demo, or loop if needed.
            # Assuming not too many for now.
            response = requests.get(self.base_url, headers=self.headers, params={"limit": 1000})
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"LeanCloud List Error: {e}")
            return []

    def save_problem(self, filename: str, topic: str, text: str):
        try:
            # Check if exists first to update or create
            existing = self.get_problem_by_filename(filename)
            
            data = {
                "filename": filename,
                "topic": topic,
                "text": text
            }
            
            if existing:
                # Update (PUT)
                object_id = existing.get("objectId")
                update_url = f"{self.base_url}/{object_id}"
                response = requests.put(update_url, headers=self.headers, json=data)
            else:
                # Create (POST)
                response = requests.post(self.base_url, headers=self.headers, json=data)
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"LeanCloud Save Error: {e}")
            raise e
            
    def delete_problem_category(self, filename: str):
        # First get the objectId
        problem = self.get_problem_by_filename(filename)
        if not problem:
            return {"status": "not_found"}
            
        object_id = problem.get("objectId")
        delete_url = f"{self.base_url}/{object_id}"
        
        try:
            # Actually DELETE the record
            response = requests.delete(delete_url, headers=self.headers)
            response.raise_for_status()
            return {"status": "deleted"}
        except Exception as e:
            print(f"LeanCloud Delete Error: {e}")
            raise e

lc_client = LeanCloudClient()

# Paths
IMAGE_DIR = "/Users/binli/Desktop/Work/AI Tools/Math Planning/AIME Problem Sorting/images"

# Mount static files
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

@app.get("/api/images")
async def list_images():
    try:
        files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return {"images": sorted(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Returns a map of filename -> topic for all analyzed images."""
    problems = lc_client.get_all_problems()
    status_map = {p["filename"]: p["topic"] for p in problems}
    return status_map

def analyze_with_gemini(img_path: str):
    try:
        # Read image and encode to base64
        with open(img_path, "rb") as image_file:
            # Gemini API expects standard base64 without newlines
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        headers = {
            "Content-Type": "application/json"
        }
        
        prompt = """
        Analyze this AIME math problem image.
        Categorize it into exactly ONE of the following topics: Algebra, Geometry, Number Theory, Combinatorics.
        
        Return ONLY a JSON object with a single key: "topics", which is a list containing exactly one string. Do not add markdown formatting or extra text.
        Example: {"topics": ["Algebra"]}
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_string
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        # Gemini structure: candidates[0].content.parts[0].text
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        data = json.loads(content)
        return data.get("topics", [])
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return []

@app.get("/api/answers")
def get_answers():
    return PROBLEM_ANSWERS

@app.get("/api/config")
def get_config():
    # Minimal config for frontend compatibility
    return {
        "openrouter_keys": [],
        "models": ["gemini-2.5-flash"]
    }

@app.post("/api/analyze/{filename}")
async def analyze_image(filename: str):
    img_path = os.path.join(IMAGE_FOLDER, filename)
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    topics = []
    # Always use Gemini
    topics = analyze_with_gemini(img_path)

    if isinstance(topics, str):
        topics = [topics]
    
    # Enforce single label if model returned multiple
    if len(topics) > 1:
        topics = topics[:1]
    
    # Join topics for storage/display simplicity
    topic_str = ", ".join(topics)
    
    # Save to LeanCloud ONLY if we have valid topics
    if topic_str and topic_str.lower() != "unknown":
        lc_client.save_problem(filename, topic_str, "")
    else:
        # Explicitly return empty string if unknown/empty to signify "Uncategorized"
        topic_str = ""
    
    return {
        "filename": filename,
        "topic": topic_str
    }

class TopicUpdate(BaseModel):
    topic: str

@app.put("/api/category/{filename}")
async def update_category(filename: str, update: TopicUpdate):
    try:
        # Validate topic? Optional but good.
        # For now, just save whatever string.
        lc_client.save_problem(filename, update.topic, "")
        return {"status": "success", "filename": filename, "topic": update.topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/category/{filename}")
async def delete_category(filename: str):
    try:
        lc_client.delete_problem_category(filename)
        return {"status": "success", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
