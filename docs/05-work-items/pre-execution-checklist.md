# 사전 실행 체크리스트

이 체크리스트는 광주 공식 출처 기반 RAG 웹 데모를 넓게 구현하기 전에 먼저 닫아야 하는 gate다. 현재 단계는 개인 사전 탐색이며, 팀원 이름이나 secret 값을 요구하지 않는다. 모든 provider와 배포 가정은 첫 실행 이슈 또는 pre-execution gate에서 확인한 뒤 구현에 반영한다.

## 1. 모델 우선순위 결정 gate

첫 실행 이슈에서 OpenAI와 Gemini 중 어떤 모델을 우선 사용할지 결정한다. 결정 전에는 특정 provider를 코드나 문서의 고정 전제로 두지 않는다.

확인 항목:

- [ ] OpenAI와 Gemini의 사용 가능 계정, 무료/유료 한도, 결제 책임을 확인했다.
- [ ] 한국어 공식 문서 이해와 쉬운 한국어 변환 품질을 비교할 평가 질문을 정했다.
- [ ] 영어, 베트남어, 중국어 답변 품질을 비교할 대표 질문을 정했다.
- [ ] 출처 인용, 모르는 질문 거절, 개인정보 회피 응답을 비교한다.
- [ ] latency, timeout, rate limit, 비용 리스크를 기록한다.
- [ ] 1순위 provider와 fallback 또는 no-model failure policy를 이슈 acceptance criteria에 남긴다.

결정 산출물:

- 우선 provider
- fallback 가능 여부
- 모델명 후보
- 비용/쿼터 제한
- 실패 시 사용자 메시지
- 재검토 조건

## 2. 배포 계정과 권한 gate

Vercel/Render 중 실제 데모 배포가 가능한 경로를 첫 실행 또는 pre-execution 이슈에서 확인한다.

확인 항목:

- [ ] Vercel 또는 Render 계정 접근 권한이 있다.
- [ ] 필요한 경우 billing 설정 또는 무료 플랜 제한을 확인했다.
- [ ] 환경변수 등록 권한이 있다.
- [ ] 배포 로그 접근 권한이 있다.
- [ ] 도메인 또는 preview URL 공유 방식이 정해졌다.
- [ ] 빌드/런타임 timeout 제한을 확인했다.

주의:

- secret, API key, token, 개인 계정 비밀번호는 repo에 저장하지 않는다.
- `.env` 값은 문서에 실제 값으로 적지 않는다.
- 필요한 변수명만 예시로 적고 값은 배포 플랫폼 secret/env 관리에 둔다.

## 3. 데이터베이스와 RAG 저장소 gate

공식 출처 기반 MVP에 필요한 저장 방식을 먼저 결정한다.

확인 항목:

- [ ] 데모가 DB 없이 정적 JSON/파일 인덱스로 가능한지 확인했다.
- [ ] DB가 필요하면 무료 플랜, 지역, 연결 제한, 삭제 방법을 확인했다.
- [ ] vector store, 임베딩 캐시, 문서 chunk 저장 위치를 정했다.
- [ ] 공식 출처 URL, 수집일, 갱신일, 언어, 사용 조건을 기록한다.
- [ ] 개인정보가 문서 저장소에 들어가지 않도록 입력 로그 정책을 정했다.

권장 기본값:

- 개인 사전 탐색에서는 공식 문서 메타데이터와 공개 URL만 저장한다.
- 사용자 질문 로그는 기본적으로 저장하지 않는다.
- 저장이 필요하면 익명화, 최소 보관 기간, 삭제 절차를 먼저 문서화한다.

## 4. secrets와 환경변수 gate

확인 항목:

- [ ] 필요한 환경변수 이름만 정의했다.
- [ ] 실제 secret 값은 로컬/배포 플랫폼 secret store에만 둔다.
- [ ] client bundle에 노출되면 안 되는 key를 구분했다.
- [ ] GitHub issue, markdown, screenshot, log에 secret이 포함되지 않도록 확인한다.
- [ ] 데모 evidence를 만들 때 URL query, console log, network log에 key가 찍히지 않도록 한다.

예시 변수명:

- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `RAG_INDEX_PATH`
- `ALLOWED_ORIGINS`
- `REQUEST_TIMEOUT_MS`
- `RATE_LIMIT_WINDOW_MS`
- `RATE_LIMIT_MAX_REQUESTS`

위 변수명은 예시이며 실제 값은 repo에 기록하지 않는다.

## 5. API 안전성과 운영 gate

확인 항목:

- [ ] CORS 허용 origin을 명시했다.
- [ ] request body 크기 제한을 정했다.
- [ ] LLM 호출 timeout을 정했다.
- [ ] retry는 짧고 제한적으로만 사용한다.
- [ ] rate limit 기준을 정했다.
- [ ] provider 장애, quota 초과, timeout, 빈 검색 결과의 사용자 메시지를 정했다.
- [ ] 공식 출처가 없는 답변은 추측하지 않고 거절한다.
- [ ] 의료, 법률, 체류자격 등 민감한 판단은 공식 기관 문의를 안내한다.

안전한 실패 응답 원칙:

- 사용자를 비난하지 않는다.
- 모델 내부 오류를 그대로 노출하지 않는다.
- 출처가 없으면 없다고 말한다.
- 가능한 경우 공식 기관 링크나 문의 경로를 제공한다.
- 개인정보를 다시 요구하지 않는다.

## 6. 언어와 용어집 gate

확인 항목:

- [ ] 한국어 공식 원문 용어를 기준 용어로 둔다.
- [ ] 쉬운 한국어 설명 규칙을 정했다.
- [ ] 영어, 베트남어, 중국어 핵심 용어 번역 초안을 만든다.
- [ ] 행정 용어는 임의로 바꾸지 않고 출처와 함께 설명한다.
- [ ] 번역 불확실성이 있으면 공식 원문 링크를 우선 제공한다.

## 7. 첫 실행 이슈에 반드시 포함할 항목

첫 실행 이슈는 구현 착수 전에 다음 결정을 닫는다.

- OpenAI/Gemini 우선순위와 fallback 방침
- Vercel/Render 배포 가능 여부와 권한
- DB 또는 no-DB RAG 저장 방식
- secret/env var 관리 위치
- CORS, timeout, retry, rate limit 기준
- 안전한 모델 실패 응답
- 공식 출처 인벤토리와 다국어 용어집 초안 연결

완료 기준:

- provider와 deploy 선택이 추측이 아니라 확인된 계정/권한/제약에 기반한다.
- repo에 secret이 없다.
- 팀원 이름 없이도 레인, gate, evidence만으로 다음 구현 이슈를 열 수 있다.
