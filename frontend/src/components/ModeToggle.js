"use client";

// Segmented toggle between Chat and Analysis modes. Purely additive UI.
export default function ModeToggle({ mode = "chat", onChange }) {
  const base = "flex-1 py-1.5 text-sm rounded-full transition-colors text-center";
  return (
    <div className="flex gap-1 mx-4 mb-2 p-1 bg-gray-100 rounded-full">
      <button
        onClick={() => onChange("chat")}
        className={`${base} ${mode === "chat" ? "bg-white shadow font-semibold" : "text-gray-500"}`}
      >
        💬 Chat
      </button>
      <button
        onClick={() => onChange("analysis")}
        className={`${base} ${mode === "analysis" ? "bg-white shadow font-semibold" : "text-gray-500"}`}
      >
        📊 Analysis
      </button>
    </div>
  );
}
