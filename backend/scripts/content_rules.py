# -*- coding: utf-8 -*-
import re
from datetime import date, datetime
from urllib.parse import urlparse


PUBLICATION_SCHEMA_VERSION = 3
VALID_STATUSES = {"draft", "published", "rejected"}
VALID_CONTENT_TYPES = {"patient-guide", "reviewed-research", "case-study", "reference"}
REQUIRED_FIELDS = ("title", "date", "description", "tags", "thumbnail", "slug", "status")
PUBLICATION_FIELDS = ("content_type", "editorial_value", "reviewed_by", "reviewed_at")
MIN_BODY_CHARS = 1200
MIN_EDITORIAL_VALUE_CHARS = 30


def is_valid_url(value):
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def body_char_count(body):
    return len(re.sub(r"\s+", "", body or ""))


def second_level_heading_count(body):
    return len(re.findall(r"^##\s+\S", body or "", flags=re.MULTILINE))


def has_references_section(body):
    return bool(re.search(r"^##\s+참고 자료\s*$", body or "", flags=re.MULTILINE))


def has_medical_notice(body):
    notice_patterns = (
        r"진단이나 치료를 대신하지",
        r"진단 또는 치료를 대신하지",
        r"담당 의료진과 (?:상의|상담)",
        r"의료진에게 (?:문의|연락)",
    )
    return any(re.search(pattern, body or "") for pattern in notice_patterns)


def is_iso_date(value):
    if isinstance(value, (date, datetime)):
        return True
    try:
        datetime.strptime(str(value or "").strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_post(metadata, body):
    errors = []
    status = str(metadata.get("status", "")).strip().lower()

    missing = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        errors.append(f"missing required metadata: {', '.join(missing)}")

    if status not in VALID_STATUSES:
        errors.append(f"invalid status: '{status or '(empty)'}'")

    source_url = str(metadata.get("source_url", "")).strip()
    primary_source_url = str(metadata.get("primary_source_url", "")).strip()
    if source_url and not is_valid_url(source_url):
        errors.append("source_url must be an absolute http(s) URL")
    if primary_source_url and not is_valid_url(primary_source_url):
        errors.append("primary_source_url must be an absolute http(s) URL")

    if status != "published":
        return errors

    missing_publication = [field for field in PUBLICATION_FIELDS if not metadata.get(field)]
    if missing_publication:
        errors.append(f"published post is missing: {', '.join(missing_publication)}")

    content_type = str(metadata.get("content_type", "")).strip()
    if content_type and content_type not in VALID_CONTENT_TYPES:
        errors.append(f"unsupported content_type: '{content_type}'")

    if content_type == "reviewed-research":
        if not is_valid_url(source_url):
            errors.append("reviewed-research requires a valid source_url")
        if not is_valid_url(primary_source_url):
            errors.append("reviewed-research requires a valid primary_source_url")

    editorial_value = str(metadata.get("editorial_value", "")).strip()
    if editorial_value and len(re.sub(r"\s+", "", editorial_value)) < MIN_EDITORIAL_VALUE_CHARS:
        errors.append(
            f"editorial_value must explain the original contribution in at least {MIN_EDITORIAL_VALUE_CHARS} characters"
        )

    if metadata.get("reviewed_at") and not is_iso_date(metadata.get("reviewed_at")):
        errors.append("reviewed_at must use YYYY-MM-DD")

    count = body_char_count(body)
    if count < MIN_BODY_CHARS:
        errors.append(f"body is too short for publication ({count} < {MIN_BODY_CHARS} non-whitespace characters)")

    if second_level_heading_count(body) < 3:
        errors.append("published post needs at least three H2 sections")

    if not has_references_section(body):
        errors.append("published post needs a '## 참고 자료' section")

    if not has_medical_notice(body):
        errors.append("published post needs a clear medical-information notice or care-team guidance")

    return errors
