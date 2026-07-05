# MVP 아키텍처 경계

이 문서는 광주·호남 외국인 행정/생활 지원 RAG feasibility MVP의 구현 경계를 고정한다. 현재 단계는 개인 사전 탐색이며, 공식 출처·모델·배포 결정은 첫 실행 gate 이후에만 닫는다.

## 한 줄 구조

`Next.js frontend` → `FastAPI backend` → `official-source RAG layer` → `PostgreSQL/pgvector planning store`

## 컴포넌트 책임

| 영역 | MVP 책임 | 제외/보류 |
| --- | --- | --- |
| `frontend/` Next.js TypeScript | 질문 입력, 언어 선택, `/api/chat` 호출, 답변·출처·기관 카드 표시 | 사용자 계정, 관리자 기능, 결제, 원문 수집 UI |
| `backend/` FastAPI | `/health`, `/api/chat`, 요청 검증, 안전 거절, 향후 RAG 호출 경계 | 외부 LLM 실호출, 임의 출처 생성, raw 질문 저장 |
| RAG layer | 공식 출처 청크 검색, citation validation, 긴급/민감 라우팅 | 블로그/커뮤니티/개인 경험담 사용 |
| PostgreSQL/pgvector | 문서·청크·출처 메타데이터와 임베딩 저장 계획 | 첫 실행 전 운영 DB 의존, 개인정보 저장 |
| Privacy/Safety layer | 개인정보 최소화, raw input 비저장, 근거 부족 거절, 기관 handoff | 법률·의료·출입국 개인 최종 판단 |
| Admin UI | roadmap: 출처 검수, 청크 상태, citation validation 결과 확인 | MVP 필수 범위 아님 |

## 공식 출처 RAG 경계

- 근거는 `docs/planning/official-source-inventory.md`의 공식 출처 클래스만 사용한다.
- 실제 `source_url`, `source_hash`/`snapshot_id`, `checked_at`은 첫 실행 이슈에서 사람이 확인한 뒤 기록한다.
- `status=active`와 citation validation이 통과한 청크만 답변 근거로 쓴다.
- `stale` 또는 출처 부족이면 답변을 만들지 않고 기관 연결을 우선한다.
- 긴급 질문은 검색보다 `112`, `119`, `1345` 안내를 먼저 보여준다.

## 지원 언어

초기 API와 UI의 `language` 값은 아래만 허용한다.

- `ko`: 한국어
- `easy_ko`: 쉬운 한국어
- `en`: 영어
- `vi`: 베트남어
- `zh`: 중국어

한국어 공식 원문을 기준으로 삼고, 다국어 답변은 공식 번역 또는 검토된 용어집을 보조 근거로 사용한다.

## PostgreSQL/pgvector 계획 스키마

첫 구현 전까지는 계획 경계만 둔다. 운영 DB 생성은 deployment gate 이후에 한다.

| 테이블 후보 | 핵심 필드 | 목적 |
| --- | --- | --- |
| `official_sources` | `id`, `source_name`, `source_url`, `jurisdiction`, `language`, `status`, `checked_at`, `source_hash`/`snapshot_id` | 공식 출처 단위 추적 |
| `source_chunks` | `id`, `official_source_id`, `chunk_key`, `quote_text`, `page_or_section`, `embedding_model`, `embedding`, `created_at`, `checked_at` | 검색 청크와 인용 원문 |
| `representative_questions` | `question_key`, `language`, `topic`, `question_text`, `expected_behavior`, `safety_notes` | 대표 질문 seed와 기대 동작 |
| `representative_question_citations` | `representative_question_id`, `source_chunk_id`, `citation_purpose` | 대표 질문별 citation validation 연결 |

개인 질문 원문은 기본 저장하지 않는다. 필요해도 익명화, 최소 보관 기간, 삭제 절차를 먼저 문서화한다.

## Privacy/Safety 불변 조건

- raw 질문 저장 기본값은 `false`이고 retention 기본값은 `0`일이다.
- secret, API key, token, 개인 계정 비밀번호는 repo와 문서에 쓰지 않는다.
- 개인별 비자 가능 여부, 보험료 정당성, 의료 진단, 법률 판단을 단정하지 않는다.
- 출처가 없으면 추측하지 않고 `refuse_and_handoff`로 처리한다.
- 기관 카드와 긴급 연락처는 답변보다 우선될 수 있다.

## 로컬 확인 명령

루트 README는 아래 문서와 명령을 연결해야 한다.

```bash
cd frontend
npm install
npm run dev
npm run typecheck
```

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e .[test]
uvicorn app.main:app --reload
pytest
```

패키지 설치와 전체 gate 실행은 통합 검증자가 수행한다. 이 문서는 명령 위치만 고정한다.

## 첫 실행 전 유지할 gate

- 공식 출처 URL·해시·최신성 확인
- OpenAI/Gemini 또는 no-model fallback 결정
- Vercel/Render 계정·권한·timeout 확인
- DB 사용 여부와 pgvector 준비 확인
- CORS, timeout, retry, rate limit 기준 확정
- 데모 evidence와 발표 백업 파일 분리
