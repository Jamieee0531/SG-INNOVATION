"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import TopBar from "../../components/TopBar";
import SugarChart from "../../components/SugarChart";
import { useAuth } from "../../lib/useAuth";
import { useTranslation } from "../../lib/i18n";

export default function SoftAlertPage() {
  const { user, loading } = useAuth();
  const { t } = useTranslation();

  const router = useRouter();
  const [showAlert, setShowAlert] = useState(true);
  const [showPush, setShowPush] = useState(true);
  // inquiry state machine: "initial" | "inquiryQ1" | "inquiryQ2" | "result"
  const [inquiryState, setInquiryState] = useState("initial");
  const [q1Answer, setQ1Answer] = useState(null); // "going" | "delayed" | "cancelled"
  const [q2Answer, setQ2Answer] = useState(null); // "just_ate" | "few_hours" | "barely_eaten"

  // Auto-dismiss push after 4s
  useEffect(() => {
    const timer = setTimeout(() => setShowPush(false), 4000);
    return () => clearTimeout(timer);
  }, []);

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

  if (loading || !user) return null;

  return (
    <div className="flex flex-col h-full bg-cream relative overflow-hidden">
      {/* ── Background blobs ── */}
      <div
        className="absolute z-0"
        style={{
          width: 500, height: 500, borderRadius: "50%",
          backgroundColor: "#EBE9E9",
          top: 250, left: 100,
        }}
      />
      <div
        className="absolute z-[1]"
        style={{
          width: 580, height: 580, borderRadius: "50%",
          backgroundColor: "#FBE6E1",
          top: -210, left: -250,
        }}
      />
      <div
        className="absolute z-[1]"
        style={{
          width: 650, height: 650, borderRadius: "50%",
          backgroundColor: "#CEF7EA",
          bottom: -300, left: -300,
        }}
      />

      {/* ── TopBar ── */}
      <div className="relative z-30">
        <TopBar title={t("nav_home")} transparent />
      </div>

      {/* ── Content ── */}
      <div className="relative z-10 flex-1 flex flex-col px-5 pb-4">

        {/* ====== SECTION 1: Top-left — Greeting ====== */}
        <div style={{ minHeight: 255 }}>
          <h2 className="text-2xl font-bold italic text-[#e8927c] -mt-1">
            {t("good_morning")} {user.name.split(" ")[0]}!
          </h2>

          <p className="text-base italic text-[#F4B95D] mt-0.5">
            {t("how_feeling")}
          </p>

          <Link
            href="/chat"
            className="inline-block mt-3 px-6 py-2 text-sm font-medium text-gray-700 border border-[#e8c8a0] rounded-full bg-[#fce8d0]/40 hover:bg-[#fce8d0] w-fit"
          >
            {t("chat_with_ai")}
          </Link>

          <img
            src="/healthy_life.jpg"
            alt="Healthy lifestyle"
            className="w-[160px] h-auto object-contain mt-2 -ml-1"
          />
        </div>

        {/* ====== SECTION 2: Middle-right — Snapshot + Stats + Tasks + Flower ====== */}
        <div className="self-end -mt-20 mr-0 text-right w-[55%]">
          <h3 className="text-xl font-bold italic text-[#88B3F9] leading-tight">
            {t("todays_snapshot")}
          </h3>
          <div className="mt-3 space-y-0.5 text-sm text-gray-800 text-right pr-1">
            <p><span className="font-semibold">Step Count:</span> 1234</p>
            <p><span className="font-semibold">{t("bmi")}</span> 23.0</p>
            <p><span className="font-semibold">{t("meals_logged")}</span> 1/3</p>
          </div>

          <Link
            href="/task"
            className="inline-block mt-3 px-5 py-1.5 text-sm font-medium text-gray-700 border border-gray-400 rounded-full hover:bg-gray-100"
          >
            {t("view_tasks")}
          </Link>

          <img
            src="/flower.jpg"
            alt="Decorative flower"
            className="w-[100px] h-auto object-contain mt-2 ml-auto"
          />
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* ====== SECTION 3: Bottom-left — Check your sugar + Chart ====== */}
        <div className="w-[70%]">
          <h3 className="text-2xl font-bold italic text-[#454545] leading-tight">
            {t("check_sugar")}
          </h3>
          <SugarChart />
        </div>
      </div>

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

      {/* ── Simulated Push Notification ── */}
      {showPush && (
        <div
          className="fixed top-4 left-4 right-4 z-[60] animate-slide-down cursor-pointer"
          onClick={() => setShowPush(false)}
        >
          <div className="flex items-center gap-3 p-3 rounded-2xl shadow-lg backdrop-blur-md bg-yellow-50/95 border border-yellow-200">
            <div className="w-10 h-10 rounded-xl bg-yellow-100 flex items-center justify-center text-lg shrink-0">
              ⚠️
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-gray-900 uppercase tracking-wide">
                {t("soft_push_title")}
              </p>
              <p className="text-xs text-gray-600 truncate">
                {t("soft_push_body")}
              </p>
            </div>
            <span className="text-[10px] text-gray-400 shrink-0">now</span>
          </div>
        </div>
      )}
    </div>
  );
}
