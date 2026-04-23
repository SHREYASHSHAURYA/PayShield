import { FormEvent, useState } from "react";
import { assessRisk } from "./services/assessment";
import type { AssessmentRequest, AssessmentResponse } from "./types/assessment";

const initialPayload: AssessmentRequest = {
  session_id: "demo-session-1",
  device_timestamp: new Date().toISOString(),
  locale: "en-IN",
  interaction_events: [
    {
      event_id: "e1",
      timestamp: new Date().toISOString(),
      interaction_type: "text_message",
      content_text: "",
      source_label: "user_input",
      metadata: {},
    },
  ],
  payment_context: {
    payment_method: "none",
    payment_direction: "none",
    amount: null,
    currency: "INR",
    upi_id: null,
    collect_request_present: false,
    qr_present: false,
    payment_link_present: false,
    merchant_name: null,
    note: null,
  },
  user_flags: {
    user_expects_money: false,
    user_initiated_contact: false,
    trusted_beneficiary: false,
    first_time_beneficiary: true,
    user_confirms_pressure: false,
    user_confirms_identity_verified: false,
  },
};

export default function App() {
  const [payload, setPayload] = useState<AssessmentRequest>(initialPayload);
  const [result, setResult] = useState<AssessmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const requestPayload: AssessmentRequest = {
        ...payload,
        device_timestamp: new Date().toISOString(),
        interaction_events: payload.interaction_events.map((item, index) => ({
          ...item,
          event_id: `e${index + 1}`,
          timestamp: new Date().toISOString(),
        })),
      };

      const response = await assessRisk(requestPayload);
      setResult(response);
    } catch (err) {
      setError(
        "Failed to assess risk. Make sure the backend server is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.hero}>
          <p style={styles.kicker}>PayShield</p>
          <h1 style={styles.title}>Pre-Transaction Scam Risk Assistant</h1>
          <p style={styles.subtitle}>
            Enter the visible interaction context and payment details. PayShield
            will estimate scam risk before payment execution.
          </p>
        </div>

        <form style={styles.layout} onSubmit={handleSubmit}>
          <section style={styles.panel}>
            <h2 style={styles.sectionTitle}>Interaction Context</h2>

            <label style={styles.label}>
              Message or interaction content
              <textarea
                style={styles.textarea}
                value={payload.interaction_events[0].content_text ?? ""}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    interaction_events: [
                      {
                        ...payload.interaction_events[0],
                        content_text: event.target.value,
                      },
                    ],
                  })
                }
                placeholder="Example: I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently."
                required
              />
            </label>

            <label style={styles.label}>
              Interaction type
              <select
                style={styles.input}
                value={payload.interaction_events[0].interaction_type}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    interaction_events: [
                      {
                        ...payload.interaction_events[0],
                        interaction_type: event.target
                          .value as AssessmentRequest["interaction_events"][0]["interaction_type"],
                      },
                    ],
                  })
                }
              >
                <option value="text_message">Text Message</option>
                <option value="phone_call">Phone Call</option>
                <option value="qr_scan">QR Scan</option>
                <option value="upi_id_entry">UPI ID Entry</option>
                <option value="collect_request">Collect Request</option>
                <option value="payment_link">Payment Link</option>
                <option value="app_prompt">App Prompt</option>
                <option value="user_confirmation">User Confirmation</option>
              </select>
            </label>

            <div style={styles.checkboxGroup}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.user_flags.user_initiated_contact}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      user_flags: {
                        ...payload.user_flags,
                        user_initiated_contact: event.target.checked,
                      },
                    })
                  }
                />
                User initiated the contact
              </label>

              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.user_flags.user_confirms_pressure}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      user_flags: {
                        ...payload.user_flags,
                        user_confirms_pressure: event.target.checked,
                      },
                    })
                  }
                />
                User feels pressured
              </label>

              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.user_flags.user_confirms_identity_verified}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      user_flags: {
                        ...payload.user_flags,
                        user_confirms_identity_verified: event.target.checked,
                      },
                    })
                  }
                />
                Identity verified
              </label>
            </div>
          </section>

          <section style={styles.panel}>
            <h2 style={styles.sectionTitle}>Payment Context</h2>

            <label style={styles.label}>
              Payment method
              <select
                style={styles.input}
                value={payload.payment_context.payment_method}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    payment_context: {
                      ...payload.payment_context,
                      payment_method: event.target
                        .value as AssessmentRequest["payment_context"]["payment_method"],
                    },
                  })
                }
              >
                <option value="none">None</option>
                <option value="qr_code">QR Code</option>
                <option value="upi_id">UPI ID</option>
                <option value="collect_request">Collect Request</option>
                <option value="payment_link">Payment Link</option>
              </select>
            </label>

            <label style={styles.label}>
              Payment direction
              <select
                style={styles.input}
                value={payload.payment_context.payment_direction}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    payment_context: {
                      ...payload.payment_context,
                      payment_direction: event.target
                        .value as AssessmentRequest["payment_context"]["payment_direction"],
                    },
                  })
                }
              >
                <option value="none">None</option>
                <option value="send">Send</option>
                <option value="receive">Receive</option>
              </select>
            </label>

            <label style={styles.label}>
              Amount
              <input
                style={styles.input}
                type="number"
                min="0"
                step="0.01"
                value={payload.payment_context.amount ?? ""}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    payment_context: {
                      ...payload.payment_context,
                      amount: event.target.value
                        ? Number(event.target.value)
                        : null,
                    },
                  })
                }
                placeholder="500"
              />
            </label>

            <label style={styles.label}>
              UPI ID
              <input
                style={styles.input}
                type="text"
                value={payload.payment_context.upi_id ?? ""}
                onChange={(event) =>
                  setPayload({
                    ...payload,
                    payment_context: {
                      ...payload.payment_context,
                      upi_id: event.target.value || null,
                    },
                  })
                }
                placeholder="name@bank"
              />
            </label>

            <div style={styles.checkboxGroup}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.payment_context.qr_present}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      payment_context: {
                        ...payload.payment_context,
                        qr_present: event.target.checked,
                      },
                    })
                  }
                />
                QR present
              </label>

              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.payment_context.collect_request_present}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      payment_context: {
                        ...payload.payment_context,
                        collect_request_present: event.target.checked,
                      },
                    })
                  }
                />
                Collect request present
              </label>

              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={payload.payment_context.payment_link_present}
                  onChange={(event) =>
                    setPayload({
                      ...payload,
                      payment_context: {
                        ...payload.payment_context,
                        payment_link_present: event.target.checked,
                      },
                    })
                  }
                />
                Payment link present
              </label>
            </div>

            <button type="submit" style={styles.button} disabled={loading}>
              {loading ? "Assessing..." : "Assess Risk"}
            </button>

            {error ? <p style={styles.error}>{error}</p> : null}
          </section>
        </form>

        <section style={styles.resultPanel}>
          <h2 style={styles.sectionTitle}>Assessment Result</h2>

          {result ? (
            <div style={styles.resultContent}>
              <div style={styles.summaryGrid}>
                <div style={styles.summaryCard}>
                  <span style={styles.summaryLabel}>Risk Level</span>
                  <strong style={styles.summaryValue}>
                    {formatTitleCase(result.risk_level)}
                  </strong>
                </div>
                <div style={styles.summaryCard}>
                  <span style={styles.summaryLabel}>Risk Score</span>
                  <strong style={styles.summaryValue}>
                    {result.risk_score}
                  </strong>
                </div>
                <div style={styles.summaryCard}>
                  <span style={styles.summaryLabel}>Current Stage</span>
                  <strong style={styles.summaryValue}>
                    {formatTitleCase(result.current_stage)}
                  </strong>
                </div>
                <div style={styles.summaryCard}>
                  <span style={styles.summaryLabel}>Action</span>
                  <strong style={styles.summaryValueAction}>
                    {formatAction(result.recommended_action)}
                  </strong>
                </div>
              </div>

              <div style={styles.block}>
                <h3 style={styles.blockTitle}>Triggered Signals</h3>
                <ul style={styles.list}>
                  {result.triggered_signals.map((signal) => (
                    <li
                      key={`${signal.signal_type}-${signal.source_event_id ?? "none"}`}
                      style={styles.listItem}
                    >
                      {signal.signal_type} ({signal.confidence}) -{" "}
                      {signal.evidence}
                    </li>
                  ))}
                </ul>
              </div>

              <div style={styles.block}>
                <h3 style={styles.blockTitle}>Stage History</h3>
                <p style={styles.paragraph}>
                  Completed stages:{" "}
                  {result.stage_state.completed_stages.join(" -> ") || "none"}
                </p>
              </div>

              <div style={styles.block}>
                <h3 style={styles.blockTitle}>Explanation</h3>
                <ul style={styles.list}>
                  {result.explanation.map((item, index) => (
                    <li key={index} style={styles.listItem}>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p style={styles.paragraph}>
              No assessment yet. Submit the form to see the result.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}

function formatAction(value: string) {
  return value.split("_").join(" ");
}

function formatTitleCase(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    background:
      "linear-gradient(135deg, rgb(244, 239, 226) 0%, rgb(255, 250, 242) 45%, rgb(238, 246, 243) 100%)",
    color: "#172127",
    fontFamily: "Georgia, 'Times New Roman', serif",
    padding: "32px 20px",
  },
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
    display: "grid",
    gap: "24px",
  },
  hero: {
    background: "rgba(255, 255, 255, 0.85)",
    border: "1px solid rgba(23, 33, 39, 0.1)",
    borderRadius: "24px",
    padding: "28px",
    boxShadow: "0 18px 45px rgba(23, 33, 39, 0.08)",
  },
  kicker: {
    margin: 0,
    textTransform: "uppercase",
    letterSpacing: "0.18em",
    fontSize: "12px",
    color: "#8a4b2a",
  },
  title: {
    margin: "10px 0 8px",
    fontSize: "44px",
    lineHeight: 1.05,
  },
  subtitle: {
    margin: 0,
    maxWidth: "760px",
    fontSize: "18px",
    lineHeight: 1.6,
    color: "#40505c",
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "24px",
  },
  panel: {
    background: "rgba(255, 255, 255, 0.9)",
    border: "1px solid rgba(23, 33, 39, 0.1)",
    borderRadius: "24px",
    padding: "24px",
    display: "grid",
    gap: "18px",
    boxShadow: "0 16px 36px rgba(23, 33, 39, 0.06)",
  },
  resultPanel: {
    background: "#172127",
    color: "#f6efe3",
    borderRadius: "24px",
    padding: "24px",
    display: "grid",
    gap: "18px",
    boxShadow: "0 18px 44px rgba(23, 33, 39, 0.18)",
  },
  sectionTitle: {
    margin: 0,
    fontSize: "24px",
  },
  label: {
    display: "grid",
    gap: "8px",
    fontSize: "14px",
    fontWeight: 600,
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    borderRadius: "14px",
    border: "1px solid rgba(23, 33, 39, 0.18)",
    padding: "12px 14px",
    fontSize: "15px",
    background: "#fffdf8",
    color: "#172127",
  },
  textarea: {
    width: "100%",
    boxSizing: "border-box",
    minHeight: "180px",
    borderRadius: "18px",
    border: "1px solid rgba(23, 33, 39, 0.18)",
    padding: "14px",
    fontSize: "15px",
    resize: "vertical",
    background: "#fffdf8",
    color: "#172127",
  },
  checkboxGroup: {
    display: "grid",
    gap: "10px",
  },
  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontSize: "14px",
  },
  button: {
    border: "none",
    borderRadius: "16px",
    padding: "14px 18px",
    background: "#b6542c",
    color: "#fff8f3",
    fontSize: "16px",
    fontWeight: 700,
    cursor: "pointer",
  },
  error: {
    margin: 0,
    color: "#a52323",
    fontSize: "14px",
  },
  resultContent: {
    display: "grid",
    gap: "18px",
  },
  summaryGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
    gap: "14px",
  },
  summaryCard: {
    background: "rgba(246, 239, 227, 0.08)",
    border: "1px solid rgba(246, 239, 227, 0.12)",
    borderRadius: "18px",
    padding: "16px",
    display: "grid",
    gap: "6px",
  },
  summaryLabel: {
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "#cdbda8",
  },
  summaryValue: {
    fontSize: "20px",
  },
  summaryValueAction: {
    fontSize: "20px",
    lineHeight: 1.3,
    overflowWrap: "anywhere",
    wordBreak: "break-word",
    textTransform: "capitalize",
  },

  block: {
    display: "grid",
    gap: "10px",
  },
  blockTitle: {
    margin: 0,
    fontSize: "18px",
  },
  paragraph: {
    margin: 0,
    lineHeight: 1.6,
    color: "#e6d8c4",
  },
  list: {
    margin: 0,
    paddingLeft: "18px",
    display: "grid",
    gap: "8px",
  },
  listItem: {
    lineHeight: 1.5,
  },
};
