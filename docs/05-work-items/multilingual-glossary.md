# 다국어 용어집 시작 정책

## 목적

이 문서는 광주 초기정착 외국인 지원 RAG 웹 데모의 영어·베트남어·중국어 용어집을 시작하기 위한 정책이다. 한국어 공식 원문을 기준으로 삼고, 공식 번역과 기관 명칭을 우선 사용한다. 실제 URL·해시·스냅샷 근거는 첫 실행 이슈에서 공식 출처 인벤토리와 함께 채운다.

## 용어 채택 원칙

1. 한국어 공식 기관명과 제도명을 기준 키로 둔다.
2. 공식 영문·베트남어·중국어 번역이 존재하면 해당 번역을 우선한다.
3. 공식 번역이 없으면 임시 번역으로 표시하고, 첫 실행 이후 팀 리뷰에서 확정한다.
4. 법률·의료·출입국 결과를 단정하는 표현은 용어집에 넣지 않는다.
5. 같은 기관·제도는 UI, RAG 답변, 인용문에서 동일한 표현을 사용한다.
6. 쉬운 한국어가 필요한 경우 원문 용어를 보존하되 괄호 안에 쉬운 설명을 덧붙인다.

## 용어집 필드

| 필드 | 설명 |
| --- | --- |
| 한국어 기준어 | 공식 원문에 나타나는 기관명·제도명·상담 번호 |
| 쉬운 한국어 | 초급 한국어 사용자를 위한 짧은 설명 |
| English | 공식 또는 검토된 영어 표현 |
| Tiếng Việt | 공식 또는 검토된 베트남어 표현 |
| 中文 | 공식 또는 검토된 중국어 표현 |
| 출처 상태 | 공식 번역 확인 전에는 `first_execution_required` |
| 주의 | 금지 표현, 오해 가능성, handoff 필요성 |

## 초기 용어 후보

| 한국어 기준어 | 쉬운 한국어 | English | Tiếng Việt | 中文 | 출처 상태 | 주의 |
| --- | --- | --- | --- | --- | --- | --- |
| 광주광역시 | 광주 시청과 지역 행정기관 | Gwangju Metropolitan City | Thành phố Gwangju | 光州广域市 | first_execution_required | 공식 표기 확인 전 임의 약칭 금지 |
| 광주외국인주민지원센터 | 광주 외국인 상담·생활 지원 기관 | Gwangju Foreign Residents Support Center | Trung tâm hỗ trợ cư dân nước ngoài Gwangju | 光州外国居民支援中心 | first_execution_required | 센터 공식 다국어 명칭 확인 필요 |
| HiKorea | 출입국·체류 민원 포털 | HiKorea | HiKorea | HiKorea | first_execution_required | 서비스명을 번역하지 않고 고유명으로 유지 |
| 법무부 | 출입국 정책을 담당하는 중앙부처 | Ministry of Justice | Bộ Tư pháp | 法务部 | first_execution_required | 국가별 법무부와 혼동되지 않게 한국 기관임을 표시 |
| 국민건강보험공단 | 건강보험을 담당하는 공공기관 | National Health Insurance Service | Dịch vụ Bảo hiểm Y tế Quốc gia | 国民健康保险公团 | first_execution_required | 공식 영문 약칭 NHIS 사용 여부 확인 |
| 외국인등록 | 한국에 사는 외국인이 등록하는 절차 | Alien registration / foreigner registration | đăng ký người nước ngoài | 外国人登记 | first_execution_required | `alien`은 공식 문맥 외 사용 주의. UI에는 쉬운 표현 우선 |
| 체류자격 | 한국에 머무를 수 있는 자격 종류 | status of stay / visa status | tư cách lưu trú | 停留资格 | first_execution_required | 개인 가능 여부를 단정하는 답변과 분리 |
| 출입국·외국인청 | 출입국 업무를 보는 기관 | Immigration Office | Văn phòng xuất nhập cảnh | 出入境外国人厅 | first_execution_required | 관할 기관명은 실제 지역·업무별 확인 필요 |
| 1345 | 출입국·외국인 종합안내 전화 | Immigration Contact Center 1345 | Tổng đài tư vấn xuất nhập cảnh 1345 | 1345出入境外国人综合咨询中心 | first_execution_required | 운영시간·언어 지원은 첫 실행에서 공식 확인 |
| 112 | 경찰 긴급 신고 전화 | Police emergency number 112 | Số khẩn cấp cảnh sát 112 | 警察紧急电话112 | first_execution_required | 범죄·위협 상황에서는 일반 RAG보다 우선 |
| 119 | 화재·구조·구급 신고 전화 | Fire, rescue, and emergency medical number 119 | Số khẩn cấp cứu hỏa, cứu hộ và cấp cứu 119 | 火灾、救援、急救电话119 | first_execution_required | 의료 진단 대신 긴급 연락 안내 |
| 건강보험 | 병원비 부담을 줄이는 공적 보험 | national health insurance | bảo hiểm y tế quốc gia | 国民健康保险 | first_execution_required | 개인 보험료·자격 판단 금지 |
| 통번역 지원 | 말이나 문서를 다른 언어로 돕는 서비스 | interpretation and translation support | hỗ trợ phiên dịch và biên dịch | 口译和笔译支持 | first_execution_required | 제공 언어·시간을 과장하지 않음 |

## 금지·주의 번역

| 표현 | 문제 | 대체 정책 |
| --- | --- | --- |
| “비자가 승인됩니다”, “you will be approved” | 개인 출입국 결과 단정 | “공식 기관에서 확인해야 합니다”와 1345/HiKorea 연결 |
| “합법/불법입니다” | 개인 법률 판단 단정 | 공식 일반 안내와 전문기관·공공상담 handoff |
| “병원에 가지 않아도 됩니다” | 의료 위험 축소 | 긴급 증상은 119 또는 의료기관 문의 우선 |
| “무료입니다” | 비용 정책 변동 가능성 | 공식 출처에 비용이 명시된 경우에만 날짜와 함께 안내 |
| “always”, “guaranteed”, “확실히” | 제도·운영 변경 가능성 무시 | 확인일, 출처, 문의 경로를 함께 제공 |
| “외노자” 등 비하·낙인 표현 | 차별적 표현 | “외국인 주민”, “외국인 근로자” 등 공식·중립 표현 사용 |
| 기계번역식 기관명 혼용 | 같은 기관을 여러 이름으로 표시해 혼란 | 용어집 기준어 하나로 통일하고 공식 별칭만 허용 |

## 언어 품질 평가 기준

| 기준 | 통과 조건 |
| --- | --- |
| 공식성 | 기관명·제도명·전화번호가 공식 출처 또는 검토된 용어집과 일치 |
| 안전성 | 법률·의료·출입국 최종 판단을 피하고 필요한 경우 기관 handoff 제공 |
| 이해 가능성 | 초급 한국어 또는 비원어민 사용자가 핵심 행동을 이해할 수 있음 |
| 일관성 | 같은 용어가 UI, RAG 답변, 출처 인용에서 동일하게 사용됨 |
| 다국어 충실도 | 영어·베트남어·중국어가 한국어 원문의 범위를 과장하거나 축소하지 않음 |
| 최신성 | 첫 실행 이슈의 `checked_at`과 `source_hash`/`snapshot_id`가 연결됨 |
| 문화·차별 민감성 | 낙인, 비하, 공포 조장, 과도한 단정 표현이 없음 |

## 첫 실행에서 확정할 항목

- 공식 번역이 이미 존재하는 기관명·제도명 선별
- 공식 번역이 없는 항목의 임시 번역 표시와 리뷰 필요 표시
- 영어·베트남어·중국어별 native 또는 proficient reviewer 필요 여부
- 대표 질문 답변에서 실제로 사용된 용어와 용어집의 불일치 정리
- 출처 인벤토리의 `source_url`, `checked_at`, `source_hash` 또는 `snapshot_id`와 용어별 근거 연결
