# 배포 Pre-check

Vercel/Render 배포는 공식 출처, 모델, DB, secret gate를 닫은 뒤에만 진행한다. 이 문서는 실행 전 확인 목록이며 실제 secret 값이나 개인 계정 정보는 기록하지 않는다.

## 배포 후보

| 영역 | 후보 | 확인 항목 |
| --- | --- | --- |
| Frontend | Vercel | `frontend/` root 설정, `NEXT_PUBLIC_API_BASE_URL`, preview URL 공유 방식, 빌드 timeout |
| Backend | Render Web Service | `backend/` root 설정, Python 3.11+, `uvicorn app.main:app`, CORS origin, request timeout |
| Database | Render PostgreSQL 또는 별도 PostgreSQL | pgvector extension 가능 여부, 무료 플랜 제한, region, 삭제 절차 |

Vercel/Render는 후보일 뿐이다. 실제 계정 접근권한과 비용/제한은 첫 실행 gate에서 확인한다.

## 로컬 install/test 명령

루트 README는 아래 명령으로 연결해야 한다.

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run typecheck
```

### Backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e .[test]
uvicorn app.main:app --reload
pytest
```

통합 전에는 프로젝트 전체 gate, package install, formatter를 반복 실행하지 않는다.

## 환경변수 이름

값은 로컬 `.env` 또는 배포 플랫폼 secret/env 관리에만 둔다. 문서, issue, screenshot, log에 실제 값을 쓰지 않는다.

### Frontend

| 변수 | 예시 값 형태 | 공개 가능 여부 | 설명 |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` 또는 backend URL | public | frontend bundle에 노출되는 API base |

### Backend

| 변수 | 예시 값 형태 | 공개 가능 여부 | 설명 |
| --- | --- | --- | --- |
| `LLM_PROVIDER` | `disabled`, `openai`, `gemini` | non-secret | provider gate 전 기본 `disabled` |
| `OPENAI_API_KEY` | 실제 값 기록 금지 | secret | OpenAI 선택 시에만 |
| `GEMINI_API_KEY` | 실제 값 기록 금지 | secret | Gemini 선택 시에만 |
| `DATABASE_URL` | 실제 값 기록 금지 | secret | PostgreSQL 연결 문자열 |
| `RAG_INDEX_PATH` | 내부 경로 | non-secret | no-DB 인덱스 또는 scaffold 판단 |
| `ALLOWED_ORIGINS` | comma-separated origins | non-secret | CORS 허용 origin |
| `REQUEST_TIMEOUT_MS` | number | non-secret | 전체 요청 timeout |
| `RATE_LIMIT_WINDOW_MS` | number | non-secret | rate limit window |
| `RATE_LIMIT_MAX_REQUESTS` | number | non-secret | window당 최대 요청 수 |
| `RAW_RETENTION_DAYS` | `0` | non-secret | raw 질문 저장 금지 기본값 |

## CORS 확인

- local frontend: `http://localhost:3000`
- preview frontend: Vercel preview URL
- production frontend: 실제 demo URL
- backend는 필요한 origin만 `ALLOWED_ORIGINS`에 둔다.
- wildcard `*`는 공개 demo 직전까지 사용하지 않는다.

## Timeout, retry, rate limit

첫 실행 gate에서 수치를 확정한다. 기본 방향은 아래와 같다.

| 항목 | 권장 방향 |
| --- | --- |
| request timeout | 짧게 시작하고 provider timeout을 사용자 메시지로 변환 |
| retry | 외부 provider에는 제한적 1회 이하, 사용자 입력 재전송 주의 |
| rate limit | IP 또는 세션 단위 최소 방어. 개인정보 저장 없이 집계 |
| body size | 질문 2000자 제한을 유지 |
| failure message | 내부 오류, provider 오류, stack trace 노출 금지 |

## DB/pgvector readiness

DB를 쓰기로 결정한 경우에만 진행한다.

- [ ] PostgreSQL 버전과 pgvector extension 사용 가능 여부 확인
- [ ] `CREATE EXTENSION vector;` 권한 확인
- [ ] region과 latency 확인
- [ ] 무료 플랜 sleep/connection limit 확인
- [ ] backup/export/delete 절차 확인
- [ ] `official_sources`, `source_chunks`, `representative_questions`, `representative_question_citations`, `institution_cards`, `audit_events` 계획 필드와 migration 전략 확인
- [ ] raw 사용자 질문 저장 금지 정책이 schema와 log 설정에 반영됐는지 확인

DB 없이 정적 JSON/파일 인덱스로 시작할 수 있으면 첫 데모에서는 no-DB를 우선 검토한다.

## 공식 출처 readiness

- [ ] HiKorea/법무부, 광주광역시, 광주외국인주민지원센터, 국민건강보험공단, 112, 119, 1345 공식 페이지 후보 확인
- [ ] 각 출처의 `source_url`, `checked_at`, `source_hash` 또는 `snapshot_id` 확보
- [ ] `status`를 `active`, `stale`, `retired`로 판정
- [ ] 대표 질문과 `quote_text` 연결 검증
- [ ] 비공식 출처가 인덱스에 섞이지 않았는지 확인

## No-secrets policy

금지:

- repo에 API key, token, password, DB URL 실제 값 저장
- markdown에 secret 값 예시 작성
- GitHub issue/screenshot/log에 secret 노출
- 팀원 이름, 개인 계정 식별자, 개인 연락처를 배포 requirement로 요구

허용:

- 변수명 문서화
- 플랫폼 secret store 사용 지시
- secret 존재 여부를 체크리스트로만 기록

## Evidence 분리

제품 경로와 발표 백업을 섞지 않는다.

| 구분 | 위치/형태 | 원칙 |
| --- | --- | --- |
| 제품 코드 | `frontend/`, `backend/` | 실행 가능한 MVP만 유지 |
| 제품 문서 | `docs/04-architecture/`, `docs/05-work-items/` | gate, contract, 공식 출처 증거 |
| 발표 백업 | 별도 presentation backup 또는 asset 경로 | 데모 캡처·슬라이드 원본. 제품 import 대상 아님 |
| 실행 evidence | issue comment, artifact, test output | secret 제거, raw 질문 최소화 |

`asset/`의 발표 자료는 제품 runtime 경로가 아니다. 제품 코드에서 발표 백업 파일을 import하거나 RAG 근거로 쓰지 않는다.

## 배포 전 stop/go 기준

Go:

- `/health`가 preview backend에서 정상 응답
- `/api/chat`이 scaffold refusal 또는 공식 출처 기반 응답만 반환
- frontend가 `NEXT_PUBLIC_API_BASE_URL`로 backend를 호출
- CORS origin이 preview URL과 일치
- secret 값이 repo와 evidence에 없음
- 공식 출처 gate 또는 scaffold refusal 정책이 명확함

Stop:

- 공식 출처 없이 citation이 생성됨
- raw 질문 저장 또는 logging 경로가 확인됨
- provider key가 client bundle에 들어감
- DB/pgvector 권한을 모른 채 migration을 실행해야 함
- Vercel/Render 계정·billing·권한이 불명확함
