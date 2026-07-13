# -*- coding: utf-8 -*-
import argparse
import os
import re
import sys
from collections import Counter
from urllib.parse import urlparse

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.dirname(BASE_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")
VALID_STATUSES = {"draft", "published", "rejected"}
REQUIRED_FIELDS = ("title", "date", "description", "tags", "thumbnail", "slug")


def parse_post(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as post_file:
        content = post_file.read()
    if not content.startswith("---"):
        raise ValueError("YAML frontmatter가 없습니다.")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("YAML frontmatter 구분자가 닫히지 않았습니다.")
    metadata = yaml.safe_load(parts[1]) or {}
    if not isinstance(metadata, dict):
        raise ValueError("YAML frontmatter가 객체 형식이 아닙니다.")
    return metadata, parts[2].strip()


def is_valid_url(value):
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


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

        status = str(metadata.get("status", "published")).strip().lower()
        status_counts[status] += 1
        if status not in VALID_STATUSES:
            errors.append(f"{filename}: 알 수 없는 status '{status}'")

        missing = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
        if missing:
            errors.append(f"{filename}: 필수 메타데이터 누락 ({', '.join(missing)})")

        source_url = str(metadata.get("source_url", "")).strip()
        if source_url:
            if is_valid_url(source_url):
                source_urls.append((source_url, filename))
            else:
                errors.append(f"{filename}: source_url 형식 오류")

        if status == "published":
            if not source_url:
                warnings.append(f"{filename}: 게시 글에 source_url이 없습니다.")
            if not metadata.get("reviewed_at"):
                warnings.append(f"{filename}: 게시 글에 reviewed_at이 없습니다.")
            if len(re.sub(r"\s+", "", body)) < 700:
                warnings.append(f"{filename}: 본문이 짧아 정보 깊이를 다시 확인해야 합니다.")
            if source_url and "## 참고 자료" not in body:
                warnings.append(f"{filename}: 출처 URL은 있지만 본문 참고 자료 섹션이 없습니다.")
            if not re.search(r"진단이나 치료를 대신하지|(?:의료진|신장내과|임상영양사).{0,24}(?:상의|상담)", body):
                warnings.append(f"{filename}: 의료 정보 면책·상담 안내 문구를 확인해야 합니다.")

        if status == "draft" and metadata.get("reviewed_at"):
            warnings.append(f"{filename}: 검토일이 있지만 아직 draft 상태입니다.")
        if status == "rejected" and not (metadata.get("review_note") or metadata.get("review_reason")):
            warnings.append(f"{filename}: rejected 판정 사유가 없습니다.")

    duplicates = Counter(url for url, _ in source_urls)
    for url, count in duplicates.items():
        if count > 1:
            files = ", ".join(filename for candidate, filename in source_urls if candidate == url)
            errors.append(f"동일 source_url이 {count}번 사용됨: {url} ({files})")

    return filenames, status_counts, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Markdown 게시물 메타데이터와 검토 상태를 점검합니다.")
    parser.add_argument("--strict", action="store_true", help="경고도 실패(exit 1)로 처리합니다.")
    args = parser.parse_args()

    filenames, status_counts, errors, warnings = audit_posts()
    print(f"[SUMMARY] files={len(filenames)} " + " ".join(f"{key}={value}" for key, value in sorted(status_counts.items())))
    for message in errors:
        print(f"[ERROR] {message}")
    for message in warnings:
        print(f"[WARN] {message}")
    print(f"[COMPLETE] errors={len(errors)} warnings={len(warnings)}")

    if errors or (args.strict and warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
