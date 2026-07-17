# -*- coding: utf-8 -*-
import argparse
import os
import sys
from collections import Counter

import yaml

from content_rules import is_valid_url, validate_post


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.dirname(BASE_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")


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


def audit_posts():
    errors = []
    warnings = []
    source_urls = []
    status_counts = Counter()

    filenames = sorted(name for name in os.listdir(POSTS_DIR) if name.endswith(".md"))
    for filename in filenames:
        filepath = os.path.join(POSTS_DIR, filename)
        try:
            metadata, body = parse_post(filepath)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{filename}: {exc}")
            continue

        status = str(metadata.get("status", "")).strip().lower()
        status_counts[status or "missing"] += 1
        errors.extend(f"{filename}: {message}" for message in validate_post(metadata, body))

        source_url = str(metadata.get("source_url", "")).strip()
        if is_valid_url(source_url):
            source_urls.append((source_url, filename))

        if status == "draft" and metadata.get("reviewed_at"):
            warnings.append(f"{filename}: reviewed_at is set but status is still draft")
        if status == "rejected" and not (metadata.get("review_note") or metadata.get("review_reason")):
            warnings.append(f"{filename}: rejected post has no review reason")

    duplicates = Counter(url for url, _ in source_urls)
    for url, count in duplicates.items():
        if count > 1:
            files = ", ".join(filename for candidate, filename in source_urls if candidate == url)
            errors.append(f"source_url is reused {count} times: {url} ({files})")

    return filenames, status_counts, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Audit medical post metadata and publication quality gates.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    filenames, status_counts, errors, warnings = audit_posts()
    counts = " ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
    print(f"[SUMMARY] files={len(filenames)} {counts}")
    for message in errors:
        print(f"[ERROR] {message}")
    for message in warnings:
        print(f"[WARN] {message}")
    print(f"[COMPLETE] errors={len(errors)} warnings={len(warnings)}")

    if errors or (args.strict and warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
