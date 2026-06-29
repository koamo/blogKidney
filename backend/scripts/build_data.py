# -*- coding: utf-8 -*-
import os
import json
import yaml
import markdown
import hashlib
from datetime import datetime
from deep_translator import GoogleTranslator

# 기본 프로젝트 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 출력물과 캐시 파일 경로
OUTPUT_FILE = os.path.join(BLOG_DIR, "frontend", "src", "data", "posts.json")
CACHE_FILE = os.path.join(BLOG_DIR, "data", ".posts_cache.json")

# 지원 언어 (ko: 한국어, en: 영어, ja: 일본어)
LANGUAGES = ['ko', 'en', 'ja']

def get_file_hash(filepath):
    """파일의 내용 기반 MD5 해시를 구하여 내용 수정 여부를 감지합니다."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def translate_markdown(markdown_text, target_lang):
    """
    마크다운 특수 기호와 코드 블록(```)을 보호하며 번역을 수행합니다.
    """
    if not markdown_text.strip() or target_lang == 'ko':
        return markdown_text
        
    print(f"  [TRANSLATE] 번역 요청 처리 중 (ko -> {target_lang})")
    
    translator = GoogleTranslator(source='ko', target=target_lang)
    paragraphs = markdown_text.split("\n")
    translated_paragraphs = []
    in_code_block = False
    
    for p in paragraphs:
        if p.strip().startswith("```"):
            in_code_block = not in_code_block
            translated_paragraphs.append(p)
            continue
            
        if in_code_block:
            translated_paragraphs.append(p)
            continue
            
        if not p.strip():
            translated_paragraphs.append(p)
            continue
            
        try:
            translated_p = translator.translate(p)
            if translated_p is None:
                translated_p = p
            translated_paragraphs.append(translated_p)
        except Exception as e:
            print(f"  [WARNING] 문단 번역 실패: {e}")
            translated_paragraphs.append(p)
            
    return "\n".join(translated_paragraphs)

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
            print(f"[INFO] 기존 번역 캐시 로드 성공 ({len(cache)}개 파일 캐시됨)")
        except Exception as e:
            print(f"[WARNING] 캐시 파일 로드 실패: {e}")
            cache = {}

    print(f"[INFO] 블로그 정적 포스트 컴파일 및 번역 작업 시작 (경로: {POSTS_DIR})")
    
    markdown_files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    new_cache = {}

    # 모든 마크다운 파일을 순회
    for filename in markdown_files:
        filepath = os.path.join(POSTS_DIR, filename)
        file_hash = get_file_hash(filepath)
        
        # 캐시에 해당 파일이 있고 내용 해시값이 정확하게 같다면 번역 생략하고 캐시 데이터 활용
        if filename in cache and cache[filename].get("hash") == file_hash:
            print(f"[CACHE HIT] '{filename}' 파일 변경 사항 없음. 캐시된 번역 데이터를 사용합니다.")
            posts.extend(cache[filename]["translations"])
            new_cache[filename] = cache[filename]
            continue
            
        # 변경되었거나 새로 수집된 파일은 번역 수행
        print(f"[CACHE MISS] '{filename}' 파일 생성 또는 변경 감지! 번역 및 컴파일을 수행합니다.")
        
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
                print(f"[WARNING] '{filename}' YAML 헤더 파싱 오류: {e}")
                
        orig_title = meta.get("title", os.path.splitext(filename)[0])
        date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
        orig_description = meta.get("description", "")
        tags = meta.get("tags", [])
        thumbnail = meta.get("thumbnail", "")
        slug = meta.get("slug", os.path.splitext(filename)[0])
        
        file_translations = []
        
        for lang in LANGUAGES:
            print(f"[PROCESS] 기사 팽창 중: {filename} -> 언어 코드: [{lang}]")
            
            try:
                if lang == 'ko':
                    title = orig_title
                    description = orig_description
                    translated_tags = tags
                    translated_markdown_body = markdown_text
                else:
                    translator = GoogleTranslator(source='ko', target=lang)
                    title = translator.translate(orig_title)
                    if title is None:
                        title = orig_title
                        
                    description = translator.translate(orig_description)
                    if description is None:
                        description = orig_description
                        
                    translated_tags = []
                    for tag in tags:
                        try:
                            tt = translator.translate(tag)
                            translated_tags.append(tt if tt else tag)
                        except:
                            translated_tags.append(tag)
                    
                    translated_markdown_body = translate_markdown(markdown_text, lang)
                
                html_content = markdown.markdown(
                    translated_markdown_body, 
                    extensions=['fenced_code', 'tables', 'nl2br']
                )
                
                post_data = {
                    "title": title,
                    "date": str(date),
                    "description": description,
                    "tags": translated_tags,
                    "thumbnail": thumbnail,
                    "slug": slug,
                    "lang": lang,
                    "content": html_content
                }
                
                file_translations.append(post_data)
                print(f"  [OK] 컴파일 성공: {slug} [{lang}]")
                
            except Exception as e:
                print(f"  [ERROR] 번역 빌드 실패: {filename} [{lang}]: {e}")
        
        posts.extend(file_translations)
        new_cache[filename] = {
            "hash": file_hash,
            "translations": file_translations
        }
                
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
        
    print(f"\n[COMPLETE] 총 {len(posts)}개의 다국어 기사가 '{OUTPUT_FILE}' 파일로 완전히 컴파일되었습니다!")

if __name__ == "__main__":
    build_blog_data()