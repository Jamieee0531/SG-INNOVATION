"use client";

import { useState, useEffect } from "react";

// Shows the analysis plan with steps revealing one-by-one ("thinking" feel).
export default function PlanCard({ steps = [] }) {
  const [shown, setShown] = useState(0);

  useEffect(() => {
    if (shown >= steps.length) return;
    const t = setTimeout(() => setShown((n) => n + 1), 450);
    return () => clearTimeout(t);
  }, [shown, steps.length]);

  return (
    <div className="bg-white rounded-2xl p-3 shadow-sm max-w-[280px]">
      <p className="text-xs font-semibold text-gray-500 mb-2">📋 分析计划</p>
      <ol className="space-y-1">
        {steps.slice(0, shown).map((s, i) => (
          <li key={i} className="text-sm text-gray-700 flex gap-1.5">
            <span className="text-gray-400">{i + 1}.</span>
            <span>{s}</span>
          </li>
        ))}
        {shown < steps.length && <li className="text-sm text-gray-400">…</li>}
      </ol>
    </div>
  );
}
