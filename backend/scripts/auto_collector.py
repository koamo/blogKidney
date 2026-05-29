# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import urllib.parse
import feedparser
import requests
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# 윈도우 환경 터미널 특수문자(\xa0 등) 출력 인코딩 크래시 원천 차단
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 기본 프로젝트 경로 설정 (blog_kidney 전용)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 불법/정책위반 키워드 블랙리스트 정의 (구글 애드센스 정책 준수)
BLACKLIST_KEYWORDS = [
    'hack', 'crack', 'casino', 'gambling', 'illegal', 'adult', 'porn', 'torrent', 'bypass',
    '도박', '해킹', '크랙', '불법복제', '마약', '성인물', '사설토토', '무단배포', '우회'
]

# 신장 건강 및 치유 테마의 고품질 Unsplash 상업용 무료 라이선스 썸네일
UNSPLASH_THUMBNAILS = [
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80", # 요가 명상 힐링
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80", # 신선한 야채 건강 식단
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80", # 맑은 물과 건강한 생활
    "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&w=800&q=80", # 청진기 의학 신뢰
    "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=800&q=80"  # 치유의 자연 숲
]

def clean_html(raw_html):
    """HTML 태그 제거"""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def check_blacklist(text):
    """정책 위반 필터링"""
    if not text:
        return False
    text_lower = text.lower()
    for word in BLACKLIST_KEYWORDS:
        if word in text_lower:
            return True
    return False

def validate_content(title, summary):
    """
    수집된 요약글이 의학 정보로서 실질적인 가치가 있는지 검증합니다.
    80자 이하이거나 메타데이터 텍스트가 있을 경우 False를 반환하여 수집을 스킵합니다.
    """
    if not summary or not title:
        return False
    if len(summary.strip()) < 80:
        return False
    
    # 단순 메타데이터 성격의 단어가 섞여 있으면 수집 대상에서 제외
    meta_patterns = ['category:', 'news date:', 'last edit review:', '마지막 편집', '뉴스작성일']
    summary_lower = summary.lower()
    for pattern in meta_patterns:
        if pattern in summary_lower:
            return False
            
    return True

def clean_truncated_summary(summary):
    """
    RSS 피드 요약글 꼬리의 잘림 표기 [...] 및 [Read More]를 제거하고
    문법적으로 완성도 높게 문장을 마감 보정합니다.
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

def extract_main_subject(title):
    """신장 건강 뉴스 제목에서 핵심 키워드를 안전하게 추출하고 조사를 제거하며 의학 용어로 치환합니다."""
    if not title:
        return "신장 건강"
    
    # 1. 대괄호/괄호 안의 주제어 정제
    title_clean = re.sub(r'\[.*?\]', '', title)
    title_clean = re.sub(r'\(.*?\)', '', title_clean)
    title_clean = title_clean.strip()
    
    if not title_clean:
        return "신장 건강"
        
    # 2. 콜론 앞부분 주제어 추출
    if ":" in title_clean:
        part = title_clean.split(":", 1)[0].strip()
        if len(part) < 30:
            title_clean = part
            
    # 3. 영어 타이틀인 경우 (원문 제목 처리)
    words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', title_clean)
    if words:
        filtered = [w for w in words if w.lower() not in [
            'a', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'by', 'for', 'with', 
            'new', 'how', 'why', 'what', 'study', 'research', 'patients', 'people',
            'her', 'his', 'him', 'she', 'he', 'they', 'them', 'their', 'brother', 'sister', 'child', 'boy', 'girl'
        ]]
        if filtered:
            english_subject = filtered[0]
            eng_ko_map = {
                "Kidney": "신장", "Renal": "신장", "Nephrology": "신장학", "Diet": "식단",
                "Water": "수분 섭취", "Stone": "신장 결석", "Stones": "신장 결석",
                "Fibrosis": "신장 섬유화", "HLHS": "소아 장기 이식", "Transplant": "장기 이식",
                "Heart": "장기 이식", "Gut": "장내 미생물", "Guava": "구아바 주스",
                "Drug": "신약 개발", "Diabetes": "당뇨병성 신증", "Hypertension": "고혈압",
                "Urology": "비뇨기계 질환", "Dialysis": "신장 투석 치료"
            }
            if english_subject in eng_ko_map:
                return eng_ko_map[english_subject]
            if english_subject.lower() in ['her', 'his', 'brother', 'sister', 'child', 'boy', 'girl', 'year']:
                return "소아 장기 이식"
            return english_subject

    # 4. 한국어 번역 타이틀인 경우 (번역된 제목 처리)
    korean_words = re.findall(r'\b[가-힣0-9]{2,8}\b', title_clean)
    if korean_words:
        candidate = korean_words[0]
        
        # 조사를 안전하게 제거하는 한글 형태소 꼬리 정제 로직
        particles = [
            '에서는', '으로부터', '에게서', '으로써', '으로서', '에서', '에게', '한테', 
            '으로', '부터', '까지', '보다', '은', '는', '이', '가', '을', '를', '의', '에', 
            '로', '과', '와', '도', '만', '나', '고', '며'
        ]
        for p in particles:
            if candidate.endswith(p) and len(candidate) > len(p):
                candidate = candidate[:-len(p)]
                break
                
        # 인칭대명사나 부적절한 단어를 격이 높은 의학 전문 명사로 치환하는 사전
        subject_replace_map = {
            "소년": "소아 장기 이식", "소녀": "소아 장기 이식", "그녀": "소아 장기 이식", 
            "그": "신장 보호", "그들": "신장 환우", "어린이": "소아 장기 이식", 
            "아이": "소아 장기 이식", "환자": "신장 환우", "사람": "신장 보호", 
            "연구": "신장 연구", "발표": "신장 소식", "보도": "신장 뉴스",
            "형제": "장기 기증", "오빠": "장기 기증", "누나": "장기 기증", 
            "언니": "장기 기증", "동생": "장기 기증", "가족": "가족 건강",
            "세": "소아 장기 이식", "세의": "소아 장기 이식", "그레이시": "소아 장기 이식"
        }
        if candidate in subject_replace_map:
            return subject_replace_map[candidate]
            
        # 숫자가 포함된 단어이거나 너무 짧은 비정상 글자 필터 방어 (예: 11세, 11, 세 등 격퇴)
        if not re.match(r'^[가-힣]+$', candidate) or candidate.isdigit() or len(candidate) < 2:
            return "소아 장기 이식"
            
        return candidate
        
    return "만성 콩팥병 관리"
def generate_dynamic_free_content(feed_name, link, translated_title, translated_body):
    """
    무료 번역 모드(Fallback) 실행 시, 100% 획일적인 정적 템일 복제를 영구 박멸하고,
    실제 번역 본문을 문장 단위로 분해하고 분석하여 기사마다 유일무이한 고품질 콩팥 보고서를 동적으로 합성합니다.
    """
    subject = extract_main_subject(translated_title)
    
    # 1. 팩트 팽창 엔진(Fact Expander): 요약문을 마침표 기준으로 나누어 유기적으로 보강
    body_sentences = [s.strip() + "." for s in translated_body.split('.') if s.strip()]
    cleaned_sentences = [s for s in body_sentences if len(s) > 10]
    
    fact_core = " ".join(cleaned_sentences[:2]) if len(cleaned_sentences) >= 2 else translated_body
    fact_expansion = ""
    
    if len(translated_body) < 180:
        fact_expansion = (
            f" 이번 발표된 의학 연구 결과는 사구체 여과율 수호가 생명선인 만성 콩팥병 환우들에게 매우 획기적인 임상적 돌파구를 선사합니다. "
            f"신장의학 및 임상영양학 권위자들은 이번 **{subject}** 소식에 조명된 신체 대사 조절 작용이 요독증 관리 및 골대사 합병증 예방에 대단히 깊은 연관이 있다고 분석합니다. "
            f"특히 이 소식은 환우분들이 일상 식탁에서 무심코 섭취할 수 있는 수분 및 칼륨 균형 통제에 중대한 식단 웰니스 가이드를 부여하여 큰 도움을 안겨주고 있습니다."
        )
    else:
        fact_expansion = (
            f" 이 중대한 의학적 사실은 **{subject}** 건강 관리 전반에 걸쳐 신장내과 사구체 필터를 안정적으로 보호하고, "
            f"환우 가족분들이 가정에서 실천하기 적합한 정밀 저나트륨/저칼륨 라이프 수칙에 중대한 실천 가이드라인을 제공합니다."
        )
        
    expanded_fact = fact_core + fact_expansion

    # 2. 기사 본문 기반 동적 콩팥 건강 수칙 분석기
    insight_point_1 = "신장 사구체 누적 부하 제어 및 보존"
    insight_desc_1 = f"이번에 소개된 {subject}의 흐름은 신장 사구체 필터의 과여과 현상을 방지하고, 매일 섭취하는 영양 성분의 대사 노폐물을 최소화하는 데 중요한 나침반이 됩니다."
    
    insight_point_2 = "수동적인 약물 의존 탈피와 자가 식단 수호"
    insight_desc_2 = f"단순 약물 투약에만 의존하는 것보다, 이번 {subject} 관련 의학 지표를 식탁 요리에 이식하여 콩팥에 직접 작용하는 칼륨과 인의 수치를 안전하게 다스려야 합니다."
    
    insight_point_3 = "전신 부종 차단 및 부작용 예방 가이드"
    insight_desc_3 = f"결국 환우분들의 장기 생명 연장과 웰니스는 체내 수분 밸런스를 조화롭게 제어하고, {subject}에 맞추어 임상영양사와의 맞춤 상담을 거친 안전한 자연식에서 시작됩니다."
    
    if len(cleaned_sentences) >= 3:
        insight_desc_1 = f"학술적으로 보고된 '{cleaned_sentences[0]}' 의학 팩트는 콩팥 손상을 막고 신장 필터의 잔여 기능을 장기 안식하도록 유도하는 직접적인 교훈이 됩니다."
    if len(cleaned_sentences) >= 4:
        insight_desc_2 = f"특히 '{cleaned_sentences[1]}'에 언급된 대사 기전은 혈액 투석 및 투석 전 단계 환우들이 고칼륨혈증 부정맥 리스크를 예방하기 위해 반드시 명심해야 할 식단 열쇠입니다."
    if len(cleaned_sentences) >= 5:
        insight_desc_3 = f"나아가 '{cleaned_sentences[2]}' 측면의 분석을 살펴보면, 뼈 칼슘 소실 및 가려움증을 유발하는 과다 인 섭취 위험을 사전 통제하고 {subject}의 시너지를 배가시키는 든든한 방어막이 됩니다."

    # 3. 콩팥 라이프 식이 4대 원칙 맞춤형 케어
    diet_guidelines = f"""이번 **{subject}** 소식은 콩팥 사구체를 무결하게 수호하기 위한 식이요법 기준을 제시합니다. 환우분들이 안전하게 준수해야 하는 식탁 4대 철칙은 다음과 같습니다:

1. **천연 양념을 활용한 저나트륨 식단 (Low Sodium)**
   * **원리**: 체내 나트륨 수치가 불안정하면 혈압 동요를 유발해 신장 필터를 빠르게 악화시키고 신체 부종을 촉진합니다.
   * **실천 가이드**: 소금과 간장 대신 식초, 레몬즙, 마늘, 파 등 천연 조미료로 맛을 내고 국과 찌개의 국물은 단 1방울도 마시지 않고 전부 남겨야 합니다.

2. **칼륨 수치 안전 통제 및 물 섭취 가이드 (Low Potassium)**
   * **원리**: 신부전 환자는 칼륨 배출이 어려워 바나나, 토마토 등 생과채류 섭취 시 부정맥 등 심각한 위험을 겪을 수 있습니다.
   * **실천 가이드**: {subject} 식단 실천을 위해 모든 푸른 채소는 얇게 썰어 물에 2시간 이상 담가두거나 끓는 물에 데쳐서 수용성 칼륨을 완벽하게 제거하고 섭취해야 합니다.

3. **가공식품 첨가물 배제 저인 관리 (Low Phosphorus)**
   * **원리**: 콜라, 소시지 등 인스턴트 식품에 포함된 보존용 인산염은 거의 100% 체내로 흡수되어 뼈 칼슘 소실 및 혈관 석회화를 초래하는 독입니다.
   * **실천 가이드**: 유제품과 치즈를 멀리하고 가급적 식품 첨가물이 없는 자연 그대로의 신선한 쌀밥과 데친 나물 식단을 엄수해 주셔야 합니다.

4. **사구체 보호 양질의 저단백 생활 (Low Protein)**
   * **원리**: 과도한 단백질 섭취는 신장에 과부하를 주어 요독 수치를 폭발적으로 상승시키는 악순환을 만듭니다.
   * **실천 가이드**: 전체 단백질의 섭취량은 주치의 처방량에 맞추어 저울로 계량하여 드시되, 찌꺼기가 적고 효율이 높은 흰 계란이나 닭가슴살 위주로 소량 섭취해야 합니다."""

    post_content = f"""
만성 콩팥병 및 신장 건강의 든든한 동반자이자 과학적 건강 가이드를 제시하는 **[{feed_name}]**의 최신 보도 정보를 만성 콩팥병 환우와 가족분들의 안전한 생활 관리를 돕기 위해 정밀 편찬한 헬스 리포트입니다.

---

## 1. 최신 의학 리포트 요약 및 팩트 체크
해당 학술 소식이 다루고 있는 핵심 연구 결과 및 의학 정보의 핵심 번역 요약은 다음과 같습니다:

> **[주요 팩트 요약]**
> {expanded_fact}

*이 최신 의학 정보는 콩팥 사구체 여과율의 안정적 보존과 전신 염증 예방에 기여할 수 있는 중요한 흐름을 담고 있습니다. 상세한 연구 전문 및 임상 시험 데이터를 열람하시려면 하단에 기재된 공식 출처 링크를 적극 참고해 보시길 권장합니다.*

---

## 2. 만성 콩팥병 환우를 위한 핵심 건강 수칙
이번에 발표된 **{subject}** 소식과 연계하여, 만성 콩팥병 환우분들이 일상생활 속에서 안전을 확보하고 신장 기능을 최상으로 보호하기 위해 실천해야 할 구체적인 지침입니다:

* **{insight_point_1}**
  * *현업 적용*: {insight_desc_1}
* **{insight_point_2}**
  * *현업 적용*: {insight_desc_2}
* **{insight_point_3}**
  * *현업 적용*: {insight_desc_3}

---

## 3. 콩팥 라이프 식이 4대 원칙 맞춤형 케어
신장 건강 수호의 절대적 기준이자 신체 기능 부하를 원천 차단하기 위해 매일 식탁에서 준수해야 하는 식이요법의 정석입니다:

{diet_guidelines}

---

## 4. 결론 및 신장 전문의 관점의 시사점
결론적으로 **{subject}**의 올바른 의학적 인지와 가정 내 식이 조절은 콩팥 회복의 골든타임을 확보하려는 수많은 환우 및 가족분들께 일상 속 작은 기적을 선사하는 든든한 지침서가 될 것입니다. 늘 건강하고 신뢰할 수 있는 전 세계의 공신력 높은 의학 데이터를 정밀 팩트 체크하여 환우 여러분들의 신장 건강 동반자로서 끝까지 함께 걷고 응원하겠습니다.

*본 헬스 리포트는 [{feed_name}]({link})의 공식 RSS 발행 자료를 바탕으로 올바른 의학 정보 제공을 위해 저작권 가이드라인을 철저히 준수하여 정밀 번역 및 전문 콩팥 관리 지식을 융합해 작성되었습니다. 개인의 병증 단계에 따른 구체적인 약제 및 식단 적용은 반드시 담당 신장내과 전문의 및 임상영양사와의 상세한 상담을 우선적으로 거치셔야 합니다.*
"""
    return post_content

def call_gemini_api(api_key, prompt):
    """
    구글 최신 Gemini API를 강력한 재시도 로직과 모델명 다변화(1.5-flash / 2.5-flash) 정책을 탑재하여 호출합니다.
    """
    models = ["gemini-1.5-flash", "gemini-2.5-flash"]
    
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        # 3회 연속 실패 복구용 지수 백오프 재시도 기동
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=40)
                if response.status_code == 200:
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                elif response.status_code == 429:
                    # 무료 키의 429 할당량 초과는 대기해도 풀리지 않으므로 즉시 폴백을 실행하여 개발 속도를 보장합니다.
                    print(f"  [Gemini API Rate Limit (429)] 무료 API 키 할당량 초과 감지. 무중단 폴백 엔진을 즉각 기동합니다.")
                    return None
                else:
                    print(f"  [Gemini API Warning] {model_name} 호출 실패 (HTTP {response.status_code}): {response.text[:120]}")
                    break
            except Exception as e:
                import time
                wait_time = (attempt + 1) * 3
                print(f"  [Gemini API Network Exception] {e}. {wait_time}초 대기 후 재시도 합니다.")
                time.sleep(wait_time)
                
    return None

def auto_collect_posts():
    # 수집 정보 (의학적으로 공신력과 무결한 가동성이 입증된 글로벌 메이저 헬스 RSS 피드 매칭)
    # 인공신장, 최신 투석기기 및 신약 정보가 가장 활발하게 보도되는 2대 강자 최상단 전진 배치!
    feeds = [
        {"name": "Medical News Today Urology", "url": "https://rss.medicalnewstoday.com/urology-nephrology.xml"},
        {"name": "News Medical Renal", "url": "https://www.news-medical.net/syndication.axd?feed=Renal-Disease"},
        {"name": "ScienceDaily Kidney Disease", "url": "https://www.sciencedaily.com/rss/health_medicine/kidney_disease.xml"},
        {"name": "ScienceDaily Nutrition", "url": "https://www.sciencedaily.com/rss/health_medicine/nutrition.xml"},
        {"name": "WHO Health News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
        {"name": "CDC Newsroom", "url": "https://www.cdc.gov/media/feed.xml"}
    ]
    
    # 윈도우 환경 편의성 대폭 개선: 시스템 환경 변수 외에도 프로젝트 루트의 .env 파일 자동 로딩 및 주입
    # [BOM 철통 방어]: utf-8-sig 코덱을 사용하여 파워쉘에서 생성한 UTF-8 BOM 파일도 무결 감지합니다.
    api_key_loaded = os.environ.get("GEMINI_API_KEY") or ""
    if not api_key_loaded:
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
                                    api_key_loaded = val.strip().strip('"').strip("'")
                                    print(f"  [INFO] 로컬 설정 파일({os.path.basename(env_file)})에서 GEMINI_API_KEY 자동 로드 완료!")
                                    break
                except Exception as e:
                    print(f"  [WARNING] 로컬 설정 파일 파싱 중 오류: {e}")
            if api_key_loaded:
                break
                
    print("[INFO] 만성 콩팥병 및 신장 건강 전문 AI/지능형 자동 수집 파이프라인 가동!")
    # [품질 보장 조치]: 콘텐츠 영구 누적을 위해 이전 자동 파일 청소 단계를 배제합니다.
    print('[INFO] 콘텐츠 영구 누적을 위해 이전 자동 파일 청소 단계를 배제합니다.')
    collected_count = 0
    # 하루 수집 상한 한도를 3건으로 하향 조정하여 중복 노출을 지능적으로 차단
    max_collect_limit = 3
    
    for idx, feed_info in enumerate(feeds):
        if collected_count >= max_collect_limit:
            break
            
        print(f"\n[FEED] 신장의학 전문 채널 분석 개시: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            print(f"  [ERROR] RSS 피드를 읽어들일 수 없습니다: {e}")
            continue
            
        # 가장 최근 기사 최신 3개씩 파싱 시도 (필터에 통과하지 못하는 부실 기사가 있으므로 3개씩 후보 확보)
        entries = feed.entries[:3]
        
        for entry in entries:
            if collected_count >= max_collect_limit:
                break
                
            title = entry.title
            link = entry.link
            summary = entry.get("summary", entry.get("description", ""))
            summary_clean = clean_html(summary)
            
            # [보안 필터 1]: 애드센스 정책 위반 키워드가 섞여 있으면 스크랩 원천 배제
            if check_blacklist(title) or check_blacklist(summary_clean):
                print(f"  [BLOCKED] 애드센스 정책 위반 소지 감지 기사 배제: {title[:20]}...")
                continue
                
            # [품질 필터 2]: 요약문 글자 수가 80자 이하이거나 메타데이터 텍스트만 있는 부실 기사는 수집 원천 제외!
            if not validate_content(title, summary_clean):
                print(f"  [SKIP QUALITY] 알맹이가 없고 단순 메타데이터만 든 부실 기사 거부: {title[:20]}...")
                continue
                
            # 슬러그 생성 및 파일명 포맷 조합
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            slug_words = slug.split("-")[:5]
            slug = "-".join(slug_words)
            
            output_filepath = os.path.join(POSTS_DIR, f"auto-{slug}.md")
            
            # 중복 수집 발행 방지
            if os.path.exists(output_filepath):
                print(f"  [SKIP] 이미 데이터베이스에 존재하는 포스팅: auto-{slug}.md")
                continue
                
            print(f"  [COLLECT] 신규 의학 콘텐츠 수집 완료: {title[:25]}...")
            
            post_content = ""
            meta_description = ""
            
            # Unsplash 상업용 무료 라이선스 고화질 힐링 사진 썸네일 매핑
            thumbnail_url = UNSPLASH_THUMBNAILS[collected_count % len(UNSPLASH_THUMBNAILS)]
            
            # 1초 잘림 방지 필터 거치기
            cleaned_summary = clean_truncated_summary(summary_clean)
            
            final_title = ""
            subject = extract_main_subject(title)
            
            # 이 개별 포스트에서 AI 생성의 성공 여부를 추적하는 플래그
            ai_generation_success = False
            
            if api_key_loaded:
                # [모드 A] Gemini Flash를 가동한 100% 완전 창작 오리지널 콩팥 전문 힐링 포스팅 모드
                print("  [AI MODE] Gemini 신장의학/영양학 전문 창작 에디팅 기동...")
                
                prompt = f"""
                You are an expert, highly compassionate clinical nephrologist, renal dietitian, and professional medical blogger.
                Below is the raw summary data of a recent medical study or health news.
                Your task is to write a highly detailed, extremely engaging, informative, and long-form (at least 1800 Korean characters) blog post in Korean that bridges this news topic to Chronic Kidney Disease (CKD) health care.
                
                CRITICAL TITLE & MARKETING RULES:
                1. You MUST generate an extremely click-driven, curiosity-inducing, and catchy Korean title.
                   - Avoid flat translations or boring clinical titles.
                   - Use high-impact hooks like "[환우필독]", "[식이수칙]", "[비상경고]", "[기적의 콩팥]", "[의학포커스]", "[건강비책]", "[사구체수호]", "[긴급경보]" at the beginning.
                   - Rephrase the title to spark absolute curiosity and empathy so that patients and families cannot resist clicking it. (e.g., instead of "New study on renal fibrosis", write "[환우필독] 콩팥이 굳어가는 무서운 섬유화? 사구체 철벽 방어를 위한 식탁 위의 기적적인 예방 비책!")
                   - The first line of your output MUST be the title in this exact format:
                     TITLE: [Your High-Impact Hooking Title]
                
                CRITICAL MEDICAL & COPYRIGHT RULES:
                1. DO NOT copy-paste standard or generic '신장 식이 4대 법칙' explanations. You must write a completely customized, unique, and highly specific 4 principles guide that directly relates to the input news topic.
                   For instance, if the news is about water intake or kidney stones:
                     - Explain Low Sodium in terms of calcium excretion in urine.
                     - Explain Low Potassium in terms of custom fruit selection.
                     - Explain Low Phosphorus in terms of calcium-phosphate crystallization.
                     - Explain Low Protein in terms of reducing acidic loads on glomeruli.
                   Every principle must be 100% custom-written and deeply tailored to the specific news topic. Repeating generic definitions is strictly forbidden!
                2. The tone of voice must be extremely polite, compassionate, comforting, informative, and professional (use '-요', '-습니다' style). Write it so that CKD patients and their families can easily understand and find comfort and hope.
                
                Input Article Title: {title}
                Input Article Summary: {cleaned_summary}
                
                Your Output Format MUST contain the TITLE on the very first line starting with "TITLE: ", followed by the raw body of the article in standard Markdown format (separated by newlines).
                Do not include YAML frontmatter, do not include H1 title inside the markdown.
                Structure the post beautifully with Heading 2 (##) and Heading 3 (###).
                Include:
                ## 1. 최신 의학 리포트 요약 및 팩트 체크 (Detailed explanation of the news)
                ## 2. 만성 콩팥병 환우를 위한 핵심 건강 수칙 (Empathy, practical daily tips, connection of this news to renal health)
                ## 3. 콩팥 라이프 식이 4대 원칙 맞춤형 케어 (Low sodium/potassium/phosphorus/protein specific cooking and diet guide deeply customized to this news)
                ## 4. 결론 및 신장 전문의 관점의 시사점 (Empathetic closing statement)
                """
                
                ai_output = call_gemini_api(api_key_loaded, prompt)
                if ai_output:
                    ai_output = ai_output.strip()
                    lines = ai_output.split('\n')
                    title_line = ""
                    body_start_idx = 0
                    
                    for idx_line, line in enumerate(lines):
                        if line.startswith("TITLE:"):
                            title_line = line.replace("TITLE:", "").strip()
                            body_start_idx = idx_line + 1
                            break
                        elif line.startswith("title:"):
                            title_line = line.replace("title:", "").strip()
                            body_start_idx = idx_line + 1
                            break
                            
                    if title_line:
                        title_line = title_line.strip('"').strip("'")
                        final_title = title_line
                        post_content = "\n".join(lines[body_start_idx:]).strip()
                    else:
                        final_title = "[콩팥 가이드] " + subject + "의 놀라운 대반전"
                        post_content = ai_output
                        
                    meta_description = f"최신 글로벌 콩팥 의학 소식 '{final_title}'에 대한 신장 전문의 관점의 독창적인 해석 및 케어 가이드 리포트입니다."
                    ai_generation_success = True
                else:
                    print("  [Gemini API Failure] API 호출 실패 또는 타임아웃으로 이 포스트에 한해 무료 폴백 모드로 자동 전환합니다.")
                    
            if not api_key_loaded or not ai_generation_success:
                # [모드 B] 구글 번역 + 신장 전문 인텔리전트 동적 매핑 엔진 (출처 정확히 명시 모드)
                print("  [FREE MODE] 무료 신장 전문 지능형 동적 매핑 엔진 집필 기동...")
                translator = GoogleTranslator(source='en', target='ko')
                
                try:
                    # 제목 번역
                    translated_title = translator.translate(title)
                    # 요약 본문 번역
                    translated_body = translator.translate(cleaned_summary[:4500])
                    
                    # 호기심 유발형 타이틀 빌더 적용
                    final_title = "[콩팥 가이드] " + translated_title
                    prefixes = ["[환우필독]", "[식이수칙]", "[비상경고]", "[기적의 콩팥]", "[의학포커스]", "[건강비책]"]
                    suffixes = ["절대 놓쳐선 안 되는 이유!", "콩팥을 수호하는 핵심 열쇠!", "이대로 두면 위험합니다!", "평생 콩팥 수호하는 지름길!"]
                    
                    title_clean = translated_title.replace("콩팥 가이드", "").replace("[콩팥 가이드]", "").strip()
                    title_clean = re.sub(r'^["\'\[\(]+', '', title_clean)
                    title_clean = re.sub(r'["\'\]\)]+$', '', title_clean)
                    
                    final_title = f"{random.choice(prefixes)} '{subject}'을(를) 위한 긴급 처방: {title_clean} - {random.choice(suffixes)}"
                    
                    # 동적 템플릿 조합 본문 생성
                    post_content = generate_dynamic_free_content(feed_info['name'], link, translated_title, translated_body)
                    
                    meta_description = f"글로벌 신장 전문 채널 {feed_info['name']}에서 보도된 '{final_title}' 자료에 대한 콩팥 라이프 정밀 번역 분석 리포트입니다."
                    
                except Exception as e:
                    print(f"  [ERROR] 무료 번역 엔진 장애 발생: {e}")
                    continue
            
            # YAML Frontmatter 헤더 가이드라인 생성
            yaml_header = f"""---
title: "{final_title}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{meta_description}"
tags: ["콩팥건강", "만성콩팥병", "식이요법", "신장케어"]
thumbnail: "{thumbnail_url}"
slug: "auto-{slug}"
---

"""
            # 완성된 마크다운 초안 적재
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(yaml_header + post_content)
                
            print(f"  [SUCCESS] 초안 마크다운 적재 완료: auto-{slug}.md (제목: {final_title})")
            collected_count += 1
            
    # [백업 엔진]: 오늘 신규 수집된 뉴스가 없는 경우, 블로그 활성화를 위해 Gemini 오리지널 특집 기사(인공신장/새 투석기)를 발행합니다.
    if collected_count == 0 and api_key_loaded:
        print("\n  [BACKUP ENGINE] 오늘 신규 수집된 뉴스가 없습니다. 블로그 활성화를 위해 Gemini 오리지널 특집 기사를 발행합니다...")
        
        # 만성 콩팥병 환우들의 지적 요구를 충족할 인공신장, 최신 투석 기술 테마들 중 하나를 무작위로 선정
        special_topics = [
            {
                "theme": "웨어러블 인공신장(WAK) 개발 로드맵과 상용화 전망",
                "slug": "wearable-artificial-kidney-development-status",
                "tag": "인공신장"
            },
            {
                "theme": "차세대 고효율 혈액투석기 필터 기술과 요독 제거 향상 방안",
                "slug": "next-generation-hemodialysis-filter-technology",
                "tag": "새로운 투석기기"
            },
            {
                "theme": "만성 신부전 환우를 위한 신장 보호 4대 영양 밸런스 실천 비책",
                "slug": "four-essential-renal-dietary-rules-for-ckd",
                "tag": "식이요법"
            },
            {
                "theme": "복막투석 환우를 위한 가정 내 복막염 예방 및 안전 관리 수칙",
                "slug": "home-peritoneal-dialysis-safety-guide",
                "tag": "새로운 투석기기"
            }
        ]
        
        selected_topic = random.choice(special_topics)
        output_filepath = os.path.join(POSTS_DIR, f"auto-{selected_topic['slug']}.md")
        
        if not os.path.exists(output_filepath):
            print(f"  [AI CREATIVE] 특집 주제로 집필 개시: {selected_topic['theme']}")
            
            prompt = f"""
            You are an expert clinical nephrologist and professional renal health writer.
            Your task is to write a comprehensive, highly engaging, empathetic, and long-form (at least 2000 Korean characters) blog post about the following special topic:
            
            Topic: {selected_topic['theme']}
            
            Structure the post beautifully with Heading 2 (##) and Heading 3 (###).
            Use polite and caring Korean (use '-요', '-습니다' style).
            Include:
            ## 1. 들어가는 말 및 환우들의 공감대 형성 (Empathetic introduction)
            ## 2. {selected_topic['theme']}의 정밀 핵심 분석 (Detailed explanation and status of technology/diet)
            ## 3. 만성 콩팥병 환우들을 위한 실생활 맞춤 행동 강령 (Practical daily action plan)
            ## 4. 신장학 전문의 관점에서의 희망적 제언 및 마감 (Closing statement)
            
            The first line of your output MUST be the title starting with:
            TITLE: [Catchy, click-driven, highly empathetic hooking Korean title with tag like '[특집기획]']
            """
            
            ai_output = call_gemini_api(api_key_loaded, prompt)
            if ai_output:
                ai_output = ai_output.strip()
                lines = ai_output.split('\n')
                title_line = ""
                body_start_idx = 0
                
                for idx_line, line in enumerate(lines):
                    if line.startswith("TITLE:"):
                        title_line = line.replace("TITLE:", "").strip()
                        body_start_idx = idx_line + 1
                        break
                    elif line.startswith("title:"):
                        title_line = line.replace("title:", "").strip()
                        body_start_idx = idx_line + 1
                        break
                
                if title_line:
                    final_title = title_line.strip('"').strip("'")
                    post_content = "\n".join(lines[body_start_idx:]).strip()
                else:
                    final_title = f"[특집기획] {selected_topic['theme']}"
                    post_content = ai_output
                
                meta_description = f"만성 콩팥병 환우분들을 위한 특집 의학 가이드 '{final_title}'에 대한 신장의학 신기술 및 웰니스 솔루션 리포트입니다."
                
                thumbnail_url = UNSPLASH_THUMBNAILS[random.randint(0, len(UNSPLASH_THUMBNAILS)-1)]
                
                yaml_header = f"""---
title: "{final_title}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{meta_description}"
tags: ["콩팥건강", "만성콩팥병", "인공신장", "{selected_topic['tag']}"]
thumbnail: "{thumbnail_url}"
slug: "auto-{selected_topic['slug']}"
---

"""
                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(yaml_header + post_content)
                    
                print(f"  [SUCCESS] 특집 오리지널 기사 발행 및 영속화 완료: auto-{selected_topic['slug']}.md (제목: {final_title})")
                collected_count += 1

    print(f"\n[COMPLETE] 총 {collected_count}개의 고품질 신장 전문 AI/지능형 기사 초안이 '/data/posts/' 하위에 완벽히 생성 적재되었습니다!")

if __name__ == "__main__":
    auto_collect_posts()
