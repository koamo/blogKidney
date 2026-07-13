# 콘텐츠 검토 기록

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
