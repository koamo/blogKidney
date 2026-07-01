# -*- coding: utf-8 -*-
import os
import json
import yaml
import markdown
import hashlib
from datetime import datetime

# 기본 프로젝트 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 출력물과 캐시 파일 경로
OUTPUT_FILE = os.path.join(BLOG_DIR, "frontend", "src", "data", "posts.json")
CACHE_FILE = os.path.join(BLOG_DIR, "data", ".posts_cache.json")

def get_file_hash(filepath):
    """파일의 내용 기반 MD5 해시를 구하여 내용 수정 여부를 감지합니다."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def build_blog_data():
    posts = []
    
    if not os.path.exists(POSTS_DIR):
        print(f"[ERROR] 포스트 디렉토리를 찾을 수 없습니다: '{POSTS_DIR}'")
        return
        
    # 캐시 데이터 불러오기
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as cf:
                cache = json.load(cf)
            print(f"[INFO] 기존 캐시 로드 성공 ({len(cache)}개 파일 캐시됨)")
        except Exception as e:
            print(f"[WARNING] 캐시 파일 로드 실패: {e}")
            cache = {}

    print(f"[INFO] 블로그 정적 포스트 컴파일 작업 시작 (한국어 전용, 경로: {POSTS_DIR})")
    
    markdown_files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    new_cache = {}

    # 모든 마크다운 파일을 순회
    for filename in markdown_files:
        filepath = os.path.join(POSTS_DIR, filename)
        file_hash = get_file_hash(filepath)
        
        # 캐시에 해당 파일이 있고 내용 해시값이 정확하게 같다면 컴파일 생략
        if filename in cache and cache[filename].get("hash") == file_hash:
            print(f"[CACHE HIT] '{filename}' 변경 없음. 캐시 데이터 사용.")
            posts.extend(cache[filename]["posts"])
            new_cache[filename] = cache[filename]
            continue
            
        print(f"[COMPILE] '{filename}' 신규/변경 감지. 컴파일 수행.")
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                markdown_text = parts[2]
            else:
                frontmatter_text = ""
                markdown_text = content
        else:
            frontmatter_text = ""
            markdown_text = content
            
        meta = {}
        if frontmatter_text.strip():
            try:
                meta = yaml.safe_load(frontmatter_text)
            except Exception as e:
                print(f"[WARNING] '{filename}' YAML 파싱 오류: {e}")
                
        title = meta.get("title", os.path.splitext(filename)[0])
        date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
        description = meta.get("description", "")
        tags = meta.get("tags", [])
        thumbnail = meta.get("thumbnail", "")
        slug = meta.get("slug", os.path.splitext(filename)[0])
        
        try:
            html_content = markdown.markdown(
                markdown_text, 
                extensions=['fenced_code', 'tables', 'nl2br']
            )
            
            post_data = {
                "title": title,
                "date": str(date),
                "description": description,
                "tags": tags,
                "thumbnail": thumbnail,
                "slug": slug,
                "lang": "ko",
                "content": html_content
            }
            
            file_posts = [post_data]
            posts.extend(file_posts)
            new_cache[filename] = {
                "hash": file_hash,
                "posts": file_posts
            }
            print(f"  [OK] 컴파일 성공: {slug}")
            
        except Exception as e:
            print(f"  [ERROR] 컴파일 실패: {filename}: {e}")
                
    # 날짜 기준으로 내림차순 정렬
    posts.sort(key=lambda x: x["date"], reverse=True)
    
    # JSON 파일 최종 출력
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    # 캐시 파일 갱신
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as cf:
        json.dump(new_cache, cf, ensure_ascii=False, indent=2)
        
    print(f"\n[COMPLETE] 총 {len(posts)}개의 기사가 '{OUTPUT_FILE}' 파일로 컴파일되었습니다!")

if __name__ == "__main__":
    build_blog_data()