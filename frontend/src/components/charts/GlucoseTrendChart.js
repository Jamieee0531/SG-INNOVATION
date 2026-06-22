"use client";

// Hand-rolled SVG glucose trend line with a shaded target band (3.9–10 mmol/L).
// Props: data = [{ day, avg }].
export default function GlucoseTrendChart({ data = [] }) {
  if (!data.length) return null;
  const W = 300, H = 150, padL = 30, padB = 22, padT = 10;
  const yLo = 3, yHi = 12; // fixed clinical y-range so the band is meaningful
  const yToPx = (v) => H - padB - ((v - yLo) / (yHi - yLo)) * (H - padT - padB);
  const xAt = (i) => padL + (i / Math.max(data.length - 1, 1)) * (W - padL - 10);

  const bandTop = yToPx(10);
  const bandBottom = yToPx(3.9);
  const linePath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${xAt(i).toFixed(1)} ${yToPx(d.avg).toFixed(1)}`)
    .join(" ");

  const hasRange = data.every((d) => typeof d.min === "number" && typeof d.max === "number");
  const topPts = data.map((d, i) => `${xAt(i).toFixed(1)},${yToPx(d.max).toFixed(1)}`);
  const botPts = data.map((d, i) => `${xAt(i).toFixed(1)},${yToPx(d.min).toFixed(1)}`).reverse();
  const rangeArea = hasRange ? `M ${topPts.join(" L ")} L ${botPts.join(" L ")} Z` : null;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
      {/* target range band 3.9–10 */}
      <rect x={padL} y={bandTop} width={W - padL - 10} height={bandBottom - bandTop}
            fill="#CEF7EA" opacity="0.6" />
      {rangeArea && <path d={rangeArea} fill="#e8927c" opacity="0.15" />}
      <line x1={padL} y1={padT} x2={padL} y2={H - padB} stroke="#333" strokeWidth="1" />
      <line x1={padL} y1={H - padB} x2={W - 5} y2={H - padB} stroke="#333" strokeWidth="1" />
      <path d={linePath} fill="none" stroke="#e8927c" strokeWidth="1.8"
            strokeLinecap="round" strokeLinejoin="round" />
      {data.map((d, i) => (
        <g key={d.day || i}>
          <circle cx={xAt(i)} cy={yToPx(d.avg)} r="2.2" fill="#e8927c" />
          <text x={xAt(i)} y={H - padB + 12} fontSize="8" fill="#666" textAnchor="middle">
            {d.day}
          </text>
        </g>
      ))}
    </svg>
  );
}
