# -*- coding: utf-8 -*-
import os
import re
import json
import urllib.parse
import feedparser
import requests
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# 기본 디렉토리 설정 (blog_kidney 기준)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 디렉토리
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 디렉토리
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 스팸/광고성 키워드 필터 (해당 키워드가 들어간 글은 수집 차단)
BLACKLIST_KEYWORDS = [
    'hack', 'crack', 'casino', 'gambling', 'illegal', 'adult', 'porn', 'torrent', 'bypass',
    '해킹', '경마', '릴게임', '도박', '카지노', '불법', '성인물', '우회', '판매'
]

# 포스트의 기본 고화질 대표 썸네일 이미지 목록 (Unsplash)
UNSPLASH_THUMBNAILS = [
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80", # 요가 및 명상
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80", # 신선한 채소와 건강 식단
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80", # 마음 챙김과 명상
    "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&w=800&q=80", # 치료와 혈액 투석
    "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=800&q=80"  # 맑은 자연과 숲
]

def clean_html(raw_html):
    """HTML 태그 제거"""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def check_blacklist(text):
    """블랙리스트 기반 글 필터링"""
    if not text:
        return False
    text_lower = text.lower()
    for word in BLACKLIST_KEYWORDS:
        if word in text_lower:
            return True
    return False

def validate_content(title, summary):
    """
    수집 대상 기사의 최소 품질 기준을 검증합니다.
    본문이 80자 미만이거나 단순 메타 텍스트가 가득한 경우 수집을 건너뜁니다.
    """
    if not summary or not title:
        return False
    if len(summary.strip()) < 80:
        return False
    
    # 단순 메타 데이터 위주의 기사 차단
    meta_patterns = ['category:', 'news date:', 'last edit review:', '수집일시', '작성자']
    summary_lower = summary.lower()
    for pattern in meta_patterns:
        if pattern in summary_lower:
            return False
            
    return True

def clean_truncated_summary(summary):
    """
    RSS 피드의 특성상 생기는 불완전한 문장 끝맺음 [...] 및 [Read More] 기호를 정교하게 제거하고
    온전한 문장 형태로 요약본을 마감합니다.
    """
    if not summary:
        return ""
        
    summary_clean = re.sub(r'\[\.\.\.\]', '', summary)
    summary_clean = re.sub(r'\[Read\s+More.*?\]', '', summary_clean, flags=re.IGNORECASE)
    summary_clean = re.sub(r'\.\s*\.\s*\.', '', summary_clean)
    
    summary_clean = summary_clean.strip()
    
    sentences = re.split(r'(\.|\!|\?)\s+', summary_clean)
    if len(sentences) > 2:
        reconstructed = []
        for i in range(0, len(sentences)-1, 2):
            reconstructed.append(sentences[i] + sentences[i+1])
        
        last_item = sentences[-1].strip()
        if last_item and not any(last_item.endswith(p) for p in ['.', '!', '?']):
            summary_clean = " ".join(reconstructed)
        else:
            if last_item:
                reconstructed.append(last_item)
            summary_clean = " ".join(reconstructed)
            
    summary_clean = summary_clean.strip()
    if summary_clean and not any(summary_clean.endswith(p) for p in ['.', '!', '?']):
        summary_clean += "."
        
    return summary_clean

def verify_and_refine_translation(text):
    """
    [개선 기능] 기계 번역된 제목과 본문 내에서 발생하기 쉬운 
    치명적인 번역 오류나 의학적 비문을 도메인에 맞는 바른 어휘로 강제 정제합니다.
    """
    if not text:
        return text
        
    # 신장(Kidney) 및 신부전 건강 블로그 특화 번역 교정 딕셔너리
    replacements = {
        "소년에게 소식": "소아 이식 소식",
        "소년에게 연구 결과": "소아 장기 이식 연구 결과",
        "소년에게 생태계": "신장 건강 생태계",
        "소년에게 보호": "신장 보호",
        "소년에게 기능": "신장 기능",
        "소년에게 질환": "신장 질환",
        "소년에게 환우": "신장 질환 환우",
        "소년에게 연구": "신장 관련 연구",
        "소년에게 생태계에서": "신장 관리 체계에서",
        "11세 소년에게 두 개의 새로운 장기가 필요했고": "11세 소아에게 두 개의 새로운 장기가 필요했고",
        "소년에게": "신장 기능"  # 단독 발생 시 안전 대체어
    }
    
    refined_text = text
    for target, replacement in replacements.items():
        refined_text = refined_text.replace(target, replacement)
        
    return refined_text

def extract_main_subject(title):
    """
    [개선 기능] 제목에서 주제 키워드(예: 신장, 영양, 이식 등)를 발라내고,
    조사 결합 및 오역을 정교하게 방어하여 정제된 키워드를 추출합니다.
    """
    if not title:
        return "신장건강"
        
    subject = "만성콩팥병"
    
    # 1. 대괄호 안의 문구 1순위
    brackets = re.findall(r'\[(.*?)\]', title)
    if brackets:
        subject = brackets[0]
    # 2. 콜론 앞의 문구 2순위
    elif ":" in title:
        part = title.split(":", 1)[0].strip()
        if len(part) < 30:
            subject = part
    # 3. 영어 대문자로 시작하는 고유명사나 명사구 3순위
    else:
        words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', title)
        if words:
            filtered = [w for w in words if w.lower() not in ['a', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'by', 'for', 'with', 'new', 'how', 'why', 'what', 'study']]
            if filtered:
                subject = " ".join(filtered[:2])
        # 4. 순수 한글 명사 4순위
        else:
            korean_words = re.findall(r'\b[가-힣]{2,8}\b', title)
            if korean_words:
                subject = korean_words[0]
            else:
                subject = "만성콩팥병"
                
    # --- [개선 로직 1] 끝부분에 결합된 한국어 조사 분리 및 정제 ---
    josa_patterns = [
        r'에게$', r'은$', r'는$', r'이$', r'가$', r'을$', r'를$', 
        r'과$', r'와$', r'의$', r'로$', r'으로$', r'에$', r'에서$', 
        r'조차$', r'마저$', r'부터$', r'까지$'
    ]
    for pattern in josa_patterns:
        subject = re.sub(pattern, '', subject)
        
    # --- [개선 로직 2] 핵심 명사 오역 치환 매핑 테이블 적용 ---
    translation_fixes = {
        "소년": "소아 장기 이식",
        "소녀": "소아 장기 이식",
        "어린이": "소아 장기 이식",
        "11세": "소아 장기 이식",
        "kidney": "신장 건강",
        "Kidney": "신장 건강",
        "kidneys": "신장",
        "renal": "신장",
        "Renal": "신장",
        "nephron": "네프론",
        "nephrology": "신장학"
    }
    
    subject = subject.strip()
    if subject in translation_fixes:
        subject = translation_fixes[subject]
        
    if len(subject) < 2:
        return "신장건강"
        
    return subject

def generate_dynamic_free_content(feed_name, link, translated_title, translated_body):
    """
    무료 모드용 정적 템플릿 콘텐츠 조립기.
    주제 키워드를 기반으로 매우 전문적이고 알찬 신장 4대 수칙 건강 컬럼을 구성합니다.
    """
    subject = extract_main_subject(translated_title)
    
    # 콩팥 보호 4대 식사 수칙 가이드 고정 세션
    diet_guidelines = f"""만성 콩팥병 환우분들은 질환의 단계(1~5단계)에 관계없이 잔여 신장 기능을 철저히 보존하기 위해 식이조절에 정성을 다하셔야 합니다. 콩팥을 지키기 위한 **'신장 4대 식사 원칙'**을 일상에서 실천해 보세요.

1. **저염 (Low Sodium) - 체액량 조절 및 사구체 보호**
   * **이유**: 염분(나트륨) 섭취가 늘어나면 체액량이 증가하고 혈압이 상승하여, 신장의 핵심 여과 장치인 사구체에 물리적 타격과 손상을 줍니다.
   * **실천 요령**: 소금, 간장, 된장 등의 양념류 사용량을 평소의 절반 이하로 줄이십시오. 국물 요리는 건더기 위주로 섭취하고 햄, 인스턴트, 가공식품 등 염분이 고도로 축적된 식품은 식탁에서 차단해야 합니다.

2. **저칼륨 (Low Potassium) - 심장 부정맥 예방**
   * **이유**: 신장의 칼륨 배설 능력이 줄어들면 고칼륨혈증이 생겨, 심장에 심각한 마비나 급성 부정맥 등의 치명적인 위협을 줄 수 있습니다.
   * **실천 요령**: 칼륨은 물에 잘 녹는 성질이 있으므로, **채소류는 얇게 썰어 따뜻한 물에 최소 2시간 이상 담가두거나 끓는 물에 푹 데친 뒤** 섭취하는 것이 좋습니다. 바나나, 토마토, 참외, 아보카도 같은 고칼륨 과일의 섭취는 극도로 삼가시기 바랍니다.

3. **저인 (Low Phosphorus) - 뼈 건강 보존과 석회화 예방**
   * **이유**: 혈액 내 인 수치가 과도하게 상승하면 칼슘이 뼈에서 빠져나가 뼈가 골다공증처럼 약해지고 부러지기 쉬워지며, 칼슘이 혈관 벽에 달라붙어 동맥경화 등 심혈관계 합병증이 생깁니다.
   * **실천 요령**: 첨가물 속의 인은 가공식품(탄산음료, 햄 등)을 통해 거의 100% 몸에 흡수되므로 철저히 금해야 하며, 치즈나 요거트 같은 유제품, 견과류 및 잡곡의 섭취를 적절히 조율하고 백미 중심의 신선한 건강 식사 구조를 잡아야 합니다.

4. **저단백 (Low Protein) - 요독 축적 배설 완화 및 잔여 사구체 보호**
   * **이유**: 단백질이 몸 안에서 쪼개지며 생겨난 질소 노폐물(요독)은 신장을 통해 나가야 합니다. 단백질을 과도하게 많이 먹으면 요독이 혈액 속에 정체되어 신장에 여과 과부하가 걸려 신장이 급격히 손상됩니다.
   * **실천 요령**: 본인의 신장 기능 단계에 알맞은 하루 단백질 권장량을 임상영양사나 주치의와 의논하여 섭취해야 하며, 단백질 섭취가 필요할 때는 양질의 단백질(달걀 흰자, 살코기 등)을 소량씩만 영양 균형에 맞추어 식사 계획을 짜는 것이 필요합니다."""

    # 조립용 기사 분석 인사이트 세션 템플릿
    insight_templates = [
        f"""이번에 공개된 **{subject}** 소식은 만성 콩팥병 환우분들의 전신 건강 관리 및 치료 여정에서 매우 강력한 교훈을 전달하고 있습니다. 신장 기능을 장기적으로 보존하고 사구체 압력을 다스리기 위한 실질적인 영양 조언은 아래와 같습니다:
* **전신 면역과 안전성 확보**: 장기 이식 수술 사례나 신장 연구 결과가 말해주듯, 만성 질환에서 몸의 항상성을 유지하는 능력은 매우 귀중합니다. 일상생활 속에서 스트레스를 피하고 충분한 숙면을 취해 안정된 신체 균형을 지켜야 합니다.
* **영양 균형을 통한 사구체 여과 과부하 예방**: 콩팥은 체내의 각종 대사 노폐물을 청소하는 소중한 장기입니다. 규칙적인 소량 식사와 정밀한 식이 원칙 준수만이 무리한 여과 과부하를 막아 장기 수명을 연장하는 핵심 비결입니다.""",

        f"""새롭게 조명된 **{subject}** 연구 소식과 극복 사례는 만성 신부전 환우들이 기나긴 치료 경로에서 마주하는 스트레스에 따뜻한 안식을 제공합니다. 신장의 장기적인 보존을 도모하기 위한 구체적인 홈케어 관리 요령은 다음과 같습니다:
* **철저한 혈압과 혈당의 통제**: {subject} 생태계에서 가장 기본적이고 핵심이 되는 지표는 바로 혈압 조절입니다. 가정용 자동 혈압계를 수시로 체크하여 수축기 혈압 130mmHg 미만을 일상 속에서 타이트하게 유지하는 습관을 들여야 합니다.
* **가벼운 유산소 운동과 수분량 제어**: 탈수가 오면 신장으로 가는 혈류량이 급격히 줄어 신기능이 단기 악화될 수 있으므로, 적절한 온도의 맹물을 조금씩 나누어 드십시오. 단, 투석 단계 환우분은 과도한 음수가 폐부종을 부를 수 있어 철저히 계량된 음수 조절이 필수적입니다."""
    ]
    
    # 맺음말 결론 템플릿
    conclusion_templates = [
        f"""이번 {subject} 관련 의학 릴리즈 정보는 길고 고단한 만성 콩팥병 치료 여정 속에서 신뢰할 수 있는 임상적 지표와 용기를 안겨주는 단비 같은 가이드라인입니다. 늘 환우분들의 건강을 최우선으로 생각하고 신장의 안정을 지키는 믿음직한 든든한 동반자가 되겠습니다.""",
        
        f"""이번 {subject} 소식이 신기능 보호와 홈케어 조절에 힘쓰고 계시는 모든 환우분들의 가정에 따스한 희망으로 가 닿기를 소망합니다. 매일 마주하는 식탁 위에서 저염, 저칼륨, 저인, 저단백 4대 식사 수칙을 단호하고도 영리하게 실천해 나가시길 늘 마음 다해 응원합니다."""
    ]
    
    # 해시 시드를 이용해 템플릿 조합의 다양성 확보
    hash_seed = len(translated_title) + len(translated_body)
    selected_insight = insight_templates[hash_seed % len(insight_templates)]
    selected_conclusion = conclusion_templates[(hash_seed + 3) % len(conclusion_templates)]
    
    post_content = f"""
늘 신장 질환 환우분들의 건강과 신장 수명 연장을 최우선으로 생각하는 **[{feed_name}]**의 최신 의학 리포트 분석 시간입니다.

---

## 1. 최신 의학 리포트 팩트 체크
해당 분석 뉴스의 구체적인 핵심 원문 정보와 요약은 다음과 같습니다:

> **[핵심 리포트 요약]**
> {translated_body}

*이번 임상 분석 데이터는 환우분들의 전신 장기 기능 보존 및 치료 방향에 지대한 영향을 미칠 수 있는 중요한 지표를 내포하고 있습니다. 세부 분석 결과와 행동 지침은 아래의 연계 수칙을 반드시 참고해 주시기 바랍니다.*

---

## 2. 만성 콩팥병 환우를 위한 핵심 건강 수칙
이번에 공유된 **{subject}** 소식과 연계하여, 만성 콩팥병 환우분들이 일상 속에서 몸의 항상성을 유지하고 신장 손상을 최소화하기 위해 매일 명심해야 할 임상 시사점입니다:

{selected_insight}

---

## 3. 콩팥 보호를 위한 4대 식사 원칙 및 식단 가이드
신장 여과율 저하로 콩팥 기능을 금쪽같이 보존해야 하는 단계에서 가장 영양학적으로 비중 있게 다뤄야 할 식이 관리 요령입니다:

{diet_guidelines}

---

## 4. 따뜻한 격려와 맺음말
{selected_conclusion}

*본 콘텐츠는 [{feed_name}]({link})의 RSS 자료 정보를 바탕으로 작성되었습니다. 개별 환우분의 정확한 건강 및 콩팥 기능 단계(사구체 여과율 수치, 전해질 상태 등)에 따라 세부 물 섭취 제한이나 염분 및 단백질 섭취 한도는 차이가 클 수 있으므로, 실생활에 적용하시기 전 반드시 병원 담당 주치의 및 임상영양사와의 1:1 영양 상담을 최우선적으로 거치시길 강력히 권해 드립니다.*
"""
    return post_content

def call_gemini_api(api_key, prompt):
    """
    구글 Gemini 2.5 Flash API를 호출하여 컨텐츠를 지능적으로 생성하거나 감수합니다.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"  [Gemini API Warning] API 호출 실패 (HTTP {response.status_code}): {response.text[:100]}")
            return None
    except Exception as e:
        print(f"  [Gemini API Error] 네트워크 단절 또는 API 호출 오류: {e}")
        return None

def auto_collect_posts():
    # 수집 대상 글로벌 의학 저널 및 신장 관련 주요 RSS 피드 정의
    feeds = [
        {"name": "ScienceDaily Kidney Disease", "url": "https://www.sciencedaily.com/rss/health_medicine/kidney_disease.xml"},
        {"name": "ScienceDaily Nutrition", "url": "https://www.sciencedaily.com/rss/health_medicine/nutrition.xml"},
        {"name": "WHO Health News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
        {"name": "CDC Newsroom", "url": "https://www.cdc.gov/media/feed.xml"}
    ]
    
    # .env 파일 또는 .env.local 환경 변수에서 API KEY 자동 탐지 및 로드
    api_key = os.environ.get("GEMINI_API_KEY") or ""
    if not api_key:
        env_files = [os.path.join(BLOG_DIR, ".env"), os.path.join(BLOG_DIR, ".env.local")]
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8-sig") as ef:
                        for line in ef:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                key, val = line.split("=", 1)
                                if key.strip() == "GEMINI_API_KEY":
                                    api_key = val.strip().strip('"').strip("'")
                                    print(f"  [INFO] 환경 파일({os.path.basename(env_file)})에서 GEMINI_API_KEY 자동 로드 완료!")
                                    break
                except Exception as e:
                    print(f"  [WARNING] 환경 파일 로드 실패: {e}")
            if api_key:
                break
                
    print("[INFO] 신장 블로그 자동 포스팅 수집 수집기 기동!")
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # 낡거나 기존에 자동으로 작성된 포스트들을 지우고 청소 작업을 선행합니다.
    print("[INFO] 이전 수집된 자동 생성 마크다운 파일들의 폴더 정리 시작...")
    removed_count = 0
    if os.path.exists(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if filename.startswith("auto-") and filename.endswith(".md"):
                try:
                    os.remove(os.path.join(POSTS_DIR, filename))
                    removed_count += 1
                except Exception as e:
                    print(f"  [CLEAN WARNING] 파일 제거 중 에러: {filename}: {e}")
    print(f"[INFO] 이전 자동 수집 마크다운 파일 {removed_count}개 일괄 정리 완료!")
    
    collected_count = 0
    # 전체 피드 통합 최대 수집 제한 (과도한 포스팅 생성 및 API 남용 방지)
    max_collect_limit = 6
    
    for idx, feed_info in enumerate(feeds):
        if collected_count >= max_collect_limit:
            break
            
        print(f"\n[FEED] 신규 피드 채널 분석 중: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            print(f"  [ERROR] RSS 피드를 읽을 수 없습니다: {e}")
            continue
            
        # 최신 기사 3개씩을 타겟팅하여 중복 여부 확인 후 파싱 시도
        entries = feed.entries[:3]
        
        for entry in entries:
            if collected_count >= max_collect_limit:
                break
                
            title = entry.title
            link = entry.link
            summary = entry.get("summary", entry.get("description", ""))
            summary_clean = clean_html(summary)
            
            # [필터 1]: 스팸 및 광고성 금지 키워드가 포함되었는지 확인
            if check_blacklist(title) or check_blacklist(summary_clean):
                print(f"  [BLOCKED] 금지 키워드가 발견되어 글을 차단합니다: {title[:20]}...")
                continue
                
            # [필터 2]: 품질 기준 통과 및 최소 글자수 검사
            if not validate_content(title, summary_clean):
                print(f"  [SKIP QUALITY] 품질 기준 미달 혹은 짧은 메타 텍스트로 건너뜁니다: {title[:20]}...")
                continue
                
            # 파일 이름용 슬러그 생성
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            slug_words = slug.split("-")[:5]
            slug = "-".join(slug_words)
            
            output_filepath = os.path.join(POSTS_DIR, f"auto-{slug}.md")
            
            # 이미 수집되어 마크다운 파일이 쌓인 경우 건너뜀
            if os.path.exists(output_filepath):
                print(f"  [SKIP] 이미 존재하는 마크다운 파일입니다: auto-{slug}.md")
                continue
                
            print(f"  [COLLECT] 신규 기사 수집 작업 시작: {title[:25]}...")
            
            post_content = ""
            meta_description = ""
            
            # 기사 카드용 가 Harmonics 대표 Unsplash 썸네일 고화질 링크 매핑
            thumbnail_url = UNSPLASH_THUMBNAILS[collected_count % len(UNSPLASH_THUMBNAILS)]
            
            # 뉴스 요약본 문장 끝맺음 청소
            cleaned_summary = clean_truncated_summary(summary_clean)
            
            if api_key:
                # [방식 A] Gemini 2.5 Flash를 이용한 100% 창작 포스트 생성 모드 구동
                print("  [AI MODE] Gemini 2.5 Flash 고품질 창작 글쓰기 기동...")
                
                prompt = f"""
                You are an expert, highly compassionate clinical nephrologist, renal dietitian, and professional medical blogger.
                Below is the raw summary data of a recent technology news or medical study.
                Your task is to write a highly detailed, extremely engaging, informative, and long-form (at least 1800 Korean characters) blog post in Korean that bridges this news topic to Chronic Kidney Disease (CKD) health care.
                
                CRITICAL MEDICAL & COPYRIGHT RULES:
                1. DO NOT copy-paste sentences from the input. Extract the medical facts only, and write the entire post using completely new sentence structures and your own highly professional, empathetic, and clear explanation.
                2. The tone of voice must be extremely polite, compassionate, comforting, informative, and professional (use '-요', '-습니다' style). Write it so that CKD patients and their families can easily understand and find comfort and hope.
                3. INTEGRATE THE 4대 신장 식사 수칙 (Low Sodium, Low Potassium, Low Phosphorus, Low Protein) naturally by explaining exactly how to apply it in cooking and daily life in relation to the theme:
                   - 나트륨 (Low Sodium): 혈압 조절 및 사구체 보호를 위한 염분 조절.
                   - 칼륨 (Low Potassium): 고칼륨혈증 예방 및 근육/심장 안정을 위해 칼륨 배출 조절 및 채소 전처리 가이드.
                   - 인 (Low Phosphorus): 뼈 및 혈관 질환 예방을 위한 가공식품 자제 및 첨가물 인 주의.
                   - 단백질 (Low Protein): 질소 노폐물(요독)을 줄여 잔여 사구체를 보존하기 위한 단백질 제한 및 아미노산 공급 요령.
                
                Input Article Title: {title}
                Input Article Summary: {cleaned_summary}
                
                Your Output Format MUST contain only the raw body of the article in standard Markdown format.
                Do not include YAML frontmatter, do not include H1 title inside the markdown.
                Structure the post beautifully with Heading 2 (##) and Heading 3 (###).
                Include:
                ## 1. 최신 의학 리포트 팩트 체크 (Detailed explanation of the news)
                ## 2. 만성 콩팥병 환우를 위한 핵심 건강 수칙 (Empathy, practical daily tips, connection of this news to renal health)
                ## 3. 콩팥 보호를 위한 4대 식사 원칙 및 식단 가이드 (Low sodium/potassium/phosphorus/protein specific cooking and diet guide)
                ## 4. 따뜻한 격려와 맺음말 (Empathetic closing statement)
                """
                
                ai_output = call_gemini_api(api_key, prompt)
                if ai_output:
                    post_content = ai_output.strip()
                    meta_description = f"최신 글로벌 헬스 소식 '{title}'에 대한 임상학적 영양 분석 및 콩팥 보호 식사 수칙 가이드입니다."
                else:
                    api_key = "" # API 연동 실패 시 방식 B(FREE MODE)로 폴백 처리
                    
            if not api_key:
                # [방식 B] 구글 번역 및 고도화된 정적 템플릿 조립 (무료 모드 기본)
                print("  [FREE MODE] 기계 번역 및 정제 템플릿 조립 기동...")
                translator = GoogleTranslator(source='en', target='ko')
                
                try:
                    # 1. 구글 1차 번역
                    translated_title = translator.translate(title)
                    translated_body = translator.translate(cleaned_summary[:4500])
                    
                    # 2. 번역 오역 및 비문 정밀 교정
                    translated_title = verify_and_refine_translation(translated_title)
                    translated_body = verify_and_refine_translation(translated_body)
                    
                    # 3. 마크다운 결합 조립
                    post_content = generate_dynamic_free_content(feed_info['name'], link, translated_title, translated_body)
                    meta_description = f"글로벌 신장 채널 {feed_info['name']}의 '{translated_title}' 자료에 대한 전문적 분석 리포트입니다."
                    
                    # --- [추가 개선] API Key가 유효하다면 조립된 최종 포스트를 Gemini를 통해 최종 매끄럽게 윤문 감수 ---
                    # 이로써 무료 번역 모드로 포스트를 생성했더라도 번역 문장의 부자연스러움을 완벽하게 탈피합니다.
                    temp_api_key = os.getenv("GEMINI_API_KEY")
                    if temp_api_key:
                        print("  [AI PROOFREAD] Gemini API를 활용한 실시간 한국어 번역 윤문 감수 구동...")
                        proofread_prompt = f"""
                        You are a professional medical translator and top-tier editor specialized in clinical nephrology.
                        Below is a draft blog post in Korean. It was generated via machine translation and static templates, and contains some rough sentences, grammar issues, or awkward phrasing.
                        
                        Your task is to thoroughly proofread, polish, and rewrite the sentences in Korean so they flow EXTREMELY naturally, professionally, and compassionately (comforting '-요', '-습니다' style).
                        
                        CRITICAL INSTRUCTIONS:
                        1. DO NOT change the core medical facts, structure, or standard Markdown headers (##, ###).
                        2. Fix any awkward direct translations of English terms so they read like a premium Korean clinical column.
                        3. Fix the Korean particles (은/는, 이/가, 을/를) and honorifics so they flow naturally.
                        
                        Here is the draft post:
                        {post_content}
                        
                        Return only the polished standard Markdown output. No extra chats or explanations.
                        """
                        refined_output = call_gemini_api(temp_api_key, proofread_prompt)
                        if refined_output and len(refined_output.strip()) > 500:
                            post_content = refined_output.strip()
                            print("  [AI PROOFREAD SUCCESS] 실시간 윤문 감수 처리가 완료되었습니다!")
                    
                except Exception as e:
                    print(f"  [ERROR] 무료 번역 처리 중 예외 발생: {e}")
                    continue
            
            # YAML Frontmatter 헤더 자동 생성
            final_title = f"[AI 추천] {translated_title if not api_key else title}"
            
            yaml_header = f"""---
title: "{final_title}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{meta_description}"
tags: ["신장건강", "사구체보호", "이식관리", "식단가이드"]
thumbnail: "{thumbnail_url}"
slug: "auto-{slug}"
---

"""
            # 최종 완성된 포스트를 UTF-8 인코딩으로 마크다운 저장
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(yaml_header + post_content)
                
            print(f"  [SUCCESS] 파일 영속화 완료: auto-{slug}.md")
            collected_count += 1
            
    print(f"\n[COMPLETE] 총 {collected_count}개의 최신 의학 기사가 포맷 필터 및 AI/번역 검증을 통과하여 '/data/posts/'에 완벽하게 영속화되었습니다!")

if __name__ == "__main__":
    auto_collect_posts()
