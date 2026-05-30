// ============================================================
// App.js
// Gamma Email Generator — React Frontend
// ============================================================
// FEATURES:
//   ✅ Select Category + Sub-Category
//   ✅ Paste raw email input
//   ✅ Generate Gamma-branded email via 5 agents
//   ✅ Copy output to clipboard
//   ✅ Auto saves to DB on every generation
// ============================================================

import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";
const CATEGORIES = ["Newsletter", "Promotion", "Welcome"];

export default function App() {

  // ─────────────────────────────────────────
  // STATE
  // ─────────────────────────────────────────
  const [category, setCategory] = useState("Newsletter");
  const [subCategory, setSubCategory] = useState("");
  const [inputMail, setInputMail] = useState("");
  const [outputMail, setOutputMail] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // ─────────────────────────────────────────
  // HANDLERS
  // ─────────────────────────────────────────
  const generateEmail = async () => {
    if (!inputMail.trim()) return alert("Please paste an input email.");
    setLoading(true);
    setOutputMail("");
    try {
      const res = await axios.post(`${API}/api/email/generate`, {
        input_mail: inputMail,
        category,
        sub_category: subCategory
      });
      setOutputMail(res.data.output_mail);
    } catch {
      setOutputMail("❌ Error generating email. Is the backend running?");
    }
    setLoading(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(outputMail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const clearAll = () => {
    setInputMail("");
    setOutputMail("");
    setSubCategory("");
  };

  // ─────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────
  return (
    <div style={styles.app}>

      {/* ── HEADER ── */}
      <header style={styles.header}>
        <h1 style={styles.logo}> Gamma AI Email Generator</h1>
      
      </header>

      {/* ── MAIN CARD ── */}
      <div style={styles.card}>
        <h2 style={styles.cardTitle}>Generate Gamma-Branded Email</h2>

        {/* ── CATEGORY + SUB-CATEGORY ── */}
        <div style={styles.row}>
          <div style={styles.field}>
            <label style={styles.label}>Category</label>
            <select style={styles.select} value={category}
              onChange={e => setCategory(e.target.value)}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Sub-Category (optional)</label>
            <input style={styles.input} value={subCategory}
              onChange={e => setSubCategory(e.target.value)}
              placeholder="e.g. Product Launch, Tips and Tricks" />
          </div>
        </div>

        {/* ── INPUT EMAIL ── */}
        <label style={styles.label}>Paste Raw Input Email</label>
        <textarea
          style={styles.textarea}
          rows={7}
          value={inputMail}
          onChange={e => setInputMail(e.target.value)}
          placeholder="Paste the raw email you want to transform into a Gamma-branded email..."
        />

        {/* ── BUTTONS ── */}
        <div style={styles.btnRow}>
          <button
            style={loading ? styles.btnDisabled : styles.btn}
            onClick={generateEmail}
            disabled={loading}>
            {loading ? "Agents working..." : "✨ Generate Branded Email"}
          </button>
          <button style={styles.btnClear} onClick={clearAll}>
            🗑️ Clear
          </button>
        </div>

        {/* ── AGENT PROGRESS ── */}
        {loading && (
          <div style={styles.progressBox}>
            <p style={styles.progressTitle}>🔄 Agent Pipeline Running...</p>
            <div style={styles.progressItem}>
               <strong>Agent 1</strong> — Orchestrator analyzing email...
            </div>
            <div style={styles.progressItem}>
               <strong>Agent 2/3/4</strong> — {category} Specialist generating...
            </div>
            <div style={styles.progressItem}>
               <strong>Agent 5</strong> — Validator reviewing quality...
            </div>
            <div style={styles.progressItem}>
               <strong>Auto saving</strong> to database...
            </div>
          </div>
        )}

        {/* ── OUTPUT EMAIL ── */}
        {outputMail && (
          <div style={styles.outputBox}>

            {/* Output Header */}
            <div style={styles.outputHeader}>
              <h3 style={styles.outputTitle}> Gamma-Branded Output</h3>
              <div style={styles.outputActions}>
                <span style={styles.savedBadge}> Saved to DB</span>
                <button style={styles.copyBtn} onClick={copyToClipboard}>
                  {copied ? " Copied!" : " Copy"}
                </button>
              </div>
            </div>

            {/* Output Content */}
            <pre style={styles.outputText}>{outputMail}</pre>

          </div>
        )}

      </div>

      {/* ── FOOTER ── */}
      <footer style={styles.footer}>
       
        
      </footer>

    </div>
  );
}

// ─────────────────────────────────────────
// STYLES
// ─────────────────────────────────────────
const styles = {
  app: {
    minHeight: "100vh",
    background: "#f0f4ff",
    fontFamily: "'Segoe UI', sans-serif"
  },
  header: {
    background: "linear-gradient(135deg,#1a1aff,#6600cc)",
    color: "#fff",
    padding: "2rem",
    textAlign: "center"
  },
  logo: { margin: 0, fontSize: "2rem", fontWeight: 700 },
  subtitle: { margin: "0.5rem 0 0", opacity: 0.85, fontSize: "0.95rem" },
  card: {
    background: "#fff",
    margin: "2rem auto",
    maxWidth: 850,
    borderRadius: 16,
    padding: "2rem",
    boxShadow: "0 4px 20px rgba(0,0,0,0.08)"
  },
  cardTitle: { marginTop: 0, color: "#1a1aff", fontSize: "1.4rem" },
  row: { display: "flex", gap: "1rem", marginBottom: "1rem" },
  field: { flex: 1 },
  label: {
    display: "block",
    fontWeight: 600,
    marginBottom: "0.4rem",
    color: "#333",
    fontSize: "0.9rem"
  },
  input: {
    width: "100%",
    padding: "0.65rem",
    borderRadius: 8,
    border: "1px solid #ddd",
    fontSize: 14,
    boxSizing: "border-box"
  },
  select: {
    width: "100%",
    padding: "0.65rem",
    borderRadius: 8,
    border: "1px solid #ddd",
    fontSize: 14,
    boxSizing: "border-box"
  },
  textarea: {
    width: "100%",
    padding: "0.8rem",
    borderRadius: 8,
    border: "1px solid #ddd",
    fontSize: 14,
    marginBottom: "1rem",
    boxSizing: "border-box",
    resize: "vertical"
  },
  btnRow: { display: "flex", gap: "1rem", marginBottom: "1rem" },
  btn: {
    background: "linear-gradient(135deg,#1a1aff,#6600cc)",
    color: "#fff",
    border: "none",
    padding: "0.8rem 2rem",
    borderRadius: 8,
    fontSize: 15,
    cursor: "pointer",
    fontWeight: 600
  },
  btnDisabled: {
    background: "#aaa",
    color: "#fff",
    border: "none",
    padding: "0.8rem 2rem",
    borderRadius: 8,
    fontSize: 15,
    cursor: "not-allowed",
    fontWeight: 600
  },
  btnClear: {
    background: "#fff",
    color: "#cc0000",
    border: "1px solid #cc0000",
    padding: "0.8rem 1.5rem",
    borderRadius: 8,
    fontSize: 15,
    cursor: "pointer",
    fontWeight: 600
  },
  progressBox: {
    background: "#f8f5ff",
    border: "1px solid #d4b8ff",
    borderRadius: 10,
    padding: "1rem 1.5rem",
    marginBottom: "1rem"
  },
  progressTitle: {
    margin: "0 0 0.8rem",
    color: "#6600cc",
    fontWeight: 700,
    fontSize: 15
  },
  progressItem: {
    padding: "0.3rem 0",
    color: "#444",
    fontSize: 14
  },
  outputBox: {
    marginTop: "1.5rem",
    background: "#f8fff8",
    border: "1px solid #c3e6c3",
    borderRadius: 12,
    padding: "1.5rem"
  },
  outputHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1rem"
  },
  outputTitle: { margin: 0, color: "#1a7a1a", fontSize: "1.1rem" },
  outputActions: { display: "flex", gap: "0.8rem", alignItems: "center" },
  savedBadge: {
    background: "#e8fff0",
    color: "#1a7a1a",
    padding: "4px 12px",
    borderRadius: 20,
    fontSize: 12,
    fontWeight: 600,
    border: "1px solid #c3e6c3"
  },
  copyBtn: {
    background: "#1a1aff",
    color: "#fff",
    border: "none",
    padding: "0.4rem 1rem",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 13
  },
  outputText: {
    whiteSpace: "pre-wrap",
    fontFamily: "'Segoe UI', sans-serif",
    lineHeight: 1.8,
    margin: 0,
    fontSize: 14,
    color: "#222"
  },
  footer: {
    textAlign: "center",
    padding: "2rem",
    color: "#888",
    fontSize: 13
  }
};