# -*- coding: utf-8 -*-
import os
import re
import sys
from datetime import datetime

import feedparser
import requests
from deep_translator import GoogleTranslator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.dirname(BASE_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

FEEDS = [
        {"name": "Medical Xpress Kidney News", "url": "https://medicalxpress.com/rss-feed/kidney-disease-news/"},
        {"name": "ScienceDaily Kidney News", "url": "https://www.sciencedaily.com/rss/health_medicine/kidney_disease.xml"},
        {"name": "Nephrology News", "url": "https://www.news-medical.net/tag/feed/Kidney-Disease.aspx"},
    ]
TOPIC_KEYWORDS = ['kidney', 'renal', 'dialysis', 'hemodialysis', 'peritoneal', 'artificial kidney', 'transplant', 'ckd', 'chronic kidney']
DEFAULT_TAGS = ["신장건강", "만성콩팥병", "환자교육"]
THUMBNAILS = [
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80",
]

BLOCKED_KEYWORDS = [
    "casino", "gambling", "porn", "adult", "torrent", "crack", "piracy",
    "malware", "phishing", "credential theft", "bypass paywall",
]


def clean_html(raw_html):
    if not raw_html:
        return ""
    return re.sub(r"<.*?>", "", raw_html).strip()


def has_blocked_keyword(text):
    lowered = (text or "").lower()
    return any(word in lowered for word in BLOCKED_KEYWORDS)


def has_topic_keyword(text):
    lowered = (text or "").lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in TOPIC_KEYWORDS)


def is_quality_source(title, summary):
    if not title or not summary:
        return False
    if len(summary.strip()) < 80:
        return False
    if has_blocked_keyword(title) or has_blocked_keyword(summary):
        return False
    return has_topic_keyword(f"{title} {summary}")


def clean_summary(summary):
    summary = re.sub(r"\[\.\.\.\]", "", summary or "")
    summary = re.sub(r"\[Read\s+More.*?\]", "", summary, flags=re.IGNORECASE)
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary


def slugify(title):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")
    return "-".join(slug.split("-")[:6]) or f"post-{datetime.now().strftime('%Y%m%d')}"


def load_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    for env_name in [".env", ".env.local"]:
        env_path = os.path.join(BLOG_DIR, env_name)
        if not os.path.exists(env_path):
            continue
        with open(env_path, "r", encoding="utf-8-sig") as env_file:
            for line in env_file:
                if "=" not in line or line.strip().startswith("#"):
                    continue
                name, value = line.split("=", 1)
                if name.strip() == "GEMINI_API_KEY":
                    return value.strip().strip('"').strip("'")
    return ""


def call_gemini(api_key, prompt):
    models = ["gemini-2.5-flash", "gemini-flash-latest"]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.45,
            "topP": 0.8,
            "maxOutputTokens": 2200,
        },
    }
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"[WARN] Gemini {model_name} failed: HTTP {response.status_code}")
        except Exception as exc:
            print(f"[WARN] Gemini request failed: {exc}")
    return ""


def build_prompt(feed_name, title, summary, link):
    return f"""
You are an editor. {promptRules}

Output format:
TITLE: concise Korean title

Markdown body with 2-4 natural ## sections.
End with a source note: "참고한 원문: [{feed_name}]({link})"

Input title: {title}
Input summary: {summary}
Source: {feed_name} - {link}
""".strip()


def fallback_post(feed_name, title, summary, link):
    translator = GoogleTranslator(source="auto", target="ko")
    translated_title = translator.translate(title).strip()
    translated_summary = translator.translate(summary[:2500]).strip()
    title_line = translated_title
    body = f"""이 글은 {feed_name}에 올라온 공개 기사 요약을 바탕으로 핵심만 정리한 메모입니다.

## 핵심 내용
{translated_summary}

## 읽을 때 확인할 점
원문 요약만으로는 세부 수치나 조건을 모두 확인하기 어렵습니다. 실제 의사결정에 사용하기 전에는 원문과 공식 문서를 함께 확인하는 편이 안전합니다.

참고한 원문: [{feed_name}]({link})
"""
    return title_line, body


def split_title_and_body(text):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'"), "\n".join(lines[index + 1:]).strip()
    return "", text.strip()


def write_post(filepath, title, description, slug, thumbnail, body):
    header = f'''---
title: "{title.replace('"', '\"')}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{description.replace('"', '\"')}"
tags: {DEFAULT_TAGS}
thumbnail: "{thumbnail}"
slug: "auto-{slug}"
---

'''
    with open(filepath, "w", encoding="utf-8") as post_file:
        post_file.write(header + body.strip() + "\n")


def auto_collect_posts():
    os.makedirs(POSTS_DIR, exist_ok=True)
    api_key = load_api_key()
    collected = 0
    max_posts = 3

    for feed in FEEDS:
        if collected >= max_posts:
            break
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries[:12]:
            if collected >= max_posts:
                break
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = clean_summary(clean_html(entry.get("summary", entry.get("description", ""))))
            if not is_quality_source(title, summary):
                continue
            slug = slugify(title)
            filepath = os.path.join(POSTS_DIR, f"auto-{slug}.md")
            if os.path.exists(filepath):
                continue

            generated_title = ""
            generated_body = ""
            if api_key:
                generated = call_gemini(api_key, build_prompt(feed["name"], title, summary, link))
                generated_title, generated_body = split_title_and_body(generated)

            if not generated_title or not generated_body:
                generated_title, generated_body = fallback_post(feed["name"], title, summary, link)

            description = generated_body.replace("\n", " ")
            description = re.sub(r"\s+", " ", description)[:145].strip()
            thumbnail = THUMBNAILS[collected % len(THUMBNAILS)]
            write_post(filepath, generated_title, description, slug, thumbnail, generated_body)
            print(f"[OK] wrote auto-{slug}.md")
            collected += 1

    print(f"[COMPLETE] collected {collected} posts")


if __name__ == "__main__":
    auto_collect_posts()
