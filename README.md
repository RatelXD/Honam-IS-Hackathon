# 호남·광주 공식 출처 RAG feasibility MVP

이 저장소는 호남/광주 지역 외국인 주민을 위한 행정·생활 지원 RAG 웹 데모의 개인 사전 feasibility/exploration 작업 공간입니다. 현재 목표는 공식 출처 기반 답변, 안전한 거절, 다국어 응답 가능성을 검증하는 최소 MVP 골격을 마련하는 것입니다. 팀 운영, 실제 배포, 외부 모델 호출, production 데이터 수집은 아직 범위 밖입니다.

## 범위와 원칙

- 공식 출처가 확인된 내용만 RAG 근거로 사용합니다.
- 블로그, 커뮤니티, 개인 경험담은 답변 근거로 사용하지 않습니다.
- 출처가 없거나 확신할 수 없는 질문은 추측하지 않고 안전하게 거절합니다.
- 사용자의 원문 질문이나 개인정보를 저장하지 않습니다.
- secret, API key, token, 개인 계정 비밀번호는 저장소에 커밋하지 않습니다.
- 모델 provider, 공식 출처, DB/RAG 저장 방식, 배포 가능 여부는 `docs/planning/`의 gate 문서에서 추적합니다.

## 작업 영역 경계

### Frontend: `frontend/`

Next.js TypeScript 데모 UI 영역입니다.

- 브라우저에 노출 가능한 설정만 사용합니다.
- API 주소는 `NEXT_PUBLIC_API_BASE_URL` 환경변수로 받습니다.
- 채팅 요청은 backend의 `/api/chat` 경로를 호출합니다.
- citation, 안전 거절 메시지, 지원 언어 선택 UI를 표현하는 데 집중합니다.

### Backend: `backend/`

FastAPI API 영역입니다.

- `/health`는 로컬 실행과 배포 상태 확인용입니다.
- `/api/chat`은 질문, 언어, 선택적 컨텍스트를 받아 안전한 scaffold 응답을 반환하는 경로입니다.
- 외부 LLM 호출은 gate가 닫히기 전까지 고정 전제로 두지 않습니다.
- raw user question 저장, fake citation 생성, secret 로그 출력은 금지합니다.

### Database: `database/`

PostgreSQL/pgvector 계획 스키마 영역입니다.

- 공식 출처, 검색 청크, 대표 질문, 기관 카드, 비식별 감사 이벤트를 설계합니다.
- 현재 스키마는 planning-grade skeleton이며 실제 운영 migration이 아닙니다.
- pgvector 사용 여부, 임베딩 모델, 보관 정책은 `docs/planning/` gate에서 확정합니다.

## 환경변수

`.env.example`에는 변수 이름만 둡니다. 실제 값은 로컬 `.env`, shell 환경변수, 또는 배포 플랫폼 secret/env 관리 기능에만 저장합니다.

클라이언트에 노출되는 변수는 `NEXT_PUBLIC_API_BASE_URL`뿐입니다. `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL` 같은 server-side secret은 frontend bundle에 들어가면 안 됩니다.

## Quick Start

로컬에서 백엔드와 프론트엔드를 함께 띄우는 최소 경로입니다.

터미널 1 - backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
uvicorn app.main:app --reload
```

터미널 2 - frontend:

```bash
npm install --workspace frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run frontend:dev
```

브라우저에서 `http://localhost:3000`을 열고 데모 질문을 실행합니다. backend 없이 frontend만 실행하면 화면은 명시적으로 표시된 local fallback sample을 보여주며 citation row를 만들지 않습니다.

## 로컬 setup 명령

아래 명령은 설치와 실행 위치를 문서화하기 위한 힌트입니다. 의존성이 아직 설치되어 있지 않으면 먼저 해당 디렉터리에서 설치해야 합니다.

### Frontend

```bash
npm install --workspace frontend
npm run frontend:dev
npm run frontend:build
npm run frontend:lint
npm run --workspace frontend typecheck
```

또는 frontend 디렉터리에서 직접 실행할 수 있습니다.

```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
uvicorn app.main:app --reload
python -m pytest
```

Backend 파일 구조나 dependency 이름이 바뀌면 위 명령도 함께 갱신합니다.

### Database

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

현재 `database/schema.sql`은 계획 스키마입니다. 실제 DB 적용 전에는 pgvector 확장, 권한, migration 도구, 데이터 보관 정책을 gate에서 확인합니다.

## planning gate

다음 결정과 evidence는 `docs/planning/` 아래 문서에서 관리합니다.

- 공식 출처 인벤토리와 최신성 확인
- 대표 질문과 citation validation
- OpenAI/Gemini 등 모델 provider 선택
- DB 또는 no-DB RAG 저장 방식
- CORS, timeout, retry, rate limit 기준
- secret/env var 관리 위치
- 배포 계정과 권한 확인

이 저장소의 MVP 코드는 위 gate가 닫히기 전까지 production-ready라고 주장하지 않습니다.

## 추가 문서

- `docs/architecture/mvp-boundaries.md`: MVP 컴포넌트 경계와 비범위
- `docs/architecture/api-contract.md`: `/health`, `/api/chat` 초기 계약
- `docs/architecture/deployment-precheck.md`: Vercel/Render, CORS, timeout, rate limit, DB/pgvector 사전 확인
