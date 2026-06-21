# Soft Alert Inquiry Flow — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the soft-alert modal's static "Got it / Why?" buttons with a 2-question inquiry flow that branches into 6 personalised result states, then offers a chatbot redirect with pre-filled context.

**Architecture:** Frontend-only change across 4 files. `i18n.js` gets 26 new keys; `InputBar.js` gains an `initialText` prop; `soft-alert/page.js` replaces its state machine; `chat/page.js` wraps in Suspense and reads `?prefill=`. No backend changes.

**Tech Stack:** Next.js 15 App Router, React 19, Tailwind CSS 4, `next/navigation` (`useRouter`, `useSearchParams`), `react` (`Suspense`)

**Spec:** `docs/superpowers/specs/2026-06-21-soft-alert-inquiry-design.md`

---

## File Map

| File | Change |
|---|---|
| `frontend/src/lib/i18n.js` | Add 26 new keys to the `// ── Soft Alert ──` section, before `// ── Hard Alert ──` |
| `frontend/src/components/InputBar.js` | Add `initialText=""` prop; init state from it; auto-show input when non-empty |
| `frontend/src/app/soft-alert/page.js` | Replace all state/buttons with 4-state inquiry machine + 6 result branches |
| `frontend/src/app/chat/page.js` | Extract `ChatPageInner`; add Suspense wrapper; read `?prefill=`; pass to InputBar |

---

## Task 1: Add i18n keys

**Files:**
- Modify: `frontend/src/lib/i18n.js` (after line 222, inside `// ── Soft Alert ──` block, before `// ── Hard Alert ──`)

- [ ] **Step 1: Insert the 26 new keys**

  Open `frontend/src/lib/i18n.js`. Find the line:
  ```js
  soft_push_body: { English: "Your glucose may drop during exercise. Tap for details.", ... },
  ```
  Insert the following block immediately after that line (before `// ── Hard Alert ──`):

  ```js
  // ── Soft Alert — Inquiry Flow ──
  inquiry_start: { English: "Answer 2 quick questions for better advice", Chinese: "回答 2 个问题，获得更精准的建议", Malay: "Jawab 2 soalan untuk nasihat yang lebih baik", Tamil: "சிறந்த ஆலோசனைக்கு 2 கேள்விகளுக்கு பதிலளிக்கவும்" },
  inquiry_q1: { English: "Are you still planning to work out today?", Chinese: "你今天还打算锻炼吗？", Malay: "Adakah anda masih merancang untuk bersenam hari ini?", Tamil: "இன்று உடற்பயிற்சி செய்ய திட்டமிட்டுள்ளீர்களா?" },
  inquiry_q1_a: { English: "Yes, heading to gym at 2pm", Chinese: "是的，下午两点去健身房", Malay: "Ya, pergi ke gym jam 2 petang", Tamil: "ஆம், பிற்பகல் 2 மணிக்கு ஜிம் போகிறேன்" },
  inquiry_q1_b: { English: "Might delay it a bit", Chinese: "可能稍微推迟一下", Malay: "Mungkin tangguhkan sedikit", Tamil: "சற்று தாமதப்படுத்தலாம்" },
  inquiry_q1_c: { English: "Cancelled for today", Chinese: "今天取消了", Malay: "Dibatalkan untuk hari ini", Tamil: "இன்றைக்கு ரத்து செய்தேன்" },
  inquiry_q2: { English: "When did you last eat something?", Chinese: "你上次吃东西是什么时候？", Malay: "Bilakah anda makan terakhir kali?", Tamil: "கடைசியாக எப்போது சாப்பிட்டீர்கள்?" },
  inquiry_q2_a: { English: "Just ate (under 1 hour ago)", Chinese: "刚吃完（1小时内）", Malay: "Baru makan (kurang 1 jam lalu)", Tamil: "இப்போதுதான் சாப்பிட்டேன் (1 மணி நேரத்திற்குள்)" },
  inquiry_q2_b: { English: "About 2–3 hours ago", Chinese: "大约 2-3 小时前", Malay: "Kira-kira 2–3 jam lalu", Tamil: "சுமார் 2–3 மணி நேரத்திற்கு முன்" },
  inquiry_q2_c: { English: "Barely eaten today (4+ hours)", Chinese: "今天几乎没吃东西（4小时以上）", Malay: "Hampir tidak makan hari ini (4+ jam)", Tamil: "இன்று கிட்டத்தட்ட சாப்பிடவில்லை (4+ மணி நேரம்)" },
  inquiry_dismiss: { English: "Got it, thanks", Chinese: "明白了，谢谢", Malay: "Faham, terima kasih", Tamil: "புரிந்தது, நன்றி" },
  inquiry_chat: { English: "Ask the AI more →", Chinese: "继续问 AI →", Malay: "Tanya AI lagi →", Tamil: "AI-ஐ மேலும் கேளுங்கள் →" },
  inquiry_lighter_workout: { English: "Switch to a lighter workout", Chinese: "改为较轻量的运动", Malay: "Tukar ke senaman yang lebih ringan", Tamil: "இலகுவான உடற்பயிற்சிக்கு மாறுங்கள்" },
  result_a1_title: { English: "You're in decent shape 👍", Chinese: "状态不错 👍", Malay: "Anda dalam keadaan baik 👍", Tamil: "நீங்கள் நல்ல நிலையில் இருக்கிறீர்கள் 👍" },
  result_a1_body: { English: "You just ate, so you have a buffer. Pack 2 cream crackers just in case — eat them if you feel dizzy mid-session.", Chinese: "你刚吃完东西，有一定缓冲。随身带两片苏打饼以防万一——如果运动中途感到头晕就吃。", Malay: "Anda baru makan, jadi ada penimbal. Bawa 2 biskut krim untuk berjaga-jaga — makan jika rasa pening semasa senaman.", Tamil: "நீங்கள் இப்போதுதான் சாப்பிட்டீர்கள், எனவே இடையகம் உள்ளது. 2 கிரீம் கிராக்கர்ஸ் எடுத்துச் செல்லுங்கள் — பயிற்சியின் போது தலைசுற்றினால் சாப்பிடுங்கள்." },
  result_a2_title: { English: "Eat something before you go 🍘", Chinese: "出发前先吃点东西 🍘", Malay: "Makan dahulu sebelum pergi 🍘", Tamil: "போவதற்கு முன் ஏதாவது சாப்பிடுங்கள் 🍘" },
  result_a2_body: { English: "It's been a while since your last meal. Your blood sugar could drop to ~3.87 during HIIT. Have 2 cream crackers + cheese now, then head out in 20 minutes.", Chinese: "距上次进餐已有一段时间。HIIT 期间血糖可能降至约 3.87。现在吃两片芝士苏打饼，20 分钟后再出发。", Malay: "Sudah lama anda tidak makan. Gula darah boleh turun ke ~3.87 semasa HIIT. Makan 2 biskut krim + keju sekarang, kemudian pergi dalam 20 minit.", Tamil: "கடைசி உணவிலிருந்து சிறிது நேரம் ஆகிவிட்டது. HIIT-ல் இரத்த சர்க்கரை ~3.87 ஆக குறையலாம். இப்போது 2 கிரீம் கிராக்கர்ஸ் + சீஸ் சாப்பிடுங்கள், 20 நிமிடம் கழித்து புறப்படுங்கள்." },
  result_a3_title: { English: "Please eat a meal first ⚠️", Chinese: "请先吃一顿饭 ⚠️", Malay: "Sila makan dahulu ⚠️", Tamil: "முதலில் உணவு சாப்பிடுங்கள் ⚠️" },
  result_a3_body: { English: "You've barely eaten today. High-intensity exercise could push your blood sugar dangerously low. Have a proper meal (rice or noodles) first, or switch to a light walk.", Chinese: "你今天几乎没吃东西。高强度运动可能使血糖降至危险水平。请先吃正餐（米饭或面条），或改为轻松散步。", Malay: "Anda hampir tidak makan hari ini. Senaman intensiti tinggi boleh menurunkan gula darah dengan berbahaya. Makan makanan penuh (nasi atau mi) dahulu, atau tukar ke jalan ringan.", Tamil: "இன்று கிட்டத்தட்ட சாப்பிடவில்லை. அதிக தீவிரமான உடற்பயிற்சி இரத்த சர்க்கரையை ஆபத்தான அளவுக்கு குறைக்கலாம். முதலில் சரியான உணவு (சாதம் அல்லது நூடுல்ஸ்) சாப்பிடுங்கள், அல்லது இலகுவான நடைக்கு மாறுங்கள்." },
  result_b_title: { English: "No action needed 👌", Chinese: "无需采取行动 👌", Malay: "Tiada tindakan diperlukan 👌", Tamil: "எந்த நடவடிக்கையும் தேவையில்லை 👌" },
  result_b_body: { English: "Since you're skipping the workout, your blood sugar should stay stable. No snack needed right now.", Chinese: "既然你今天跳过训练，血糖应该会保持稳定。现在不需要加餐。", Malay: "Memandangkan anda melangkau senaman, gula darah anda sepatutnya kekal stabil. Tiada snek diperlukan sekarang.", Tamil: "உடற்பயிற்சியை தவிர்ப்பதால், இரத்த சர்க்கரை நிலையாக இருக்கும். இப்போது சிற்றுண்டி தேவையில்லை." },
  result_c1_title: { English: "You're fine for now 🕐", Chinese: "目前没问题 🕐", Malay: "Anda baik buat masa ini 🕐", Tamil: "இப்போது நீங்கள் நலமாக இருக்கிறீர்கள் 🕐" },
  result_c1_body: { English: "Since you just ate and you're delaying the session, you're good. Check your blood sugar again 30 min before your new start time.", Chinese: "你刚吃完东西并且推迟了训练，目前状况良好。在新的开始时间前 30 分钟再次检查血糖。", Malay: "Memandangkan anda baru makan dan menangguhkan sesi, anda baik. Semak gula darah anda semula 30 minit sebelum masa mula baru.", Tamil: "நீங்கள் இப்போதுதான் சாப்பிட்டீர்கள் மற்றும் அமர்வை தாமதப்படுத்துகிறீர்கள், நலமாக இருக்கிறீர்கள். புதிய தொடக்க நேரத்திற்கு 30 நிமிடம் முன்பு மீண்டும் இரத்த சர்க்கரையை சரிபாருங்கள்." },
  result_c2_title: { English: "Eat something now 🍘", Chinese: "现在吃点东西 🍘", Malay: "Makan sesuatu sekarang 🍘", Tamil: "இப்போதே ஏதாவது சாப்பிடுங்கள் 🍘" },
  result_c2_body: { English: "Even with a later start, it's been a while since you ate. Have the cream crackers + cheese now to keep your levels up.", Chinese: "即使推迟开始时间，距上次进餐已有一段时间。现在吃芝士苏打饼，维持血糖水平。", Malay: "Walaupun bermula lewat, sudah lama anda tidak makan. Makan biskut krim + keju sekarang untuk mengekalkan paras anda.", Tamil: "பிந்தைய தொடக்கம் இருந்தாலும், சாப்பிட்டு நேரம் ஆகிவிட்டது. இப்போது கிரீம் கிராக்கர்ஸ் + சீஸ் சாப்பிட்டு உங்கள் அளவை பராமரியுங்கள்." },
  ```

- [ ] **Step 2: Verify keys are present**

  Run:
  ```bash
  grep -c "inquiry_" frontend/src/lib/i18n.js
  ```
  Expected: `12` (12 lines containing "inquiry_")

  Run:
  ```bash
  grep -c "result_" frontend/src/lib/i18n.js
  ```
  Expected: at least `10` (5 result titles + 5 result bodies)

- [ ] **Step 3: Commit**

  ```bash
  git add frontend/src/lib/i18n.js
  git commit -m "feat(i18n): add 26 soft alert inquiry flow keys in 4 languages"
  ```

---

## Task 2: Update InputBar to accept initialText prop

**Files:**
- Modify: `frontend/src/components/InputBar.js`

- [ ] **Step 1: Add initialText prop and wire it up**

  Replace the existing component signature and state initialisation:

  Current code (lines 7–15):
  ```js
  export default function InputBar({
    onSendText,
    onSendAudio,
    onOpenSheet,
    disabled,
  }) {
    const { t } = useTranslation();
    const [text, setText] = useState("");
    const [showInput, setShowInput] = useState(false);
  ```

  Replace with:
  ```js
  export default function InputBar({
    onSendText,
    onSendAudio,
    onOpenSheet,
    disabled,
    initialText = "",
  }) {
    const { t } = useTranslation();
    const [text, setText] = useState(initialText);
    const [showInput, setShowInput] = useState(initialText !== "");
  ```

  Also add `useEffect` import — change the import line at the top of the file from:
  ```js
  import { useState, useRef } from "react";
  ```
  to:
  ```js
  import { useState, useRef, useEffect } from "react";
  ```

  And add this `useEffect` block right after the state declarations (before `handleSendText`):
  ```js
  useEffect(() => {
    if (initialText) {
      setText(initialText);
      setShowInput(true);
    }
  }, [initialText]);
  ```

- [ ] **Step 2: Verify the change compiles**

  ```bash
  cd frontend && npx tsc --noEmit 2>&1 | head -20
  ```
  Expected: no TypeScript errors (project uses JS so this may not apply; if it fails ignore and move on).

  Alternatively confirm the dev server starts without errors if already running.

- [ ] **Step 3: Commit**

  ```bash
  git add frontend/src/components/InputBar.js
  git commit -m "feat(InputBar): add initialText prop to pre-fill input from query param"
  ```

---

## Task 3: Implement soft-alert inquiry state machine

**Files:**
- Modify: `frontend/src/app/soft-alert/page.js`

This task replaces the entire state machine section. The background blobs, TopBar, content sections, and push notification remain unchanged.

- [ ] **Step 1: Update imports — add useRouter**

  Change the import block at the top of the file from:
  ```js
  import { useState, useCallback, useEffect } from "react";
  import Link from "next/link";
  import TopBar from "../../components/TopBar";
  import SugarChart from "../../components/SugarChart";
  import { useAuth } from "../../lib/useAuth";
  import { useTranslation } from "../../lib/i18n";
  ```
  to:
  ```js
  import { useState, useCallback, useEffect } from "react";
  import Link from "next/link";
  import { useRouter } from "next/navigation";
  import TopBar from "../../components/TopBar";
  import SugarChart from "../../components/SugarChart";
  import { useAuth } from "../../lib/useAuth";
  import { useTranslation } from "../../lib/i18n";
  ```

- [ ] **Step 2: Replace state declarations**

  Find and remove:
  ```js
  const [showAlert, setShowAlert] = useState(true);
  const [showReasoning, setShowReasoning] = useState(false);
  const [feedbackMode, setFeedbackMode] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackThanks, setFeedbackThanks] = useState(false);
  const [showPush, setShowPush] = useState(true);
  ```

  Replace with:
  ```js
  const router = useRouter();
  const [showAlert, setShowAlert] = useState(true);
  const [showPush, setShowPush] = useState(true);
  // inquiry state machine: "initial" | "inquiryQ1" | "inquiryQ2" | "result"
  const [inquiryState, setInquiryState] = useState("initial");
  const [q1Answer, setQ1Answer] = useState(null); // "going" | "delayed" | "cancelled"
  const [q2Answer, setQ2Answer] = useState(null); // "just_ate" | "few_hours" | "barely_eaten"
  ```

- [ ] **Step 3: Replace callbacks**

  Find and remove:
  ```js
  const dismissAlert = useCallback(() => {
    setShowAlert(false);
    setShowReasoning(false);
    setFeedbackMode(false);
    setFeedbackText("");
    setFeedbackThanks(false);
  }, []);

  const handleFeedbackSubmit = useCallback(() => {
    setFeedbackThanks(true);
    setTimeout(() => dismissAlert(), 1500);
  }, [dismissAlert]);
  ```

  Replace with:
  ```js
  const dismissAlert = useCallback(() => {
    setShowAlert(false);
  }, []);

  const handleChatRedirect = useCallback((prefillText) => {
    const encoded = encodeURIComponent(prefillText);
    router.push(`/chat?prefill=${encoded}`);
    setShowAlert(false);
  }, [router]);

  const getResultKey = useCallback(() => {
    if (q1Answer === "cancelled") return "b";
    if (q1Answer === "going") {
      if (q2Answer === "just_ate") return "a1";
      if (q2Answer === "few_hours") return "a2";
      if (q2Answer === "barely_eaten") return "a3";
    }
    if (q1Answer === "delayed") {
      if (q2Answer === "just_ate") return "c1";
      return "c2"; // few_hours or barely_eaten
    }
    return "a2"; // fallback
  }, [q1Answer, q2Answer]);

  const PREFILL = {
    a1: "I got a glucose alert before HIIT. I just ate, but want to know if I still need a snack before high-intensity exercise.",
    a2: "I got a glucose alert. I'm doing HIIT at 2pm and ate about 2–3 hours ago. I was told to have cream crackers — what else should I know?",
    a3: "I got a glucose alert and I've barely eaten today. I'm planning HIIT soon — how risky is this and what should I do?",
    b: "I just cancelled my workout after a glucose alert. Is there anything I should watch out for the rest of the day?",
    c1: "I delayed my gym session after a glucose alert. I ate recently — when should I check my blood sugar again?",
    c2: "I got a glucose alert and I'm delaying my workout. I haven't eaten much today — what should I eat now?",
  };
  ```

- [ ] **Step 4: Replace the modal JSX**

  Find the entire modal overlay block (from `{/* ── Soft Alert Modal Overlay ── */}` through its closing `</>`) and replace it with:

  ```jsx
  {/* ── Soft Alert Modal Overlay ── */}
  {showAlert && (
    <>
      <div className="fixed inset-0 bg-black/30 z-40" />
      <div className="fixed inset-0 z-50 flex items-center justify-center px-8">
        <div className="bg-white rounded-2xl p-6 shadow-xl max-w-[340px] w-full border-2 border-yellow-400">
          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-xl bg-yellow-50 flex items-center justify-center text-3xl">
              ⚠️
            </div>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-yellow-600 mb-2 text-center">
            {t("better_safe")}
          </h3>

          {/* Confidence badge */}
          <div className="flex justify-center mb-3">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border bg-yellow-100 text-yellow-700 border-yellow-300">
              {t("soft_alert_confidence")}: MEDIUM
            </span>
          </div>

          {/* Message */}
          <p className="text-sm text-gray-600 leading-relaxed text-center">
            {t("soft_alert_msg")}
          </p>

          {/* ── State machine ── */}
          {inquiryState === "initial" && (
            <div className="mt-5">
              <button
                onClick={() => setInquiryState("inquiryQ1")}
                className="w-full py-2 text-sm font-bold text-white bg-yellow-500 rounded-full hover:bg-yellow-600"
              >
                {t("inquiry_start")}
              </button>
            </div>
          )}

          {inquiryState === "inquiryQ1" && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-gray-700 text-center mb-3">
                {t("inquiry_q1")}
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => { setQ1Answer("going"); setInquiryState("inquiryQ2"); }}
                  className="w-full py-2 text-sm font-medium text-yellow-700 border border-yellow-400 rounded-full hover:bg-yellow-50"
                >
                  {t("inquiry_q1_a")}
                </button>
                <button
                  onClick={() => { setQ1Answer("delayed"); setInquiryState("inquiryQ2"); }}
                  className="w-full py-2 text-sm font-medium text-yellow-700 border border-yellow-400 rounded-full hover:bg-yellow-50"
                >
                  {t("inquiry_q1_b")}
                </button>
                <button
                  onClick={() => { setQ1Answer("cancelled"); setQ2Answer(null); setInquiryState("result"); }}
                  className="w-full py-2 text-sm font-medium text-gray-500 border border-gray-300 rounded-full hover:bg-gray-50"
                >
                  {t("inquiry_q1_c")}
                </button>
              </div>
            </div>
          )}

          {inquiryState === "inquiryQ2" && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-gray-700 text-center mb-3">
                {t("inquiry_q2")}
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => { setQ2Answer("just_ate"); setInquiryState("result"); }}
                  className="w-full py-2 text-sm font-medium text-yellow-700 border border-yellow-400 rounded-full hover:bg-yellow-50"
                >
                  {t("inquiry_q2_a")}
                </button>
                <button
                  onClick={() => { setQ2Answer("few_hours"); setInquiryState("result"); }}
                  className="w-full py-2 text-sm font-medium text-yellow-700 border border-yellow-400 rounded-full hover:bg-yellow-50"
                >
                  {t("inquiry_q2_b")}
                </button>
                <button
                  onClick={() => { setQ2Answer("barely_eaten"); setInquiryState("result"); }}
                  className="w-full py-2 text-sm font-medium text-orange-600 border border-orange-400 rounded-full hover:bg-orange-50"
                >
                  {t("inquiry_q2_c")}
                </button>
              </div>
            </div>
          )}

          {inquiryState === "result" && (() => {
            const key = getResultKey();
            const isA3 = key === "a3";
            return (
              <div className="mt-4">
                <div className={`rounded-lg p-3 mb-3 ${isA3 ? "bg-orange-50 border border-orange-200" : "bg-yellow-50 border border-yellow-200"}`}>
                  <p className={`text-sm font-bold mb-1 ${isA3 ? "text-orange-700" : "text-yellow-700"}`}>
                    {t(`result_${key}_title`)}
                  </p>
                  <p className="text-xs text-gray-700 leading-relaxed">
                    {t(`result_${key}_body`)}
                  </p>
                </div>
                <div className="space-y-2">
                  {isA3 && (
                    <button
                      onClick={dismissAlert}
                      className="w-full py-2 text-sm font-medium text-orange-600 border border-orange-400 rounded-full hover:bg-orange-50"
                    >
                      {t("inquiry_lighter_workout")}
                    </button>
                  )}
                  <button
                    onClick={() => handleChatRedirect(PREFILL[key])}
                    className="w-full py-2 text-sm font-bold text-white bg-yellow-500 rounded-full hover:bg-yellow-600"
                  >
                    {t("inquiry_chat")}
                  </button>
                  <button
                    onClick={dismissAlert}
                    className="w-full py-2 text-sm font-medium text-gray-500 border border-gray-300 rounded-full hover:bg-gray-50"
                  >
                    {t("inquiry_dismiss")}
                  </button>
                </div>
              </div>
            );
          })()}
        </div>
      </div>
    </>
  )}
  ```

- [ ] **Step 5: Verify visually**

  Start the frontend (`cd frontend && npm run dev`) and navigate to `http://localhost:3000/soft-alert`.
  Check:
  - Push notification appears, auto-dismisses after 4s
  - Modal shows initial state with "Answer 2 quick questions" button
  - Q1 → Q2 → result flow works for the path: "Yes, 2pm" → "About 2–3 hours ago" → result_a2 shows
  - "Ask the AI more →" navigates to `/chat?prefill=...` (URL should contain encoded text)
  - "Got it, thanks" dismisses the modal
  - Cancelled path (Q1 → "Cancelled") jumps straight to result_b without Q2

- [ ] **Step 6: Commit**

  ```bash
  git add frontend/src/app/soft-alert/page.js
  git commit -m "feat(soft-alert): replace static modal with 2-question inquiry flow + 6 result branches"
  ```

---

## Task 4: Update chat page to read ?prefill= query param

**Files:**
- Modify: `frontend/src/app/chat/page.js`

Next.js 15 App Router requires `useSearchParams()` to be called inside a component wrapped in `<Suspense>`. The cleanest approach: extract `ChatPageInner` (contains all current logic) and keep the default export as a thin `<Suspense>` wrapper.

- [ ] **Step 1: Update imports**

  Change the import block at the top from:
  ```js
  "use client";

  import { useState, useRef } from "react";
  import TopBar from "../../components/TopBar";
  import MessageList from "../../components/MessageList";
  import InputBar from "../../components/InputBar";
  import ActionSheet from "../../components/ActionSheet";
  import ImagePreview from "../../components/ImagePreview";
  import { sendMessageStream } from "../../lib/api";
  import { useAuth } from "../../lib/useAuth";
  import { useTranslation } from "../../lib/i18n";
  ```

  To:
  ```js
  "use client";

  import { useState, useRef, Suspense } from "react";
  import { useSearchParams } from "next/navigation";
  import TopBar from "../../components/TopBar";
  import MessageList from "../../components/MessageList";
  import InputBar from "../../components/InputBar";
  import ActionSheet from "../../components/ActionSheet";
  import ImagePreview from "../../components/ImagePreview";
  import { sendMessageStream } from "../../lib/api";
  import { useAuth } from "../../lib/useAuth";
  import { useTranslation } from "../../lib/i18n";
  ```

- [ ] **Step 2: Rename the component and add prefill**

  Change `export default function ChatPage()` to `function ChatPageInner()`.

  Inside the function body, right after `const { t } = useTranslation();`, add:
  ```js
  const prefill = useSearchParams().get("prefill") ?? "";
  ```

  Then find the `<InputBar>` JSX (currently lines 143–148):
  ```jsx
  <InputBar
    onSendText={handleSendText}
    onSendAudio={handleSendAudio}
    onOpenSheet={() => setSheetOpen(true)}
    disabled={isLoading}
  />
  ```

  Add the `initialText` prop:
  ```jsx
  <InputBar
    onSendText={handleSendText}
    onSendAudio={handleSendAudio}
    onOpenSheet={() => setSheetOpen(true)}
    disabled={isLoading}
    initialText={prefill}
  />
  ```

- [ ] **Step 3: Add the thin wrapper default export**

  After the closing `}` of `ChatPageInner`, add:
  ```js
  export default function ChatPage() {
    return (
      <Suspense fallback={null}>
        <ChatPageInner />
      </Suspense>
    );
  }
  ```

- [ ] **Step 4: Verify the full flow**

  With the dev server running, navigate to:
  ```
  http://localhost:3000/chat?prefill=Hello%20from%20soft%20alert
  ```
  Expected:
  - Chat page loads
  - Text input box is visible (not hidden behind the Aa button)
  - Input is pre-filled with "Hello from soft alert"
  - User can hit Enter/send button and message is sent normally

  Then navigate to `http://localhost:3000/chat` (no query param):
  - Input box is hidden by default (Aa button required to show it)
  - No prefill text

- [ ] **Step 5: End-to-end demo flow**

  1. Go to `/soft-alert`
  2. Tap "Answer 2 quick questions"
  3. Select "Yes, heading to gym at 2pm"
  4. Select "About 2–3 hours ago"
  5. Tap "Ask the AI more →"
  6. Verify chat page opens with prefilled text about cream crackers

- [ ] **Step 6: Commit**

  ```bash
  git add frontend/src/app/chat/page.js
  git commit -m "feat(chat): add Suspense boundary and ?prefill= query param support"
  ```

---

## Self-Review Checklist

- [x] **Spec coverage:** All 4 files from spec covered. State machine: initial → Q1 → Q2 → result (+ B shortcut). 6 result keys (a1/a2/a3/b/c1/c2). 26 i18n keys. Prefill strings for all 6 results. Suspense boundary. InputBar initialText prop.
- [x] **No placeholders:** All code blocks are complete and self-contained.
- [x] **Type consistency:** `getResultKey()` returns string keys matching `PREFILL` object keys and i18n key fragments. `t("result_${key}_title")` and `t("result_${key}_body")` match the keys added in Task 1.
- [x] **Dependency order:** Task 1 (i18n) and Task 2 (InputBar) are independent. Task 3 (soft-alert) depends on Task 1 keys being present. Task 4 (chat) depends on Task 2 InputBar prop being present.
- [x] **No backend changes:** All tasks are frontend-only.
