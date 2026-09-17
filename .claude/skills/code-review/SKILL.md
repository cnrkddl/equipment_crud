---
name: code-review
description: equipment_crud 변경사항을 표준(Standards) 축과 과제 지시서 준수(Spec) 축, 두 갈래로 리뷰. 기능 단위 커밋 전이나 "리뷰해줘" 요청 시 트리거.
---

# Code Review (2-axis) — equipment_crud

diff 하나를 **독립된 두 축**으로 평가한다. 서로 섞지 않고 따로 보고한다.

## 진행 순서

1. **비교 기준 확정** — 사용자가 지정한 커밋/브랜치/워킹트리 diff를 확인한다 (기본: `git diff HEAD` 또는 워킹트리). diff가 비어있으면 리뷰할 게 없다고 알린다.
2. **스펙 위치 확인** — 스펙 원본은 `Python 웹 CRUD 기본 과제 지시서.txt`다. 특히:
   - 5. 필수 구현 기능 (5-1~5-5: 등록/목록/상세/수정/삭제 각각의 "필수 조건")
   - 9. 입력값 검증 (필수값, 중복, 공백 trim, 존재하지 않는 ID, DB 저장 실패 처리)
3. **표준 소스 확인** — 이 저장소에 문서화된 컨벤션은 없으므로, 기존 코드(`app.py`, `models.py`)에서 이미 쓰이고 있는 패턴(snake_case 라우트 함수명, `models.py`에 모델 분리 등)을 기준으로 삼고, 아래 baseline 코드 스멜을 함께 적용한다: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest.
4. **두 축 평가**
   - **Standards**: PEP8 + 위 baseline 스멜 + 기존 코드 컨벤션과의 일관성. 400단어 이내.
   - **Spec**: 지시서 5번/9번 항목 대비 누락된 필수 조건, 그리고 지시서에 없는 범위(scope creep)를 지적. 400단어 이내.
5. **보고** — `## Standards`, `## Spec` 헤딩으로 분리해서 출력. 각 축 끝에 한 줄 요약 + 가장 심각한 이슈 하나를 명시.

## 원칙

- 두 축은 절대 합치지 않는다 — 하나가 다른 하나를 가리는 걸 막기 위함.
- 코드 스멜은 판단(judgement call)이고, 지시서 5/9번의 필수 조건은 하드 룰이다. 후자를 우선한다.
- scope creep(지시서에 없는 기능/화면)을 발견하면 Spec 축에서 지적하되, 삭제를 강제하지 말고 사용자에게 확인을 구한다.
