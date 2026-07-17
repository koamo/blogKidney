# -*- coding: utf-8 -*-
import hashlib
import json
import os
import sys

import markdown
import yaml

from content_rules import PUBLICATION_SCHEMA_VERSION, validate_post


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.dirname(BASE_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")
OUTPUT_FILE = os.path.join(BLOG_DIR, "frontend", "src", "data", "posts.json")
CACHE_FILE = os.path.join(BLOG_DIR, "data", ".posts_cache.json")


def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as post_file:
        hasher.update(post_file.read())
    return hasher.hexdigest()


def parse_post(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as post_file:
        content = post_file.read()
    if not content.startswith("---"):
        raise ValueError("YAML frontmatter is missing")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("YAML frontmatter is not closed")
    metadata = yaml.safe_load(parts[1]) or {}
    if not isinstance(metadata, dict):
        raise ValueError("YAML frontmatter must be an object")
    return metadata, parts[2].strip()


def build_blog_data():
    if not os.path.isdir(POSTS_DIR):
        raise SystemExit(f"[ERROR] Posts directory does not exist: {POSTS_DIR}")

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as cache_file:
                cache = json.load(cache_file)
        except (OSError, ValueError):
            cache = {}

    posts = []
    new_cache = {}
    build_errors = []

    for filename in sorted(name for name in os.listdir(POSTS_DIR) if name.endswith(".md")):
        filepath = os.path.join(POSTS_DIR, filename)
        file_hash = get_file_hash(filepath)
        cached = cache.get(filename, {})

        if cached.get("hash") == file_hash and cached.get("schema_version") == PUBLICATION_SCHEMA_VERSION:
            posts.extend(cached.get("posts", []))
            new_cache[filename] = cached
            continue

        try:
            metadata, markdown_text = parse_post(filepath)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            build_errors.append(f"{filename}: {exc}")
            continue

        status = str(metadata.get("status", "draft")).strip().lower()
        if status != "published":
            print(f"[SKIP] {filename}: status={status or 'missing'}")
            new_cache[filename] = {
                "schema_version": PUBLICATION_SCHEMA_VERSION,
                "hash": file_hash,
                "posts": [],
            }
            continue

        validation_errors = validate_post(metadata, markdown_text)
        if validation_errors:
            build_errors.extend(f"{filename}: {message}" for message in validation_errors)
            continue

        html_content = markdown.markdown(markdown_text, extensions=["fenced_code", "tables", "nl2br"])
        post_data = {
            "title": metadata["title"],
            "date": str(metadata["date"]),
            "description": metadata["description"],
            "tags": metadata["tags"],
            "thumbnail": metadata["thumbnail"],
            "slug": metadata["slug"],
            "lang": "ko",
            "content": html_content,
            "status": status,
            "contentType": metadata.get("content_type", ""),
            "editorialValue": metadata.get("editorial_value", ""),
            "sourceName": metadata.get("source_name", ""),
            "sourceTitle": metadata.get("source_title", ""),
            "sourceUrl": metadata.get("source_url", ""),
            "sourcePublishedAt": str(metadata.get("source_published_at", "")),
            "primarySourceName": metadata.get("primary_source_name", ""),
            "primarySourceTitle": metadata.get("primary_source_title", ""),
            "primarySourceUrl": metadata.get("primary_source_url", ""),
            "reviewedBy": metadata.get("reviewed_by", ""),
            "reviewedAt": str(metadata.get("reviewed_at", "")),
        }
        file_posts = [post_data]
        posts.extend(file_posts)
        new_cache[filename] = {
            "schema_version": PUBLICATION_SCHEMA_VERSION,
            "hash": file_hash,
            "posts": file_posts,
        }
        print(f"[OK] {filename}: {metadata['slug']}")

    if build_errors:
        for message in build_errors:
            print(f"[ERROR] {message}")
        raise SystemExit(f"[FAILED] Publication gate rejected {len(build_errors)} issue(s).")

    posts.sort(key=lambda item: item["date"], reverse=True)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        json.dump(posts, output_file, ensure_ascii=False, indent=2)

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(new_cache, cache_file, ensure_ascii=False, indent=2)

    print(f"[COMPLETE] Built {len(posts)} published post(s): {OUTPUT_FILE}")


if __name__ == "__main__":
    build_blog_data()
