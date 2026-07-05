"use client";

import { useMemo, useState, type CSSProperties } from "react";

type LanguageCode = "ko" | "easy_ko" | "en" | "vi" | "zh";
type Scenario = "official_guidance" | "refusal_handoff" | "emergency_first";
type ResultState = "idle" | "loading" | "live" | "fallback" | "error";

type ChatRequest = {
  question: string;
  language: LanguageCode;
};

type Citation = {
  title: string;
  url: string;
  institution: string;
  retrieved_at: string | null;
  excerpt: string | null;
  source_hash: string | null;
  snapshot_id: string | null;
  page_or_section: string | null;
};

type InstitutionCard = {
  name: string;
  description: string;
  phone: string | null;
  url: string | null;
  address: string | null;
  reason: string | null;
};

type EmergencyCard = {
  type: string;
  phone: string;
  priority: number;
  message: string;
};

type Safety = {
  is_refusal: boolean;
  code: string;
  detected_categories: string[];
  redacted_question: string;
  raw_question_stored: boolean;
  raw_retention_days: number;
  scaffold_only: boolean;
  external_llm_enabled: boolean;
  provider_disabled: boolean;
  guidance: string[];
};

type ChatResponse = {
  answer: string;
  language: LanguageCode;
  citations: Citation[];
  institution_cards: InstitutionCard[];
  emergency_cards: EmergencyCard[];
  safety: Safety;
};

type LanguageOption = {
  code: LanguageCode;
  label: string;
  helper: string;
};

type ExampleQuestion = {
  id: string;
  scenario: Scenario;
  label: string;
  questionByLanguage: Record<LanguageCode, string>;
  intent: string;
};

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");
const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;

const languages: LanguageOption[] = [
  { code: "ko", label: "Korean", helper: "Official Korean terms" },
  { code: "easy_ko", label: "Easy Korean", helper: "Plain Korean" },
  { code: "en", label: "English", helper: "Keep official names" },
  { code: "vi", label: "Tiếng Việt", helper: "Bản demo đa ngôn ngữ" },
  { code: "zh", label: "中文", helper: "多语言演示" },
];

const exampleQuestions: ExampleQuestion[] = [
  {
    id: "G004-1",
    scenario: "official_guidance",
    label: "Official guidance",
    questionByLanguage: {
      ko: "광주에 처음 왔는데 외국인등록과 체류 관련 안내는 어디서 확인하나요?",
      easy_ko: "광주에 처음 왔어요. 외국인등록 안내를 어디서 볼 수 있나요?",
      en: "I just arrived in Gwangju. Where can I check alien registration and stay guidance?",
      vi: "Tôi mới đến Gwangju. Tôi có thể xem hướng dẫn đăng ký người nước ngoài ở đâu?",
      zh: "我刚到光州。在哪里可以确认外国人登记和居留指南？",
    },
    intent: "Official-source RAG answer with citations and institution handoff.",
  },
  {
    id: "G004-2",
    scenario: "refusal_handoff",
    label: "Refusal / handoff",
    questionByLanguage: {
      ko: "제 비자로 지금 바로 일해도 되나요?",
      easy_ko: "제 비자로 일해도 될까요?",
      en: "Tell me the final legal answer: can I work immediately with my visa?",
      vi: "Hãy quyết định giúp tôi: với visa này tôi có thể đi làm ngay không?",
      zh: "请直接最终判断：我现在这个签证能马上工作吗？",
    },
    intent: "Refuse final immigration/legal judgment and route to official institution.",
  },
  {
    id: "G004-3",
    scenario: "emergency_first",
    label: "Emergency first",
    questionByLanguage: {
      ko: "지금 위협을 받고 있어요. 어디에 연락해야 하나요?",
      easy_ko: "지금 위협을 받고 있어요. 어디에 전화해야 하나요?",
      en: "I am being threatened right now. Who should I contact first?",
      vi: "Hiện tôi đang bị đe dọa. Tôi nên liên hệ ai trước?",
      zh: "我现在正受到威胁。应该先联系哪里？",
    },
    intent: "Emergency cards render above ordinary answer content.",
  },
];

const scenarioLabels: Record<Scenario, string> = {
  official_guidance: "official guidance",
  refusal_handoff: "refusal and handoff",
  emergency_first: "emergency-first routing",
};

const fallbackAnswers: Record<Scenario, Record<LanguageCode, string>> = {
  official_guidance: {
    ko: "공식 안내는 HiKorea와 광주광역시 외국인주민 지원 안내를 먼저 확인하세요. 체류 자격별 세부 요건은 개인 상황에 따라 달라질 수 있으므로 1345 또는 관할 출입국·외국인관서에 확인해야 합니다.",
    easy_ko: "먼저 HiKorea와 광주시 안내를 보세요. 비자와 체류 문제는 사람마다 다를 수 있어요. 1345나 출입국사무소에 다시 확인하세요.",
    en: "Start with HiKorea and Gwangju official foreign-resident support guidance. Stay requirements can change by visa and personal facts, so confirm details with 1345 or the competent immigration office.",
    vi: "Hãy bắt đầu từ HiKorea và hướng dẫn chính thức của thành phố Gwangju dành cho cư dân nước ngoài. Điều kiện cư trú tùy từng visa và trường hợp, nên xác nhận với 1345 hoặc cơ quan xuất nhập cảnh phụ trách.",
    zh: "请先查看 HiKorea 和光州市面向外国居民的官方指南。居留条件会因签证和个人情况而不同，请向 1345 或管辖出入境外国人机关确认。",
  },
  refusal_handoff: {
    ko: "이 데모는 비자 취업 가능 여부를 최종 판단하지 않습니다. 잘못된 판단은 체류 자격 위반으로 이어질 수 있으므로 1345 또는 관할 출입국·외국인관서에 문의하세요.",
    easy_ko: "이 화면은 ‘일해도 된다/안 된다’를 대신 결정하지 않아요. 틀리면 비자 문제가 생길 수 있어요. 1345나 출입국사무소에 물어보세요.",
    en: "This demo cannot make a final visa-work eligibility decision. A wrong answer could affect your immigration status. Contact 1345 or the competent immigration office for case-specific confirmation.",
    vi: "Bản demo này không thể quyết định cuối cùng về việc visa của bạn có được đi làm hay không. Trả lời sai có thể ảnh hưởng tư cách cư trú. Hãy liên hệ 1345 hoặc cơ quan xuất nhập cảnh phụ trách.",
    zh: "本演示不能对签证是否允许工作作出最终判断。错误判断可能影响居留资格。请联系 1345 或管辖出入境外国人机关确认。",
  },
  emergency_first: {
    ko: "지금 신체적 위협이나 범죄 위험이 있으면 일반 행정 안내보다 긴급 신고가 먼저입니다. 안전한 장소로 이동할 수 있으면 이동하고, 즉시 112 또는 119에 연락하세요.",
    easy_ko: "지금 위험하면 먼저 112나 119에 전화하세요. 안전한 곳으로 갈 수 있으면 먼저 이동하세요.",
    en: "If there is an immediate physical threat or crime risk, emergency contact comes before administrative guidance. Move to a safer place if possible and call 112 or 119 now.",
    vi: "Nếu đang có đe dọa thân thể hoặc nguy cơ phạm tội, liên hệ khẩn cấp phải được ưu tiên hơn hướng dẫn hành chính. Nếu có thể, hãy đến nơi an toàn và gọi 112 hoặc 119 ngay.",
    zh: "如果目前有人身威胁或犯罪风险，紧急联络优先于行政指南。可以的话先转移到安全地点，并立即拨打 112 或 119。",
  },
};



const baseInstitutionCards: InstitutionCard[] = [
  {
    name: "Immigration Contact Center 1345",
    description: "Official immigration and stay-status consultation channel.",
    phone: "1345",
    url: "https://www.hikorea.go.kr/",
    address: "Nationwide phone consultation",
    reason: "Use when a question depends on visa status, stay period, employment permission, or personal facts.",
  },
  {
    name: "Gwangju Foreign Residents Support Center",
    description: "Local life and interpretation support for foreign residents in Gwangju.",
    phone: "1644-3828",
    url: "https://www.girc.or.kr/",
    address: "Gwangju Metropolitan City",
    reason: "Use for local settlement, interpretation, and public-service navigation after urgent risks are excluded.",
  },
];

const emergencyCards: EmergencyCard[] = [
  {
    type: "Police / immediate threat",
    phone: "112",
    priority: 1,
    message: "Call first when there is violence, stalking, crime, or an immediate safety threat.",
  },
  {
    type: "Fire / rescue / emergency medical",
    phone: "119",
    priority: 1,
    message: "Call for fire, rescue, ambulance, or urgent medical danger.",
  },
];

function buildFallbackResponse(scenario: Scenario, language: LanguageCode): ChatResponse {
  return {
    answer: fallbackAnswers[scenario][language],
    language,
    citations: [],
    institution_cards: baseInstitutionCards,
    emergency_cards: scenario === "emergency_first" ? emergencyCards : [],
    safety: {
      is_refusal: scenario === "refusal_handoff",
      code: scenario === "refusal_handoff" ? "REFUSE_FINAL_STATUS_DECISION" : "LOCAL_FALLBACK_SAMPLE",
      detected_categories: scenario === "emergency_first" ? ["immediate_safety"] : [scenario],
      redacted_question: "[LOCAL_FALLBACK_QUESTION_NOT_STORED]",
      raw_question_stored: false,
      raw_retention_days: 0,
      scaffold_only: true,
      external_llm_enabled: false,
      provider_disabled: true,
      guidance: [
        "Local fallback sample rendered because NEXT_PUBLIC_API_BASE_URL is not configured or /api/chat was unreachable.",
        "No fallback citation rows are rendered; only live /api/chat responses may provide citation metadata.",
      ],
    },
  };
}

function latestCitation(citations: Citation[]) {
  return citations[0] ?? null;
}

export default function Home() {
  const [language, setLanguage] = useState<LanguageCode>("ko");
  const [selectedExampleId, setSelectedExampleId] = useState(exampleQuestions[0].id);
  const selectedExample = useMemo(
    () => exampleQuestions.find((item) => item.id === selectedExampleId) ?? exampleQuestions[0],
    [selectedExampleId],
  );
  const [question, setQuestion] = useState(selectedExample.questionByLanguage.ko);
  const [resultState, setResultState] = useState<ResultState>("idle");
  const [statusMessage, setStatusMessage] = useState(
    API_BASE_URL
      ? "Ready to call the configured FastAPI /api/chat endpoint."
      : "NEXT_PUBLIC_API_BASE_URL is not configured; the button shows the documented local fallback sample.",
  );
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null);

  const selectedLanguage = useMemo(
    () => languages.find((item) => item.code === language) ?? languages[0],
    [language],
  );
  const topCitation = latestCitation(chatResult?.citations ?? []);
  function resetResult(nextStatusMessage: string) {
    setChatResult(null);
    setResultState("idle");
    setStatusMessage(nextStatusMessage);
  }


  function chooseLanguage(nextLanguage: LanguageCode) {
    setLanguage(nextLanguage);
    setQuestion(selectedExample.questionByLanguage[nextLanguage]);
    resetResult(
      API_BASE_URL
        ? `Language changed to ${nextLanguage}. Ready for live /api/chat.`
        : `Language changed to ${nextLanguage}. Local fallback sample will be shown because API base URL is not configured.`,
    );
  }

  function chooseExample(example: ExampleQuestion) {
    setSelectedExampleId(example.id);
    setQuestion(example.questionByLanguage[language]);
    setChatResult(null);
    setResultState("idle");
    setStatusMessage(
      API_BASE_URL
        ? `Selected ${scenarioLabels[example.scenario]} scenario. Ready for live /api/chat.`
        : `Selected ${scenarioLabels[example.scenario]} scenario. Local fallback sample will be shown because API base URL is not configured.`,
    );
  }

  function updateQuestion(nextQuestion: string) {
    setQuestion(nextQuestion);
    resetResult(
      API_BASE_URL
        ? "Question changed. Ready for live /api/chat."
        : "Question changed. Local fallback sample will be shown because API base URL is not configured.",
    );
  }

  async function submitQuestion() {
    const request: ChatRequest = { question, language };
    setResultState("loading");
    setStatusMessage(API_BASE_URL ? "Calling FastAPI /api/chat..." : "Using documented local fallback sample; no backend is configured.");

    if (!API_BASE_URL) {
      setChatResult(buildFallbackResponse(selectedExample.scenario, language));
      setResultState("fallback");
      return;
    }

    let response: Response;

    try {
      response = await fetch(CHAT_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
    } catch (error) {
      setChatResult(buildFallbackResponse(selectedExample.scenario, language));
      setResultState("fallback");
      setStatusMessage(
        `Backend unreachable (${error instanceof Error ? error.message : "network error"}). Showing documented local fallback sample, not fabricated live citations.`,
      );
      return;
    }

    if (!response.ok) {
      setChatResult(null);
      setResultState("error");
      setStatusMessage(
        `Backend was reachable but returned HTTP ${response.status}. No fallback citations are shown because the backend is not unreachable.`,
      );
      return;
    }

    try {
      const data = (await response.json()) as ChatResponse;
      setChatResult(data);
      setResultState("live");
      setStatusMessage("Live backend response rendered from /api/chat.");
    } catch (error) {
      setChatResult(null);
      setResultState("error");
      setStatusMessage(
        `Backend response could not be parsed (${error instanceof Error ? error.message : "invalid JSON"}). No fallback citations are shown because the backend responded.`,
      );
    }
  }

  return (
    <main style={styles.pageShell}>
      <section style={styles.hero}>
        <p style={styles.eyebrow}>Honam/Gwangju official-source RAG feasibility MVP</p>
        <h1 style={styles.title}>3-minute multilingual public demo</h1>
        <p style={styles.lead}>
          A Next.js client demo for official-source guidance, safe refusal, emergency-first routing,
          privacy warnings, and backend-provided citation metadata. Admin upload/edit workflows are
          roadmap-only and not included in this public screen.
        </p>
        <div style={styles.statusRow}>
          <span style={styles.statusPill}>API base: {API_BASE_URL || "not configured"}</span>
          <span style={styles.statusPill}>Endpoint: /api/chat</span>
          <span style={styles.statusPill}>Demo language: {selectedLanguage.label}</span>
        </div>
      </section>

      <section aria-labelledby="language-heading" style={styles.cardWide}>
        <h2 id="language-heading" style={styles.sectionTitle}>Language switching</h2>
        <div style={styles.languageGrid}>
          {languages.map((item) => (
            <button
              key={item.code}
              type="button"
              onClick={() => chooseLanguage(item.code)}
              style={{
                ...styles.languageButton,
                ...(item.code === language ? styles.languageButtonActive : {}),
              }}
            >
              <strong>{item.label}</strong>
              <span style={styles.muted}>{item.helper}</span>
            </button>
          ))}
        </div>
        <p style={styles.smallNote}>
          Request model: <strong>{"{ question, language }"}</strong>. Supported language values are
          exactly <strong>ko, easy_ko, en, vi, zh</strong>.
        </p>
      </section>

      <section aria-labelledby="question-heading" style={styles.gridTwoColumns}>
        <div style={styles.card}>
          <h2 id="question-heading" style={styles.sectionTitle}>Three demo scenario chips</h2>
          <div style={styles.chipList}>
            {exampleQuestions.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => chooseExample(item)}
                style={{
                  ...styles.chip,
                  ...(item.id === selectedExampleId ? styles.chipActive : {}),
                }}
              >
                <span style={styles.chipId}>{item.id}</span>
                <span>
                  <strong>{item.label}</strong>
                  <small style={styles.chipHelp}>{item.intent}</small>
                </span>
              </button>
            ))}
          </div>
          <label htmlFor="question" style={styles.label}>Question sent to /api/chat</label>
          <textarea
            id="question"
            value={question}
            onChange={(event) => updateQuestion(event.target.value)}
            rows={5}
            style={styles.textarea}
          />
          <button type="button" onClick={submitQuestion} disabled={resultState === "loading"} style={styles.primaryButton}>
            {resultState === "loading" ? "Loading official-source answer..." : "Run 3-minute demo"}
          </button>
          <p style={styles.smallNote}>{statusMessage}</p>
          {resultState === "fallback" ? (
            <p style={styles.fallbackNotice}>
              Fallback mode is visibly labeled. It is a local UI sample for demos only and does not
              claim that retrieval happened.
            </p>
          ) : null}
        </div>

        <div style={styles.card}>
          <div style={styles.answerHeader}>
            <h2 style={styles.sectionTitle}>Answer rendering</h2>
            <span style={styles.stateBadge}>{resultState}</span>
          </div>

          {chatResult?.emergency_cards.length ? (
            <div style={styles.emergencyPanel}>
              <h3 style={styles.subTitle}>Emergency cards appear first</h3>
              {chatResult.emergency_cards.map((card) => (
                <article key={`${card.type}-${card.phone}`} style={styles.emergencyCard}>
                  <strong>{card.type}</strong>
                  <span style={styles.emergencyPhone}>{card.phone}</span>
                  <p>{card.message}</p>
                </article>
              ))}
            </div>
          ) : null}

          {chatResult ? (
            <article style={styles.answerBox}>
              <p>{chatResult.answer}</p>
              {chatResult.safety.is_refusal ? (
                <p style={styles.refusalBanner}>Refusal active: {chatResult.safety.code}</p>
              ) : null}
            </article>
          ) : (
            <div style={styles.placeholderBox}>
              <strong>No answer rendered yet.</strong>
              <p>
                Press the demo button to render a live backend response, or a clearly labeled local
                sample when the backend is unavailable.
              </p>
            </div>
          )}
        </div>
      </section>

      <section aria-labelledby="source-heading" style={styles.gridTwoColumns}>
        <div style={styles.card}>
          <h2 id="source-heading" style={styles.sectionTitle}>Source quote and citation highlighting</h2>
          {chatResult?.citations.length ? (
            <div style={styles.citationList}>
              {chatResult.citations.map((citation, index) => (
                <article key={`${citation.snapshot_id ?? "citation"}-${citation.source_hash ?? index}`} style={styles.citationCard}>
                  <p style={styles.quote}>“{citation.excerpt ?? "No excerpt returned."}”</p>
                  {citation.url ? (
                    <a href={citation.url} target="_blank" rel="noreferrer" style={styles.link}>
                      {citation.title}
                    </a>
                  ) : (
                    <strong>{citation.title}</strong>
                  )}
                  <p style={styles.smallNote}>{citation.institution} · {citation.page_or_section ?? "No section returned"}</p>
                </article>
              ))}
            </div>
          ) : (
            <p style={styles.smallNote}>
              No citations returned. The UI does not invent citation rows when /api/chat omits them
              or when the emergency-first path intentionally prioritizes phone routing.
            </p>
          )}
        </div>

        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>Latest checked metadata</h2>
          <div style={styles.metadataGrid}>
            <div style={styles.metadataItem}>
              <span style={styles.muted}>Retrieved / checked at</span>
              <strong>{topCitation?.retrieved_at ?? "Not returned"}</strong>
            </div>
            <div style={styles.metadataItem}>
              <span style={styles.muted}>Snapshot ID</span>
              <strong>{topCitation?.snapshot_id ?? "Not returned"}</strong>
            </div>
            <div style={styles.metadataItem}>
              <span style={styles.muted}>Source hash</span>
              <strong>{topCitation?.source_hash ?? "Not returned"}</strong>
            </div>
            <div style={styles.metadataItem}>
              <span style={styles.muted}>Institution</span>
              <strong>{topCitation?.institution ?? "Not returned"}</strong>
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby="institution-heading" style={styles.gridThreeColumns}>
        <article style={styles.card}>
          <h2 id="institution-heading" style={styles.sectionTitle}>Institution cards</h2>
          {chatResult?.institution_cards.length ? (
            chatResult.institution_cards.map((card) => (
              <div key={`${card.name}-${card.phone ?? card.url ?? "card"}`} style={styles.institutionCard}>
                <strong>{card.name}</strong>
                <span>{card.phone ?? "No phone returned"}</span>
                <p>{card.description}</p>
                {card.reason ? <p style={styles.smallNote}>{card.reason}</p> : null}
                {card.url ? (
                  <a href={card.url} target="_blank" rel="noreferrer" style={styles.link}>Official site</a>
                ) : null}
              </div>
            ))
          ) : (
            <p>No institution cards returned yet.</p>
          )}
        </article>
        <article style={styles.card}>
          <h2 style={styles.sectionTitle}>Privacy / provider warnings</h2>
          <ul style={styles.warningList}>
            <li>Do not enter passport numbers, alien registration numbers, addresses, or private case details.</li>
            <li>Raw question stored: <strong>{chatResult ? String(chatResult.safety.raw_question_stored) : "unknown"}</strong>.</li>
            <li>Raw retention days: <strong>{chatResult?.safety.raw_retention_days ?? "unknown"}</strong>.</li>
            <li>External LLM enabled: <strong>{chatResult ? String(chatResult.safety.external_llm_enabled) : "unknown"}</strong>.</li>
            <li>Provider disabled: <strong>{chatResult ? String(chatResult.safety.provider_disabled) : "unknown"}</strong>.</li>
          </ul>
        </article>
        <article style={styles.card}>
          <h2 style={styles.sectionTitle}>Admin roadmap only</h2>
          <p>
            Admin upload, source editing, reviewer queues, and production retention controls are
            roadmap-only. This public G004 screen only demonstrates the user-facing answer contract.
          </p>
          <p style={styles.smallNote}>{chatResult?.safety.guidance.join(" ") ?? "Safety guidance appears after a response."}</p>
        </article>
      </section>
    </main>
  );
}

const styles: Record<string, CSSProperties> = {
  pageShell: {
    minHeight: "100vh",
    margin: 0,
    padding: "48px 24px",
    background: "#f4f7fb",
    color: "#172033",
    fontFamily:
      "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  hero: {
    maxWidth: "1080px",
    margin: "0 auto 24px",
    padding: "36px",
    borderRadius: "28px",
    background: "linear-gradient(135deg, #123c69, #1e6f8f)",
    color: "white",
    boxShadow: "0 20px 50px rgba(18, 60, 105, 0.22)",
  },
  eyebrow: {
    margin: "0 0 12px",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    fontSize: "12px",
    fontWeight: 700,
    opacity: 0.82,
  },
  title: {
    margin: 0,
    fontSize: "clamp(34px, 6vw, 64px)",
    lineHeight: 1,
  },
  lead: {
    maxWidth: "820px",
    fontSize: "18px",
    lineHeight: 1.7,
    opacity: 0.92,
  },
  statusRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
    marginTop: "24px",
  },
  statusPill: {
    padding: "8px 12px",
    borderRadius: "999px",
    background: "rgba(255, 255, 255, 0.14)",
    border: "1px solid rgba(255, 255, 255, 0.26)",
    fontSize: "14px",
  },
  cardWide: {
    maxWidth: "1080px",
    margin: "24px auto",
    padding: "24px",
    borderRadius: "22px",
    background: "white",
    border: "1px solid #dce5f2",
    boxShadow: "0 12px 30px rgba(23, 32, 51, 0.08)",
  },
  card: {
    padding: "24px",
    borderRadius: "22px",
    background: "white",
    border: "1px solid #dce5f2",
    boxShadow: "0 12px 30px rgba(23, 32, 51, 0.08)",
  },
  sectionTitle: {
    margin: "0 0 16px",
    fontSize: "20px",
  },
  subTitle: {
    margin: "0 0 10px",
    fontSize: "16px",
  },
  languageGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "12px",
  },
  languageButton: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "6px",
    padding: "14px",
    borderRadius: "16px",
    border: "1px solid #cfd9e8",
    background: "#f8fbff",
    color: "#172033",
    cursor: "pointer",
  },
  languageButtonActive: {
    borderColor: "#1e6f8f",
    background: "#e7f7fb",
    boxShadow: "inset 0 0 0 1px #1e6f8f",
  },
  gridTwoColumns: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "24px",
    maxWidth: "1080px",
    margin: "24px auto",
  },
  gridThreeColumns: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: "24px",
    maxWidth: "1080px",
    margin: "24px auto 0",
  },
  chipList: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    marginBottom: "20px",
  },
  chip: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
    width: "100%",
    padding: "12px",
    borderRadius: "14px",
    border: "1px solid #d7e2ef",
    background: "#fbfdff",
    color: "#172033",
    textAlign: "left",
    cursor: "pointer",
  },
  chipActive: {
    borderColor: "#123c69",
    background: "#edf4ff",
  },
  chipId: {
    minWidth: "58px",
    padding: "4px 8px",
    borderRadius: "999px",
    background: "#dff1ff",
    color: "#123c69",
    fontWeight: 700,
    fontSize: "12px",
    textAlign: "center",
  },
  chipHelp: {
    display: "block",
    marginTop: "4px",
    color: "#65758b",
    lineHeight: 1.4,
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: 700,
  },
  textarea: {
    width: "100%",
    boxSizing: "border-box",
    padding: "14px",
    borderRadius: "14px",
    border: "1px solid #cfd9e8",
    resize: "vertical",
    font: "inherit",
  },
  primaryButton: {
    width: "100%",
    marginTop: "12px",
    padding: "13px 16px",
    border: 0,
    borderRadius: "14px",
    background: "#123c69",
    color: "white",
    fontWeight: 800,
    cursor: "pointer",
  },
  fallbackNotice: {
    padding: "12px",
    borderRadius: "14px",
    background: "#fff9e8",
    border: "1px solid #ffe0a3",
    lineHeight: 1.5,
    fontSize: "14px",
  },
  answerHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "12px",
  },
  stateBadge: {
    padding: "5px 9px",
    borderRadius: "999px",
    background: "#edf4ff",
    color: "#123c69",
    fontSize: "12px",
    fontWeight: 800,
    textTransform: "uppercase",
  },
  answerBox: {
    padding: "18px",
    borderRadius: "18px",
    background: "#f8fbff",
    border: "1px solid #dce5f2",
    lineHeight: 1.7,
    whiteSpace: "pre-wrap",
  },
  placeholderBox: {
    padding: "18px",
    borderRadius: "18px",
    background: "#fff9e8",
    border: "1px solid #ffe0a3",
    lineHeight: 1.6,
  },
  refusalBanner: {
    marginTop: "12px",
    padding: "12px",
    borderRadius: "14px",
    background: "#fff2f2",
    border: "1px solid #ffc9c9",
    fontWeight: 700,
  },
  emergencyPanel: {
    marginBottom: "14px",
    padding: "14px",
    borderRadius: "18px",
    background: "#fff2f2",
    border: "1px solid #ffc9c9",
  },
  emergencyCard: {
    padding: "12px",
    borderRadius: "14px",
    background: "white",
    border: "1px solid #ffd8d8",
    marginTop: "10px",
    lineHeight: 1.5,
  },
  emergencyPhone: {
    display: "inline-block",
    marginLeft: "10px",
    padding: "4px 10px",
    borderRadius: "999px",
    background: "#b42318",
    color: "white",
    fontWeight: 800,
  },
  citationList: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  citationCard: {
    padding: "14px",
    borderRadius: "16px",
    background: "#f8fbff",
    border: "1px solid #dce5f2",
  },
  quote: {
    margin: "0 0 10px",
    padding: "12px",
    borderLeft: "4px solid #1e6f8f",
    background: "white",
    lineHeight: 1.6,
    fontWeight: 700,
  },
  metadataGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "12px",
    marginTop: "14px",
  },
  metadataItem: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    padding: "14px",
    borderRadius: "14px",
    background: "#f8fbff",
    border: "1px solid #dce5f2",
    wordBreak: "break-word",
  },
  institutionCard: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    padding: "14px",
    borderRadius: "14px",
    background: "#f8fbff",
    border: "1px solid #dce5f2",
    marginBottom: "12px",
    lineHeight: 1.5,
  },
  warningList: {
    margin: 0,
    paddingLeft: "20px",
    lineHeight: 1.7,
  },
  link: {
    color: "#0b5cad",
    fontWeight: 800,
  },
  muted: {
    color: "#65758b",
    fontSize: "13px",
  },
  smallNote: {
    color: "#526275",
    fontSize: "14px",
    lineHeight: 1.6,
  },
};
