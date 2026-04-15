import os
import json
import requests
from datetime import datetime, timedelta

# 配置
TAVILY_API_KEY = "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"

def fetch_news_from_tavily(query, region="global", days=1):
    """从 Tavily 搜索新闻"""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "topic": "news",
        "days": days,
        "max_results": 15  # 抓取稍多一些供后续 AI 筛选
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"搜索失败 [{query}]: {e}")
        return []

def main():
    # 定义搜索矩阵
    search_queries = {
        "international": {
            "finance": "latest global finance market news wall street",
            "technology": "latest global technology breakthrough space computer science",
            "AI": "latest artificial intelligence LLM OpenAI Anthropic research news"
        },
        "china": {
            "finance": "中国 最新 财经 宏观经济 股市 动态",
            "technology": "中国 科技 突破 芯片 半导体 航天 进展",
            "AI": "中国 人工智能 大模型 DeepSeek 百度 阿里 进展"
        }
    }

    raw_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sections": {}
    }

    for region, categories in search_queries.items():
        raw_data["sections"][region] = {}
        for cat, query in categories.items():
            print(f"正在抓取: {region} - {cat}...")
            results = fetch_news_from_tavily(query, region)
            raw_data["sections"][region][cat] = results

    # 保存原始抓取数据供 process_news.py 处理
    with open("data/raw_news.json", "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)
    print("数据抓取完成，保存至 data/raw_news.json")

if __name__ == "__main__":
    main()
