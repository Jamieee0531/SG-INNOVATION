"use client";

import GlucoseTrendChart from "./charts/GlucoseTrendChart";
import BarChart from "./charts/BarChart";

// Renders one analysis result: the chart + a one-line insight, in a card.
export default function AnalysisChart({ chart, insight }) {
  if (!chart) return null;

  let body = null;
  if (chart.chartType === "glucose") {
    body = <GlucoseTrendChart data={chart.data} />;
  } else if (chart.chartType === "exercise") {
    body = <BarChart data={chart.data.map((d) => ({ label: d.day, value: d.minutes }))} color="#88B3F9" />;
  } else if (chart.chartType === "diet") {
    body = <BarChart data={chart.data.map((d) => ({ label: d.day, value: d.kcal }))} color="#F4B95D" />;
  }

  return (
    <div className="bg-white rounded-2xl p-3 shadow-sm max-w-[280px]">
      {body}
      {insight && <p className="text-sm text-gray-700 mt-2 leading-snug">{insight}</p>}
    </div>
  );
}
