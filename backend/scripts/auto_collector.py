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
    
    # 1. 대괄호 안의 주제어 우선 추출
    brackets = re.findall(r'\[(.*?)\]', title)
    if brackets:
        return brackets[0]
        
    # 2. 콜론 앞부분 주제어 추출
    if ":" in title:
        part = title.split(":", 1)[0].strip()
        if len(part) < 30:
            title = part
            
    # 3. 영어 타이틀인 경우 (원문 제목 처리)
    words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', title)
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
                "Drug": "신약 개발", "Diabetes": "당뇨병성 신증", "Hypertension": "고혈압"
            }
            if english_subject in eng_ko_map:
                return eng_ko_map[english_subject]
            if english_subject.lower() in ['her', 'his', 'brother', 'sister', 'child', 'boy', 'girl', 'year']:
                return "소아 장기 이식"
            return english_subject

    # 4. 한국어 번역 타이틀인 경우 (번역된 제목 처리)
    korean_words = re.findall(r'\b[가-힣]{2,8}\b', title)
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
            "언니": "장기 기증", "동생": "장기 기증", "가족": "가족 건강"
        }
        if candidate in subject_replace_map:
            return subject_replace_map[candidate]
            
        return candidate
        
    return "만성 콩팥병 관리"

def make_hooking_title_kidney(translated_title, subject):
    """
    신장 블로그용 밋밋한 의학 기사 번역 제목을 환우와 가족분들의 눈길을 사로잡는 강력한 후킹 제목으로 변환합니다.
    """
    prefixes = [
        "[환우필독]", "[식이수칙]", "[비상경고]", "[기적의 콩팥]", "[의학포커스]", 
        "[건강비책]", "[사구체수호]", "[긴급경보]", "[생명정보]", "[식탁혁명]"
    ]
    suffixes = [
        "절대 놓쳐선 안 되는 이유!", "콩팥을 수호하는 핵심 열쇠!", "이대로 두면 위험합니다!",
        "지금 당장 확인해야 할 건강 법칙!", "평생 콩팥 수호하는 지름길!", "소리 없는 사구체 침공을 막아라!"
    ]
    
    # 제목 다듬기
    title_clean = translated_title.replace("콩팥 가이드", "").replace("[콩팥 가이드]", "").replace("콩팥 건강", "").replace("[콩팥 건강]", "").strip()
    title_clean = re.sub(r'^["\'\[\(]+', '', title_clean)
    title_clean = re.sub(r'["\'\]\)]+$', '', title_clean)
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    formats = [
        f"{prefix} '{subject}'이 콩팥을 살린다? {title_clean}의 비밀",
        f"{prefix} 당장 밥상에서 빼세요! {title_clean} - {suffix}",
        f"{prefix} 콩팥 환우들이 눈물 흘린 극적 연구: {title_clean}!",
        f"'{subject}' 관리 안 하면 콩팥 망가집니다! {prefix} {title_clean}",
        f"{prefix} '{subject}'에 대한 신장내과 긴급 경보: {title_clean}!"
    ]
    
    return random.choice(formats)

def generate_dynamic_free_content(feed_name, link, translated_title, translated_body):
    """
    무료 번역 모드 시, 기사 주제에 최적화된 100% 차별화된 템플릿을 선택하여
    중복 노출을 완벽하게 예방하는 초고품질 콩팥 건강 리포트를 완성합니다.
    """
    subject = extract_main_subject(translated_title)
    subject_lower = subject.lower()
    
    # 1. 주제 분석을 통한 맞춤형 4대 콩팥 식이 헌법 분기 수립 (중복 제거 핵심)
    if any(x in subject_lower for x in ['water', 'stone', 'urology', '결석', '비뇨기', '물', '음수', '체액', '붓기', '부종']):
        # 유형 A: 수분 공급 / 결석 조절 형 맞춤형 가이드라인
        diet_guidelines = f"""이번 **{subject}** 소식은 결석 예방과 적절한 체액 순환 조절 측면에서 만성 콩팥병 환우들에게 깊은 의학적 인사이트를 전달합니다. 콩팥 사구체를 무결하게 수호하기 위한 식이 4대 원칙은 다음과 같습니다:

1. **저나트륨 & 수분 제어 철칙 (Low Sodium)**
   * **원리**: 나트륨 섭취가 늘어나면 소변 내 칼슘 배출이 늘어나 결석의 씨앗이 되며, 혈압이 오르면 사구체 여과율이 파괴됩니다.
   * **실천 노하우**: 국과 찌개의 국물은 엄격하게 남기시고, 물을 드실 때는 차가운 물보다 미지근한 맹물을 하루 주치의 권장량(보통 1~1.5L, 투석 환우는 극소량 계량 섭취)에 맞춰 조금씩 자주 나눠서 드셔야 합니다.

2. **수산 차단 & 저칼륨 섭취 (Low Potassium)**
   * **원리**: 결석의 주요 성분인 수산이 칼륨이 풍부한 시금치, 근대 등에 많으므로 이에 대한 주의가 생명선입니다.
   * **실천 노하우**: 이번 {subject} 관련 식재료 및 채소를 섭취할 때는 반드시 **칼륨과 수산을 빼내기 위해 잘게 썰어 미지근한 물에 2시간 이상 담가두거나 데친 물을 꼭 짜낸 뒤** 요리해서 드셔야 안전합니다.

3. **칼슘-인 균형 저인 관리 (Low Phosphorus)**
   * **원리**: 인 수치가 과도하게 오르면 가려움증을 유발하고 뼈에서 칼슘을 빼내어 신장에 결석을 촉진하는 독이 됩니다.
   * **실천 노하우**: 가공식품의 식품첨가물 속 인산염은 거의 100% 흡수되므로 철저히 피하시고, 현미나 잡곡 대신 정제된 흰쌀밥 위주로 식사해야 {subject} 환경 속 인과 칼슘의 대사가 조화롭게 유지됩니다.

4. **사구체 보호 저단백 식사 (Low Protein)**
   * **원리**: 단백질 대사 노폐물이 걸러지지 못하면 소변이 산성화되어 결석 형성을 돕고 신장 사구체에 무리한 부하를 가합니다.
   * **실천 노하우**: {subject} 상태 관리를 위해 전체 단백질의 섭취 총량을 제한하되, 계란 흰자, 생선, 닭가슴살, 살코기 등 찌꺼기가 적은 고효율 동물성 단백질 위주로 아주 적게 섭취하여 노폐물 축적을 원천 예방해야 합니다."""
        
    elif any(x in subject_lower for x in ['diet', 'nutrition', 'protein', 'bean', '식이', '영양', '단백질', '콩', '식사', '식품', '음식']):
        # 유형 B: 정밀 식단 구성 / 영양소 섭취 형 맞춤형 가이드라인
        diet_guidelines = f"""영양학적 조절 요령을 다루고 있는 **{subject}** 소식은 매일 식탁에서 접하는 영양 가치 측면에서 환우들의 요독증 관리에 대단히 귀중한 기준을 제공합니다. 콩팥 식탁의 평화를 위한 식이 4대 원칙은 다음과 같습니다:

1. **천연 양념을 활용한 저나트륨 식단 (Low Sodium)**
   * **원리**: 나트륨을 극도로 배제하면서도 맛을 잃지 않는 요리 지혜가 식단 유지의 원동력입니다.
   * **실천 노하우**: 가공 햄, 라면, 통조림은 영구 배제하시고, 간장이나 소금 대신 레몬즙, 마늘, 식초, 와사비, 파 등의 천연 조미료로 맛을 내면 싱거우면서도 {subject} 걱정 없는 고품격 식단을 유지할 수 있습니다.

2. **칼륨 수치 안전 통제 (Low Potassium)**
   * **원리**: 콩류와 견과류, 신선한 과채류에는 칼륨이 극도로 많아 신부전 환자에게 고칼륨혈증 부정맥 위험을 안겨줍니다.
   * **실천 노하우**: 콩이나 팥, 잡곡밥은 수용성 칼륨이 많으므로 엄격히 제어하고 가급적 정제된 백미로 식사하셔야 합니다. {subject} 예방을 위해 바나나, 토마토, 수박 등 생과일 또한 일체 금지하거나 임상영양사의 처방에 따라 아주 극소량만 드셔야 합니다.

3. **식품 첨가물 배제 저인 관리 (Low Phosphorus)**
   * **원리**: 가공 훈제육이나 콜라 같은 탄산음료에 든 가공 인은 신장에서 거의 걸러지지 않아 환우의 혈관을 석회화시키는 주범입니다.
   * **실천 노하우**: 치즈, 요플레 등 유제품도 인 함량이 높아 제한 섭취하며, {subject} 식단 시 신선한 자연 식재료 위주로 조리하여 식사함으로써 체내에 인산염 노폐물이 쌓이는 일을 완벽히 차단해야 합니다.

4. **적절한 양질의 저단백 처방 (Low Protein)**
   * **원리**: 무조건적인 단백질 단식은 근손실을 부르므로, 신장에 무리를 주지 않는 선에서 최상의 양질 단백질을 섭취하는 고난도 튜닝이 요구됩니다.
   * **실천 노하우**: 매 끼니마다 계란 흰자 1~2개 또는 껍질 벗긴 닭가슴살 40g 정도의 맑은 단백질만 선별 섭취하여 요독 생성을 최소화하고 {subject}의 위험도를 극적으로 낮춰야 합니다."""

    else:
        # 유형 C: 전염병/면역/예방접종/만성 질환 전반 관리형 가이드라인
        diet_guidelines = f"""체내 방어 기제와 신체 전반의 염증 관리를 다루는 **{subject}** 소식은 외부 유해 위험으로부터 신장 기능을 견고히 방어하기 위해 만성 콩팥병 환우들이 매일 준수해야 할 필수 지표를 제공합니다:

1. **접종 및 전신 피로 차단 저나트륨 (Low Sodium)**
   * **원리**: 체내 나트륨 수치가 불안정하면 면역 저하 시 신체 부종과 신장 필터의 염증 반응이 더 가파르게 촉발됩니다.
   * **실천 노하우**: 찌개나 국의 국물 섭취를 0%에 가깝게 끊어내 혈압의 미세 동요를 원천 제어하고, {subject} 예방 차원의 충분한 안식과 가벼운 스트레칭으로 신체의 전신 피로를 사전에 씻어내 주셔야 합니다.

2. **면역 저하 시 고칼륨혈증 차단 (Low Potassium)**
   * **원리**: 신체가 비상 상태에 들어가 면역 세포가 자극을 받으면 혈액 내 칼륨 항상성이 흔들리기 쉬워 고칼륨혈증 부정맥 위협이 상승합니다.
   * **실천 노하우**: 생과일 주스나 야채 즙은 콩팥에 직접적인 독을 붓는 것과 같으므로 일체 멀리하셔야 하며, {subject} 상황 발생 시 모든 채소는 반드시 끓는 물에 정성껏 데쳐서 칼륨을 빼낸 후 드셔야 합니다.

3. **골대사 부하 방지 저인 수칙 (Low Phosphorus)**
   * **원리**: 면역력 쇠약 단계에서 뼈 조직이 무너지지 않도록 호르몬 균형(인 수치 통제)을 사수해야 2차 신성 골다공증 합병증을 차단합니다.
   * **실천 노하우**: 가공 소시지나 즉석밥 속 보존제로 쓰이는 산도조절제(인산염)를 피하기 위해, 가급적 직접 갓 지은 쌀밥과 천연 채소 요리로 {subject}에 안전한 자연식 식탁을 엄수해 주셔야 합니다.

4. **요독 합병증 차단 저단백 생활 (Low Protein)**
   * **원리**: 요독 수치가 쌓이면 뇌와 심장에 요독성 독소가 작용하여 염증 반응과 면역력을 급격히 붕괴시키는 악순환을 초래합니다.
   * **실천 노하우**: 단백질 대사 노폐물이 걸러지지 않는 위험을 줄이기 위해, {subject} 노출 시 주치의 권장 단백질 섭취 농도(체중 1kg당 0.6~0.8g)를 정교하게 저울로 계량하여 섭취하는 지혜가 필요합니다."""

    # 주제별 맞춤형 분석 인사이트 제공
    insight_templates = [
        f"""이번 보도된 {subject} 소식은 만성 콩팥병 환우들의 건강 유지와 신장 필터 보존에 매우 중대한 예방학적 메시지를 던지고 있습니다. 사구체 손상을 원천적으로 방지하고 일상에서 건강 에너지를 지속하기 위한 핵심 분석은 다음과 같습니다:
* **면역 및 전신 관리의 정석**: 신장 기능이 저하되면 신체의 방어 기제와 면역 체계가 매우 취약해집니다. 이번 {subject} 이슈는 가벼운 생활 관리 하나가 콩팥 기능 보존에 미치는 누적 효과가 얼마나 거대한지 증명합니다.
* **약물 및 건강보조제 복용 시 극도의 주의**: 콩팥은 몸에 들어오는 모든 물질을 필터링하므로, 검증되지 않은 민간요법의 약초 즙, 고함량 비타민, 건강 보조식품은 오히려 사구체를 급격히 손상시키는 독이 될 수 있습니다. 반드시 주치의와 상의한 처방 약품만 복용해야 합니다.""",

        f"""새롭게 조명된 {subject} 연구 결과는 만성 신부전 환우들이 일상 속에서 마주하는 스트레스와 치료 경로에 명확한 이정표를 쥐여줍니다. 콩팥의 장기적 안정을 도모하기 위한 구체적인 임상적 시사점은 아래와 같습니다:
* **혈압과 혈당의 수호**: {subject} 생태계에서 가장 기본이 되는 관리는 바로 2대 만성 질환인 혈압과 당뇨의 철저한 조절입니다. 가정용 혈압계를 구비하여 수시로 체크하고, 수축기 혈압 130mmHg 미만 유지를 생활화해야 합니다.
* **가벼운 걷기와 규칙적 수분 조절**: 투석 전 단계 환우분의 경우 주치의 처방 범위 내에서 하루 적정량의 깨끗한 맹물을 섭취하여 탈수를 예방하되, 투석 단계 환우분은 수분 정체로 인한 부종 및 폐부종을 막기 위해 음수량을 엄격히 계량 조절해야 합니다."""
    ]
    
    conclusion_templates = [
        f"""이번 {subject} 의학 뉴스는 콩팥 기능 회복의 터널을 지나고 계신 수많은 환우 및 가족분들께 일상 속 작은 습관의 변화가 기적 같은 치료 효과를 만들어 낼 수 있음을 보여주는 든든한 나침반입니다. 앞으로도 콩팥 건강의 동반자로서 세계적인 신장의학 데이터를 검증하여 따뜻하고 유익한 건강 보고서로 보답하겠습니다.""",
        
        f"""결론적으로 {subject}의 임상적 실천 지표는 콩팥의 골든타임을 완벽하게 수호하려는 분들께 매우 실효성 높은 건강 지침입니다. 저나트륨, 저칼륨, 저인, 저단백의 정석 식단을 매일 기쁘게 실천하시며 건강하고 활기찬 '콩팥 라이프'를 가꾸어 나가시기를 늘 마음 깊이 응원합니다."""
    ]
    
    hash_seed = len(translated_title) + len(translated_body)
    selected_insight = insight_templates[hash_seed % len(insight_templates)]
    selected_conclusion = conclusion_templates[(hash_seed + 3) % len(conclusion_templates)]
    
    post_content = f"""
만성 콩팥병 및 신장 건강의 든든한 동반자이자 과학적 건강 가이드를 제시하는 **[{feed_name}]**의 최신 보도 정보를 만성 콩팥병 환우와 가족분들의 안전한 생활 관리를 돕기 위해 정밀 편찬한 헬스 리포트입니다.

---

## 1. 최신 의학 리포트 요약 및 팩트 체크
해당 학술 소식이 다루고 있는 핵심 연구 결과 및 의학 정보의 핵심 번역 요약은 다음과 같습니다:

> **[주요 팩트 요약]**
> {translated_body}

*이 최신 의학 정보는 콩팥 사구체 여과율의 안정적 보존과 전신 염증 예방에 기여할 수 있는 중요한 흐름을 담고 있습니다. 상세한 연구 전문 및 임상 시험 데이터를 열람하시려면 하단에 기재된 공식 출처 링크를 적극 참고해 보시길 권장합니다.*

---

## 2. 만성 콩팥병 환우를 위한 핵심 건강 수칙
이번에 발표된 **{subject}** 소식과 연계하여, 만성 콩팥병 환우분들이 일상생활 속에서 안전을 확보하고 신장 기능을 최상으로 보호하기 위해 실천해야 할 구체적인 지침입니다:

{selected_insight}

---

## 3. 콩팥 라이프 식이 4대 원칙 맞춤형 케어
신장 건강 수호의 절대적 기준이자 신체 기능 부하를 원천 차단하기 위해 매일 식탁에서 준수해야 하는 식이요법의 정석입니다:

{diet_guidelines}

---

## 4. 결론 및 신장 전문의 관점의 시사점
{selected_conclusion}

*본 헬스 리포트는 [{feed_name}]({link})의 공식 RSS 발행 자료를 바탕으로 올바른 의학 정보 제공을 위해 저작권 가이드라인을 철저히 준수하여 정밀 번역 및 전문 콩팥 관리 지식을 융합해 작성되었습니다. 개인의 병증 단계에 따른 구체적인 약제 및 식단 적용은 반드시 담당 신장내과 전문의 및 임상영양사와의 상세한 상담을 우선적으로 거치셔야 합니다.*
"""
    return post_content

def call_gemini_api(api_key, prompt):
    """
    구글 최신 Gemini 2.5 Flash API를 활용하여 콩팥 식이법에 부합하는 오리지널 완전 창작글을 집필합니다.
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
        print(f"  [Gemini API Error] 네트워크 장애 또는 API 무응답: {e}")
        return None

def auto_collect_posts():
    # 수집 정보 (의학적으로 공신력과 무결한 가동성이 입증된 글로벌 메이저 헬스 RSS 피드 매칭)
    feeds = [
        {"name": "ScienceDaily Kidney Disease", "url": "https://www.sciencedaily.com/rss/health_medicine/kidney_disease.xml"},
        {"name": "ScienceDaily Nutrition", "url": "https://www.sciencedaily.com/rss/health_medicine/nutrition.xml"},
        {"name": "WHO Health News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
        {"name": "CDC Newsroom", "url": "https://www.cdc.gov/media/feed.xml"}
    ]
    
    # 윈도우 환경 편의성 대폭 개선: 시스템 환경 변수 외에도 프로젝트 루트의 .env 파일 자동 로딩 및 주입
    # [BOM 철통 방어]: utf-8-sig 코덱을 사용하여 파워쉘에서 생성한 UTF-8 BOM 파일도 무결 감지합니다.
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
                                    print(f"  [INFO] 로컬 설정 파일({os.path.basename(env_file)})에서 GEMINI_API_KEY 자동 로드 완료!")
                                    break
                except Exception as e:
                    print(f"  [WARNING] 로컬 설정 파일 파싱 중 오류: {e}")
            if api_key:
                break
                
    print("[INFO] 만성 콩팥병 및 신장 건강 전문 AI/지능형 자동 수집 파이프라인 가동!")
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # [품질 보장 조치]: 콘텐츠 영구 누적을 위해 이전 자동 파일 청소 단계를 배제합니다.
    print("[INFO] 콘텐츠 영구 누적을 위해 이전 자동 파일 청소 단계를 배제합니다.")
    
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
            
            if api_key:
                # [모드 A] Gemini 2.5 Flash를 가동한 100% 완전 창작 오리지널 콩팥 전문 힐링 포스팅 모드
                print("  [AI MODE] Gemini 2.5 Flash 신장의학/영양학 전문 창작 에디팅 기동...")
                
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
                
                ai_output = call_gemini_api(api_key, prompt)
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
                        final_title = make_hooking_title_kidney(title, subject)
                        post_content = ai_output
                        
                    meta_description = f"최신 글로벌 콩팥 의학 소식 '{final_title}'에 대한 신장 전문의 관점의 독창적인 해석 및 케어 가이드 리포트입니다."
                else:
                    api_key = "" # API 통신 실패 시 모드 B로 대체 기동
                    
            if not api_key:
                # [모드 B] 구글 번역 + 신장 전문 인텔리전트 동적 매핑 엔진 (출처 정확히 명시 모드)
                print("  [FREE MODE] 무료 신장 전문 지능형 동적 매핑 엔진 집필 기동...")
                translator = GoogleTranslator(source='en', target='ko')
                
                try:
                    # 제목 번역
                    translated_title = translator.translate(title)
                    # 요약 본문 번역
                    translated_body = translator.translate(cleaned_summary[:4500])
                    
                    # 호기심 유발형 타이틀 빌더 적용
                    final_title = make_hooking_title_kidney(translated_title, subject)
                    
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
            
    print(f"\n[COMPLETE] 총 {collected_count}개의 고품질 신장 전문 AI/지능형 기사 초안이 '/data/posts/' 하위에 완벽히 생성 적재되었습니다!")

if __name__ == "__main__":
    auto_collect_posts()
