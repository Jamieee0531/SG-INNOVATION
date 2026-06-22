"use client";

// Generic hand-rolled SVG bar chart. No charting library.
// Props: data = [{ label, value }], color (bar fill).
export default function BarChart({ data = [], color = "#88B3F9" }) {
  if (!data.length) return null;
  const W = 300, H = 140, padL = 30, padB = 22, padT = 12;
  const max = Math.max(...data.map((d) => d.value), 1);
  const slot = (W - padL - 10) / data.length;
  const barW = slot * 0.6;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
      <line x1={padL} y1={padT} x2={padL} y2={H - padB} stroke="#333" strokeWidth="1" />
      <line x1={padL} y1={H - padB} x2={W - 5} y2={H - padB} stroke="#333" strokeWidth="1" />
      {data.map((d, i) => {
        const h = ((H - padT - padB) * d.value) / max;
        const x = padL + slot * i + (slot - barW) / 2;
        const y = H - padB - h;
        return (
          <g key={d.label || i}>
            <rect x={x} y={y} width={barW} height={h} rx="2" fill={color} />
            <text x={x + barW / 2} y={H - padB + 12} fontSize="8" fill="#666" textAnchor="middle">
              {d.label}
            </text>
            {d.value > 0 && (
              <text x={x + barW / 2} y={y - 2} fontSize="7" fill="#999" textAnchor="middle">
                {d.value}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
