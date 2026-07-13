# -*- coding: utf-8 -*-
import argparse
import html
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

import feedparser
import requests
import yaml
from deep_translator import GoogleTranslator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.dirname(BASE_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

FEEDS = [
        {"name": "Medical Xpress Nephrology News", "url": "https://medicalxpress.com/rss-feed/nephrology-news/"},
        {"name": "ScienceDaily Kidney News", "url": "https://www.sciencedaily.com/rss/health_medicine/kidney_disease.xml"},
        {"name": "Nephrology News", "url": "https://www.news-medical.net/tag/feed/Kidney-Disease.aspx"},
    ]
TOPIC_KEYWORDS = ['kidney', 'renal', 'dialysis', 'hemodialysis', 'peritoneal', 'artificial kidney', 'kidney transplant', 'ckd', 'chronic kidney']
MAX_SOURCE_AGE_DAYS = 180
DEFAULT_TAGS = ["신장건강", "만성콩팥병", "환자교육"]
MODEL_NAMES = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
THUMBNAILS = [
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80",
]

BLOCKED_KEYWORDS = [
    "casino", "gambling", "porn", "adult", "torrent", "crack", "piracy",
    "malware", "phishing", "credential theft", "bypass paywall",
]

PROMPT_RULES = """
Write a Korean health-information draft using only the facts in the supplied RSS title and summary.
- Use calm, plain language for patients and families. Do not claim to be a doctor and do not invent clinic stories, patient cases, quotations, statistics, or research details.
- Distinguish laboratory, animal, observational, and clinical evidence only when that stage is stated in the input. Never imply that early research is an approved treatment.
- Do not provide individualized diagnosis, treatment changes, medication doses, fluid targets, or potassium/phosphorus/protein limits.
- Clearly separate what the source reports from general interpretation. If evidence, sample size, follow-up, or applicability is missing, say that it must be checked in the original article.
- Do not copy long phrases from the source. Summarize in original wording.
- Use 2 to 4 natural Markdown H2 sections without numbered templates, hype, miracle language, fear-based wording, or a fabricated first-person persona.
- Do not add a source section, YAML frontmatter, H1, hashtags, or a closing greeting. The application appends source details and a medical notice separately.
""".strip()


def clean_html(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


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


def is_valid_source_url(url):
    parsed = urlparse(url or "")
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def get_entry_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return ""
    return datetime(*parsed[:6]).date().isoformat()


def is_recent_source(source_published_at):
    if not source_published_at:
        return False
    try:
        published = datetime.strptime(source_published_at, "%Y-%m-%d").date()
    except ValueError:
        return False
    age_days = (datetime.now().date() - published).days
    return 0 <= age_days <= MAX_SOURCE_AGE_DAYS


def fetch_feed(feed):
    response = requests.get(
        feed["url"],
        headers={"User-Agent": "KidneyLifeFeedCollector/1.0 (+https://kidney-life.vercel.app)"},
        timeout=30,
    )
    response.raise_for_status()
    return feedparser.parse(response.content)


def load_existing_source_urls():
    urls = set()
    if not os.path.isdir(POSTS_DIR):
        return urls
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8-sig") as post_file:
            content = post_file.read()
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            metadata = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            continue
        source_url = str(metadata.get("source_url", "")).strip()
        if is_valid_source_url(source_url):
            urls.add(source_url)
    return urls


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
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.45,
            "topP": 0.8,
            "maxOutputTokens": 2600,
        },
    }
    for model_name in MODEL_NAMES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        try:
            response = requests.post(
                url,
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            if response.status_code == 200:
                data = response.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "\n".join(part.get("text", "") for part in parts).strip()
                if text:
                    return text, model_name
            print(f"[WARN] Gemini {model_name} failed: HTTP {response.status_code}")
        except Exception as exc:
            print(f"[WARN] Gemini request failed: {exc}")
    return "", ""


def build_prompt(feed_name, title, summary, link):
    return f"""
You are the editor of KidneyLife, a Korean patient-education blog.

Editing rules:
{PROMPT_RULES}

Output format:
TITLE: concise Korean title

Markdown body with natural ## sections.

Input title: {title}
Input summary: {summary}
Source: {feed_name} - {link}
""".strip()


def fallback_post(feed_name, title, summary, link):
    translator = GoogleTranslator(source="auto", target="ko")
    translated_title = translator.translate(title).strip()
    translated_summary = translator.translate(summary[:2500]).strip()
    title_line = translated_title
    body = f"""이 글은 {feed_name}의 공개 RSS 요약에서 확인되는 내용만 옮긴 검토용 초안입니다.

## 원문 요약에서 확인되는 내용
{translated_summary}

## 환자와 가족이 확인할 점
RSS 요약만으로는 연구 단계, 참여자 수, 관찰 기간, 실제 치료 적용 가능성을 모두 확인하기 어렵습니다. 현재 치료나 생활 관리를 바꾸지 말고 아래 원문과 담당 의료진을 통해 확인해야 합니다.
"""
    return title_line, body


def split_title_and_body(text):
    cleaned = re.sub(r"^```(?:markdown|text)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    lines = cleaned.splitlines()
    for index, line in enumerate(lines):
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'"), "\n".join(lines[index + 1:]).strip()
    return "", cleaned.strip()


def is_usable_draft(title, body):
    if not title or not body or len(body) < 350:
        return False
    if re.search(r"(?i)\b(title|yaml|frontmatter):", body):
        return False
    return body.count("## ") >= 2


def append_source_note(body, feed_name, source_title, source_url, source_published_at):
    safe_title = source_title.replace("[", "(").replace("]", ")")
    published_line = f"\n- 원문 게시일: {source_published_at}" if source_published_at else ""
    return f"""{body.strip()}

## 참고 자료

- 원문: [{feed_name} · {safe_title}]({source_url}){published_line}
- 수집 및 확인일: {datetime.now().strftime('%Y-%m-%d')}

원문의 공개 RSS 요약을 바탕으로 작성한 검토용 초안입니다. 이 글은 일반적인 건강 정보이며 진단이나 치료를 대신하지 않습니다. 치료와 식사 조정은 담당 의료진과 상의하세요.
"""


def build_description(body, limit=155):
    plain = re.sub(r"[#*_>`\s]+", " ", body).strip()
    if len(plain) <= limit:
        return plain
    shortened = plain[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,:;")
    return f"{shortened}..."


def write_post(filepath, title, description, slug, thumbnail, body, source, generated_with):
    metadata = {
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "tags": DEFAULT_TAGS,
        "thumbnail": thumbnail,
        "slug": f"auto-{slug}",
        "status": "draft",
        "source_name": source["name"],
        "source_title": source["title"],
        "source_url": source["url"],
        "source_published_at": source["published_at"],
        "collected_at": datetime.now().strftime("%Y-%m-%d"),
        "reviewed_at": "",
        "generated_with": generated_with,
    }
    header = "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n"
    with open(filepath, "w", encoding="utf-8") as post_file:
        post_file.write(header + body.strip() + "\n")


def auto_collect_posts(max_posts=3):
    os.makedirs(POSTS_DIR, exist_ok=True)
    api_key = load_api_key()
    known_source_urls = load_existing_source_urls()
    collected = 0

    for feed in FEEDS:
        if collected >= max_posts:
            break
        try:
            parsed = fetch_feed(feed)
        except Exception as exc:
            print(f"[WARN] Could not read {feed['name']}: {exc}")
            continue
        for entry in parsed.entries[:12]:
            if collected >= max_posts:
                break
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = clean_summary(clean_html(entry.get("summary", entry.get("description", ""))))
            if not is_valid_source_url(link) or link in known_source_urls or not is_quality_source(title, summary):
                continue
            source_published_at = get_entry_date(entry)
            if not is_recent_source(source_published_at):
                continue
            slug = slugify(title)
            filepath = os.path.join(POSTS_DIR, f"auto-{slug}.md")
            if os.path.exists(filepath):
                continue

            generated_title = ""
            generated_body = ""
            generated_with = "translation-fallback"
            if api_key:
                generated, generated_with = call_gemini(api_key, build_prompt(feed["name"], title, summary, link))
                generated_title, generated_body = split_title_and_body(generated)

            if not is_usable_draft(generated_title, generated_body):
                try:
                    generated_title, generated_body = fallback_post(feed["name"], title, summary, link)
                    generated_with = "translation-fallback"
                except Exception as exc:
                    print(f"[WARN] Could not create fallback for {title}: {exc}")
                    continue

            description = build_description(generated_body)
            source = {
                "name": feed["name"],
                "title": title,
                "url": link,
                "published_at": source_published_at,
            }
            generated_body = append_source_note(
                generated_body,
                feed["name"],
                title,
                link,
                source_published_at,
            )
            thumbnail = THUMBNAILS[collected % len(THUMBNAILS)]
            write_post(filepath, generated_title, description, slug, thumbnail, generated_body, source, generated_with)
            known_source_urls.add(link)
            print(f"[OK] wrote draft auto-{slug}.md")
            collected += 1

    print(f"[COMPLETE] collected {collected} draft posts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect kidney news as review-only Markdown drafts.")
    parser.add_argument("--max-posts", type=int, default=3)
    args = parser.parse_args()
    auto_collect_posts(max(0, args.max_posts))
