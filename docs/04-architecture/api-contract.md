# 초기 API 계약

Backend 기준 경로는 `backend/`의 FastAPI 앱이다. Frontend는 `NEXT_PUBLIC_API_BASE_URL`을 읽어 future backend path `/api/chat`을 호출한다.

## 공통 원칙

- API는 raw 사용자 질문을 저장하지 않는다.
- 공식 출처가 없으면 답변을 만들지 않고 안전 거절과 기관 handoff를 반환한다.
- citation은 실제 공식 출처 확인 전에는 빈 배열이어야 한다.
- 외부 LLM 호출은 provider gate가 닫힌 뒤에만 켠다.
- 지원 언어는 `ko`, `easy_ko`, `en`, `vi`, `zh`만 허용한다.

## `GET /health`

서비스 상태와 scaffold 여부를 확인한다.

### Response `200`

```json
{
  "status": "ok",
  "service": "honam-rag-backend",
  "scaffold_only": true,
  "raw_retention_days": 0
}
```

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `status` | string | 정상 시 `ok` |
| `service` | string | 서비스 식별자 |
| `scaffold_only` | boolean | 실제 RAG/LLM 연결 전이면 `true` |
| `raw_retention_days` | number | raw 질문 보관 일수. 기본 `0` |

## `POST /api/chat`

질문을 검증하고, scaffold 단계에서는 안전 거절을 반환한다. RAG 연결 후에는 공식 출처 기반 답변만 반환한다.

### Request

```json
{
  "question": "광주에서 외국인등록은 어디서 확인하나요?",
  "language": "ko"
}
```

| 필드 | 타입 | 필수 | 제약 |
| --- | --- | --- | --- |
| `question` | string | yes | 1~2000자. raw 값 저장 금지 |
| `language` | enum | no | `ko`, `easy_ko`, `en`, `vi`, `zh`. 기본 `ko` |

### Response `200`

```json
{
  "answer": "공식 출처 확인 전에는 답변할 수 없습니다. 1345 또는 관할 기관에 문의하세요.",
  "language": "ko",
  "citations": [],
  "institution_cards": [
    {
      "name": "Immigration Contact Center 1345",
      "description": "출입국·체류 관련 공식 상담 경로입니다.",
      "phone": "1345",
      "url": null,
      "address": null
    }
  ],
  "emergency_cards": [],
  "safety": {
    "is_refusal": true,
    "scaffold_only": true,
    "raw_question_stored": false,
    "raw_retention_days": 0,
    "code": "scaffold_refusal",
    "guidance": ["No raw question was persisted."]
  }
}
```

현재 scaffold 구현도 `emergency_cards`와 `safety.code`를 응답 경계에 포함한다. 실제 긴급 분류와 카드 우선순위는 다음 RAG/safety 구현에서 확장한다.

## 응답 객체

### `Citation`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `title` | string | 공식 문서 또는 페이지 제목 |
| `url` | string URL | 공식 `source_url` |
| `institution` | string | 예: HiKorea, 광주광역시, 국민건강보험공단 |
| `retrieved_at` | string/null | 사용자가 볼 수 있는 확인 시각 또는 날짜 |
| `excerpt` | string/null | 답변에 연결되는 `quote_text` 일부 |
| `source_hash` | string/null | 첫 실행 gate에서 확보한 해시. 외부 공개가 부적절하면 내부 evidence에만 둔다 |
| `snapshot_id` | string/null | 해시 대신 쓰는 스냅샷 식별자 |
| `page_or_section` | string/null | 페이지, 제목, 섹션, 앵커 |

### `InstitutionCard`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `name` | string | 기관명 |
| `description` | string | 사용자가 선택할 수 있는 짧은 설명 |
| `phone` | string/null | 공식 전화번호. 예: `112`, `119`, `1345` |
| `url` | string URL/null | 공식 기관 URL |
| `address` | string/null | 필요할 때만 표시 |
| `reason` | string/null | 왜 이 기관을 보여주는지 |

### `EmergencyCard`

긴급·민감 질문에서 일반 답변보다 먼저 표시한다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `type` | enum | `police`, `fire_medical`, `immigration_hotline` |
| `phone` | string | `112`, `119`, `1345` |
| `priority` | number | 낮을수록 먼저 표시 |
| `message` | string | 사용자가 바로 이해할 안내 |

### `Safety`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `is_refusal` | boolean | 답변 거절 여부 |
| `detected_categories` | string[] | 감지된 안전·개인정보 category. 기본 `[]` |
| `redacted_question` | string | 서버 내부 처리용 비식별 질문. raw 질문 저장 대체물이 아니며 UI 노출은 최소화 |
| `scaffold_only` | boolean | scaffold 응답 여부 |
| `raw_question_stored` | boolean | 항상 명시. 기본 `false` |
| `raw_retention_days` | number | 기본 `0` |
| `code` | enum/null | 아래 safety code |
| `external_llm_enabled` | boolean | 현재 응답이 외부 LLM 사용을 허용했는지. MVP 기본 `false` |
| `provider_disabled` | boolean | provider 비활성/미사용 여부. MVP 기본 `true` |
| `guidance` | string[] | 사용자에게 보일 안전 안내 |

## Safety/Error code

| Code | HTTP | 의미 | 사용자 처리 |
| --- | --- | --- | --- |
| `scaffold_refusal` | 200 | 아직 RAG/LLM 미연결 | 기관 카드 표시 |
| `source_insufficient` | 200 | 공식 출처 부족 | 추측 금지, handoff |
| `emergency_first` | 200 | 긴급 가능성 | emergency card 우선 표시 |
| `personal_judgment_refusal` | 200 | 개인 법률·의료·보험·체류 판단 요청 | 범위 제한과 공식 상담 안내 |
| `validation_error` | 422 | 요청 형식 오류 | 입력 길이/언어 확인 |
| `rate_limited` | 429 | rate limit 초과 | 짧은 대기 후 재시도 |
| `timeout` | 504 | provider/RAG timeout | 재시도 버튼, raw 입력 저장 금지 |
| `provider_unavailable` | 503 | LLM/provider 장애 | 안전 실패 메시지 |
| `internal_error` | 500 | 알 수 없는 서버 오류 | 내부 상세 오류 노출 금지 |

## 저장 정책

- `question` raw 문자열은 DB, 로그, analytics, screenshot evidence에 저장하지 않는다.
- 문제 재현이 필요하면 익명화된 category, language, safety code, timestamp만 남긴다.
- 사용자 식별자, 팀원 이름, secret 값을 API payload나 evidence에 요구하지 않는다.

## 첫 실행 gate

이 계약은 아래 결정 전까지 scaffold contract다.

- 공식 출처별 URL·해시·`checked_at` 확정
- 모델 provider와 fallback 정책 확정
- DB/pgvector 또는 no-DB 인덱스 결정
- timeout, retry, rate limit 수치 확정
- citation validation 통과 기준 확정
