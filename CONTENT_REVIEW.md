# 콘텐츠 검토 기록

## 2026-07-18 저가치 콘텐츠 개선

### 공개 상태 정리

- 공개: 7편
- 검토 대기 초안: 2편
- 제외: 3편
- 출처와 검토 기록이 없던 `auto-breakthrough-research-extends-hope-for.md`, `auto-developing-kidneys-from-scratch.md`는 `draft`로 전환했습니다.
- 새 글과 기존 글 모두 `status`가 없으면 공개되지 않습니다.

### 발행 기준

`backend/scripts/content_rules.py`를 콘텐츠 감사와 JSON 빌드가 함께 사용합니다. 공개 글은 다음 조건을 모두 충족해야 합니다.

- 제목, 날짜, 설명, 태그, 대표 이미지, 슬러그와 명시적인 `status`
- 콘텐츠 유형, 편집자가 보완한 점, 검토 주체와 검토일
- 공백 제외 1,200자 이상, H2 3개 이상, `참고 자료` 섹션
- 진단·치료를 대신하지 않는다는 안내 또는 담당 의료진과 확인할 사항
- 연구 검토 글은 보도 원문과 1차 자료 URL 모두 필요

RSS 수집 글은 항상 `draft`로 저장되며 `editorial_value`, `reviewed_by`, `reviewed_at`을 운영자가 채우고 발행 기준을 통과하기 전에는 `posts.json`에 포함되지 않습니다.

### 새 원본 안내 글

| 파일 | 독자에게 제공하는 값 | 주요 근거 |
| --- | --- | --- |
| `egfr-uacr-test-results-guide.md` | eGFR과 UACR을 함께 보고 날짜별 추세를 질문하는 방법 | KDIGO 2024, NIDDK |
| `ckd-appointment-preparation-checklist.md` | 검사표·약 목록·증상·질문을 한 장에 준비하는 순서 | NIDDK |
| `dialysis-options-question-list.md` | 혈액투석과 복막투석을 의료·생활 조건으로 비교하는 12가지 질문 | NIDDK, 대한신장학회 |
| `kidney-medicine-list-safety.md` | 처방약·일반약·영양제·한약을 한 목록으로 점검하는 방법 | NIDDK |

각 글에는 재사용 가능한 자체 SVG 안내 도표를 추가했습니다. 외부 환자 사진이나 학회 자료 이미지를 복제하지 않았습니다.

### 사이트 신뢰 정보와 광고

- 소개 페이지에 개인 운영 블로그임을 밝히고 자료 편집 검토와 의료인 감수를 구분했습니다.
- `/ko/editorial-policy`에 자료 선택, AI 보조, 자동 수집, 감수, 광고, 정정 원칙을 공개했습니다.
- 글 상세 화면에 콘텐츠 유형, 발행일, 검토일, 편집 기여, 1차 자료를 표시합니다.
- 사이트맵에 편집 원칙 페이지와 글 대표 이미지를 포함했습니다.
- 광고 소유권 메타태그는 유지하되 광고 스크립트와 슬롯은 `NEXT_PUBLIC_ADSENSE_ENABLED=true`이고 광고 계정 ID가 설정된 경우에만 로드됩니다.

### 저부하 검증 결과

- `python backend/scripts/audit_content.py --strict`: 오류 0, 경고 0
- `python backend/scripts/build_data.py`: 공개 글 7편 생성
- 사용자 요청에 따라 Next.js 프로덕션 빌드, 개발 서버, 브라우저 렌더링과 스크린샷 검사는 실행하지 않습니다.

배포 전에는 `.env.example`을 참고해 실제 연락 이메일과 사이트 URL을 설정하고, 운영자가 모바일·데스크톱 화면과 링크를 직접 확인해야 합니다.

---

- 검토일: 2026-07-13
- 기준 브랜치: `main`
- 검토 기준 커밋: `fdf32f7`
- 검토 범위: Git 변경 이력, Markdown 게시물, RSS 수집기, 정적 데이터 빌드, 의료 표현, SEO 메타데이터

## 확인된 문제

1. 마지막 커밋의 수집기에서 정의되지 않은 `promptRules` 변수를 사용해 API 키가 설정된 실행에서 `NameError`가 발생했습니다.
2. Medical Xpress의 기존 RSS 주소가 404를 반환하고 있었습니다. 공식 Nephrology News 피드 주소로 교체했습니다.
3. 과거 수집기는 원문 URL과 검토 상태를 저장하지 않았습니다. 기존 게시 글 2개는 일반적인 설명과 면책 문구는 갖췄지만 연구 원문과 근거 수준을 확인할 수 없습니다.
4. 과거 프롬프트는 신장내과 전문의 경력과 진료 경험을 꾸며냈습니다. 현재 본문에서는 해당 표현이 제거됐습니다.
5. 홈페이지가 나트륨·칼륨·인·단백질 제한을 모든 독자에게 적용되는 원칙처럼 표현해 개인별 검사와 치료 단계에 따른 차이가 충분히 드러나지 않았습니다.
6. 초안과 게시 완료 글을 구분하지 않아 자동 생성 직후 의료 글이 공개될 가능성이 있었습니다.

## 이번 수집 및 판정

| 상태 | 파일 | 판정 |
| --- | --- | --- |
| 게시 | `auto-first-e-star-annual-report-offers.md` | E-STAR 보고서의 표본·지역·단계별 수치 확인 후 재작성 |
| 게시 | `auto-oxalate-buildup-triggers-systemic-inflammation-and.md` | 동물실험과 제한적인 사람 자료를 구분해 재작성 |
| 게시 | `auto-womb-fluid-infusions-help-fetuses-with.md` | JAMA RAFT 임상시험의 대상·결과·한계를 확인해 재작성 |
| 제외 | `auto-an-11-year-old-needed-two.md` | 심장·간 이식 사례로 편집 범위와 무관 |
| 제외 | `auto-first-full-characterization-of-kidney-microbiome.md` | 2024년 자료이며 현재 투석·CKD 편집 범위와 거리가 있음 |
| 제외 | `auto-why-drinking-more-water-didn-t.md` | 신장결석 중심이며 수분 섭취 이행도 등 원문 검토가 부족함 |

## 남은 검토 대기열

- `auto-breakthrough-research-extends-hope-for.md`: 연구 원문, 연구 단계, 대상과 결과를 복구한 뒤 보강 필요
- `auto-developing-kidneys-from-scratch.md`: 오가노이드·재생 연구의 원문과 임상 적용 단계를 확인한 뒤 보강 필요

`python backend/scripts/audit_content.py`로 출처, 검토일, 본문 분량, 의료 면책 문구를 확인할 수 있습니다. 새 수집 글은 `draft`로 저장되며, 원문과 논문을 확인해 `published`와 `reviewed_at`을 명시하기 전에는 사이트 데이터에 포함되지 않습니다.
