import os
import json
import requests
from datetime import datetime

# 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def call_gemini_analyst(news_items, region, category):
    if not GEMINI_API_KEY: return []
    prompt = f"分析以下 {region} {category} 新闻并返回 JSON 列表。要求：翻译标题、给出 0-10 分、生成 5 星字符串 stars、写一段 AI 战略洞察 insight。不要返回 Markdown 标签。输入：{json.dumps(news_items, ensure_ascii=False)}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
    try:
        response = requests.post(f"{API_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        content_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(content_text)
    except: return []

def main():
    if not os.path.exists("data/raw_news.json"): return
    with open("data/raw_news.json", "r", encoding="utf-8") as f: raw_data = json.load(f)
    processed_data = {"update_time": raw_data["update_time"], "regions": {}}
    for region, categories in raw_data["sections"].items():
        processed_data["regions"][region] = {}
        for cat, news_list in categories.items():
            processed_data["regions"][region][cat] = call_gemini_analyst(news_list, region, cat) or news_list[:5]
    with open("data/news.json", "w", encoding="utf-8") as f: json.dump(processed_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": main()
