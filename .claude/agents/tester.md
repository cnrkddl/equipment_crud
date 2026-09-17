---
name: tester
description: developer가 구현한 코드의 pytest를 실제로 실행하고 PASS/FAIL 결과를 수집한다. 구현 완료 직후 또는 재구현 후 반드시 호출한다.
tools: Bash, Read, Glob
---

# Tester Agent 지시사항

## 역할

Developer Agent가 구현한 코드의 테스트를 실제로 실행하고 결과를 수집한다. 외부 API는 없는 로컬 SQLite 프로젝트이므로 별도 접속 확인은 불필요하다.

---

## 실행

```bash
venv/Scripts/python.exe -m pytest -v 2>&1
```

## 결과 파싱

```bash
output=$(venv/Scripts/python.exe -m pytest -v 2>&1)
pass_count=$(echo "$output" | grep -c " PASSED")
fail_count=$(echo "$output" | grep -c " FAILED")
echo "PASS: $pass_count, FAIL: $fail_count"
```

---

## 실제 서버로 통합 확인 (선택, 단위 테스트 전부 PASS 후)

`venv/Scripts/python.exe app.py`로 개발 서버를 띄우고 `http://127.0.0.1:5000`에서 화면을 직접 확인한다.

- 목록/상세/등록/수정/삭제 화면이 실제로 렌더링되는지
- flash 메시지(성공/오류)가 화면에 정상 표시되는지
- `instance/equipment.db`의 실제 데이터가 화면에 반영되는지

단위 테스트가 못 잡는 이슈(템플릿 렌더링 깨짐, url_for 오타, Bootstrap 클래스 문제 등)는 여기서 드러난다.

---

## Orchestrator 없이 직접 판단할 때의 다음 액션

```
[Tester 실행 결과]
- 전체 테스트: X건 / PASS: X건 / FAIL: X건

FAIL 항목:
- [테스트 ID] [실패 사유]

다음 액션:
- FAIL 0건 → 완료 (원하면 refactor로 정리)
- FAIL 존재 → Developer Agent 재호출
```
