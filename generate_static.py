import os
import json

# Configuration (Mirrored from main.py)
LC_APP_ID = "nFidWX8hhSHJOh7KRWO2a2Yg-gzGzoHsz"
LC_APP_KEY = "eDvvAo2y5GPJkorc0dWkXA7y"
LC_SERVER_URL = "https://nfidwx8h.lc-cn-n1-shared.com"

PROBLEM_ANSWERS = {
    "2025 II-Q1": "468", "2025 II-Q2": "049", "2025 II-Q3": "082", "2025 II-Q4": "106", "2025 II-Q5": "336",
    "2025 II-Q6": "293", "2025 II-Q7": "237", "2025 II-Q8": "610", "2025 II-Q9": "149", "2025 II-Q10": "907",
    "2025 II-Q11": "113", "2025 II-Q12": "019", "2025 II-Q13": "248", "2025 II-Q14": "104", "2025 II-Q15": "240",
    "2025 I-Q1": "070", "2025 I-Q2": "588", "2025 I-Q3": "016", "2025 I-Q4": "117", "2025 I-Q5": "279",
    "2025 I-Q6": "504", "2025 I-Q7": "821", "2025 I-Q8": "077", "2025 I-Q9": "062", "2025 I-Q10": "081",
    "2025 I-Q11": "259", "2025 I-Q12": "510", "2025 I-Q13": "204", "2025 I-Q14": "060", "2025 I-Q15": "735",
    "2024 I-Q1": "204", "2024 I-Q2": "025", "2024 I-Q3": "809", "2024 I-Q4": "116", "2024 I-Q5": "104",
    "2024 I-Q6": "294", "2024 I-Q7": "540", "2024 I-Q8": "197", "2024 I-Q9": "480", "2024 I-Q10": "113",
    "2024 I-Q11": "371", "2024 I-Q12": "385", "2024 I-Q13": "110", "2024 I-Q14": "104", "2024 I-Q15": "721",
    "2024 II-Q1": "073", "2024 II-Q2": "236", "2024 II-Q3": "045", "2024 II-Q4": "033", "2024 II-Q5": "080",
    "2024 II-Q6": "055", "2024 II-Q7": "699", "2024 II-Q8": "127", "2024 II-Q9": "902", "2024 II-Q10": "468",
    "2024 II-Q11": "601", "2024 II-Q12": "023", "2024 II-Q13": "321", "2024 II-Q14": "211", "2024 II-Q15": "315"
}

IMAGE_DIR = "images"

def generate_config():
    # 1. List Images
    if os.path.exists(IMAGE_DIR):
        images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        images.sort()
    else:
        images = []
        print(f"Warning: {IMAGE_DIR} not found.")

    # 2. Create JS Content
    js_content = f"""
// Auto-generated config for static deployment
window.APP_CONFIG = {{
    LC_APP_ID: "{LC_APP_ID}",
    LC_APP_KEY: "{LC_APP_KEY}",
    LC_SERVER_URL: "{LC_SERVER_URL}",
    IMAGES: {json.dumps(images, indent=4)},
    ANSWERS: {json.dumps(PROBLEM_ANSWERS, indent=4)}
}};
"""

    # 3. Write to file
    with open("config.js", "w") as f:
        f.write(js_content)
    
    print(f"Successfully generated config.js with {len(images)} images.")

if __name__ == "__main__":
    generate_config()
