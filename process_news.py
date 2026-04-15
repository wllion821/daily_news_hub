import os
import json
import requests
from datetime import datetime

# MiMo-V2-Omni 配置 - 支持环境变量或默认值
API_KEY = os.environ.get("MIMO_API_KEY", "tp-cihe9g8tdcrsjwqrmm3vtsvi5kmvz7qnhfaypgvxumxp3g4c")
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MODEL_NAME = "mimo-v2-pro"

def call_mimo_analyst(news_items, region, category):
    if not news_items:
        return []
    
    prompt = f"""你是一名专业的战略情报分析师。请分析以下 {region} 地区的 {category} 类新闻，并返回一个 JSON 数组。
每个对象必须包含以下字段：
1. "title": 原始标题。
2. "url": 原始链接。
3. "publish_time": 发布时间。
4. "score": 推荐权重 (0.0 到 10.0 的浮点数)。
5. "stars": 推荐星级 (字符串，例如 "★★★★★")。
6. "insight": AI 战略洞察 (50-100字，要求专业、高密度、有启发性)。

输入数据: {json.dumps(news_items[:5], ensure_ascii=False)}

注意：仅返回纯 JSON 数组，不要包含 Markdown 代码块。"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"MiMo API 调用失败 [{region}-{category}]: {e}")
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "publish_time": item.get("serper_date") or item.get("published_date") or "未知",
                "score": round(item.get("score", 0) * 10, 2),
                "stars": "★★★★★" if item.get("score", 0) > 0.9 else "★★★★☆",
                "insight": "AI 分析暂时不可用，请稍后重试。"
            } for item in news_items[:5]
        ]

def main():
    # 使用相对路径，兼容本地和 GitHub Actions
    workdir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(workdir, "data/raw_news.json")
    output_path = os.path.join(workdir, "data/news.json")
    
    if not os.path.exists(raw_path):
        print(f"Raw news file not found: {raw_path}")
        return
        
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    processed_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "regions": {}
    }
    
    for region, categories in raw_data.get("sections", {}).items():
        processed_data["regions"][region] = {}
        for cat, news_list in categories.items():
            print(f"正在处理: {region} - {cat} (MiMo-V2-Omni)...")
            results = call_mimo_analyst(news_list, region, cat)
            processed_data["regions"][region][cat] = results
                
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
    print(f"处理完成，结果已保存至 {output_path}")

if __name__ == "__main__":
    main()
