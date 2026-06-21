# Soft Alert Inquiry Flow — Design Spec
Date: 2026-06-21
Status: Approved

## Summary

Replace the soft alert modal's single-direction recommendation with a 2-question
inquiry flow. The user answers structured questions about their exercise intent and
last meal, receives a context-specific recommendation, then can either dismiss or
redirect to the chatbot with pre-filled context for free-form follow-up.

**Scope: frontend only. No backend changes.**

---

## Motivation

Current soft alert tells the user what to do without knowing their actual situation.
VitalDiagnosis (AAAI 2026) proposes a Clinical Inquiry Generator that gathers context
before producing a recommendation. Adding 2 targeted questions makes the
recommendation branch-specific and sets up the chatbot redirect as a natural
continuation (aligned with PHA's Health Coach Agent concept).

---

## Files Changed

| File | Change |
|---|---|
| `frontend/src/app/soft-alert/page.js` | Replace existing state machine with inquiry flow |
| `frontend/src/app/chat/page.js` | Read `?prefill=` query param; pass to InputBar |
| `frontend/src/components/InputBar.js` | Accept `initialText` prop for pre-filled input |
| `frontend/src/lib/i18n.js` | Add new i18n keys (see below) |

---

## State Machine

States (replaces existing `showReasoning` / `feedbackMode` / `feedbackThanks`):

```
initial → inquiryQ1 → inquiryQ2 → result
                   ↘ (Q1 = cancelled) → result_b (skip Q2)
```

### State: `initial`
Show: current glucose, predicted drop, prediction summary.
Button: `[t("inquiry_start")]` — transitions to `inquiryQ1`.

> Remove the current "Got it" / "Why?" split. The single entry point is the
> inquiry. This is intentional: context collection comes before recommendation.

### State: `inquiryQ1`
Question: `t("inquiry_q1")`

Three buttons (each sets `q1Answer` and transitions):
- `t("inquiry_q1_a")` → `q1Answer = "going"` → `inquiryQ2`
- `t("inquiry_q1_b")` → `q1Answer = "delayed"` → `inquiryQ2`
- `t("inquiry_q1_c")` → `q1Answer = "cancelled"` → `result` (skip Q2)

### State: `inquiryQ2`
Only reached when `q1Answer = "going"` or `"delayed"`.
Question: `t("inquiry_q2")`

Three buttons (each sets `q2Answer` and transitions to `result`):
- `t("inquiry_q2_a")` → `q2Answer = "just_ate"`
- `t("inquiry_q2_b")` → `q2Answer = "few_hours"`
- `t("inquiry_q2_c")` → `q2Answer = "barely_eaten"`

### State: `result`
Determined by `(q1Answer, q2Answer)` — see Result Table below.
Each result shows:
1. Headline + recommendation text (from i18n)
2. Two buttons:
   - `[t("inquiry_dismiss")]` → `dismissAlert()`
   - `[t("inquiry_chat")]` → `router.push("/chat?prefill=<encoded>")` then `dismissAlert()`

Result A3 exception: shows a third option `[t("inquiry_lighter_workout")]`
(same dismiss behaviour, different label) alongside the chat button.

---

## Result Table

| q1Answer | q2Answer | Result key | Tone |
|---|---|---|---|
| going | just_ate | `result_a1` | Reassuring — bring snack as backup |
| going | few_hours | `result_a2` | Standard — eat crackers now (Scenario A) |
| going | barely_eaten | `result_a3` | Escalated — eat a meal or reduce intensity |
| delayed | just_ate | `result_c1` | Calm — check back before new start |
| delayed | few_hours or barely_eaten | `result_c2` | Proactive — eat now even if delayed |
| cancelled | (any / null) | `result_b` | Reassuring — no action needed |

---

## Prefill Text Per Result

Constructed in JS (not from i18n — English only, sent to chatbot API):

| Result | Prefill string |
|---|---|
| a1 | `"I got a glucose alert before HIIT. I just ate, but want to know if I still need a snack before high-intensity exercise."` |
| a2 | `"I got a glucose alert. I'm doing HIIT at 2pm and ate about 2–3 hours ago. I was told to have cream crackers — what else should I know?"` |
| a3 | `"I got a glucose alert and I've barely eaten today. I'm planning HIIT soon — how risky is this and what should I do?"` |
| b | `"I just cancelled my workout after a glucose alert. Is there anything I should watch out for the rest of the day?"` |
| c1 | `"I delayed my gym session after a glucose alert. I ate recently — when should I check my blood sugar again?"` |
| c2 | `"I got a glucose alert and I'm delaying my workout. I haven't eaten much today — what should I eat now?"` |

---

## i18n Keys to Add

All four languages (English / Chinese / Malay / Tamil) required.
Add to the `// ── Soft Alert ──` section in `i18n.js`.

| Key | English |
|---|---|
| `inquiry_start` | `"Answer 2 quick questions for better advice"` |
| `inquiry_q1` | `"Are you still planning to work out today?"` |
| `inquiry_q1_a` | `"Yes, heading to gym at 2pm"` |
| `inquiry_q1_b` | `"Might delay it a bit"` |
| `inquiry_q1_c` | `"Cancelled for today"` |
| `inquiry_q2` | `"When did you last eat something?"` |
| `inquiry_q2_a` | `"Just ate (under 1 hour ago)"` |
| `inquiry_q2_b` | `"About 2–3 hours ago"` |
| `inquiry_q2_c` | `"Barely eaten today (4+ hours)"` |
| `inquiry_dismiss` | `"Got it, thanks"` |
| `inquiry_chat` | `"Ask the AI more →"` |
| `inquiry_lighter_workout` | `"Switch to a lighter workout"` |
| `result_a1_title` | `"You're in decent shape 👍"` |
| `result_a1_body` | `"You just ate, so you have a buffer. Pack 2 cream crackers just in case — eat them if you feel dizzy mid-session."` |
| `result_a2_title` | `"Eat something before you go 🍘"` |
| `result_a2_body` | `"It's been a while since your last meal. Your blood sugar could drop to ~3.87 during HIIT. Have 2 cream crackers + cheese now, then head out in 20 minutes."` |
| `result_a3_title` | `"Please eat a meal first ⚠️"` |
| `result_a3_body` | `"You've barely eaten today. High-intensity exercise could push your blood sugar dangerously low. Have a proper meal (rice or noodles) first, or switch to a light walk."` |
| `result_b_title` | `"No action needed 👌"` |
| `result_b_body` | `"Since you're skipping the workout, your blood sugar should stay stable. No snack needed right now."` |
| `result_c1_title` | `"You're fine for now 🕐"` |
| `result_c1_body` | `"Since you just ate and you're delaying the session, you're good. Check your blood sugar again 30 min before your new start time."` |
| `result_c2_title` | `"Eat something now 🍘"` |
| `result_c2_body` | `"Even with a later start, it's been a while since you ate. Have the cream crackers + cheese now to keep your levels up."` |

Chinese translations for all keys are required; Malay and Tamil can be
approximate for demo purposes.

---

## Chat Page Change

In `frontend/src/app/chat/page.js`:

1. Import `useSearchParams` and `Suspense` from `"next/navigation"` and `"react"`.
2. `useSearchParams()` requires a `<Suspense>` boundary in Next.js 15 App Router.
   Wrap the inner component that calls `useSearchParams()` in a `<Suspense fallback={null}>`.
   Simplest pattern: extract a `ChatPageInner` component that reads the param,
   keep the default export as a thin wrapper: `<Suspense fallback={null}><ChatPageInner /></Suspense>`.
3. Read `const prefill = useSearchParams().get("prefill") ?? ""` inside `ChatPageInner`.
4. Pass `initialText={prefill}` to `<InputBar>`.

## InputBar Change

In `frontend/src/components/InputBar.js`:

1. Accept new prop `initialText = ""`.
2. Change `useState("")` to `useState(initialText)`.
3. On mount (or when `initialText` changes), also call `setShowInput(true)` if
   `initialText` is non-empty, so the input box is visible immediately.

---

## What Is NOT Changed

- Hard alert page — untouched.
- Backend (Gateway, Alert Agent, Chatbot API) — untouched.
- Existing `showReasoning` / `feedbackMode` states — removed and replaced entirely.
- Existing `soft_alert_msg`, `soft_alert_demo_reasoning` i18n keys — kept (still
  used in the `initial` state to show the push notification text and the glucose
  prediction summary).

---

## Demo Flow (Scenario A)

1. Page loads → push notification banner auto-dismisses after 4s.
2. Modal shows `initial` state: "Your blood sugar is 4.9, predicted drop 1.03…"
   + `[Answer 2 quick questions]` button.
3. User taps → `inquiryQ1`: "Still going to the gym?" → taps "Yes, 2pm".
4. → `inquiryQ2`: "Last meal?" → taps "About 2–3 hours ago".
5. → `result_a2`: "Eat 2 cream crackers now…"
   - `[Got it, thanks]` → dismiss
   - `[Ask the AI more →]` → navigate to `/chat?prefill=I+got+a+glucose+alert...`
6. Chat page opens with input pre-filled; user hits send → Expert Agent responds
   with personalised advice.
