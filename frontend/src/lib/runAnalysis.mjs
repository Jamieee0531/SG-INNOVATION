import { ANALYSIS_MOCK } from "./analysisMock.mjs";

const KEYWORDS = {
  exercise: ["运动", "锻炼", "走", "步", "exercise", "walk", "step"],
  diet: ["吃", "饮食", "卡路里", "热量", "餐", "diet", "eat", "calorie"],
  glucose: ["血糖", "糖", "glucose", "sugar", "tir", "范围"],
};

// Pick the dimension. Exercise/diet are checked before glucose so a question
// like "运动后血糖" is treated as exercise; unknown questions default to glucose.
export function classifyQuestion(question) {
  const q = (question || "").toLowerCase();
  for (const dim of ["exercise", "diet", "glucose"]) {
    if (KEYWORDS[dim].some((kw) => q.includes(kw))) return dim;
  }
  return "glucose";
}

export function runAnalysis(question) {
  const dim = classifyQuestion(question);

  if (dim === "exercise") {
    const data = ANALYSIS_MOCK.exercise;
    const total = data.reduce((s, d) => s + d.minutes, 0);
    const activeDays = data.filter((d) => d.minutes > 0).length;
    return {
      chart: { chartType: "exercise", data, meta: { unit: "min" } },
      insight: `本周运动 ${activeDays} 天、共 ${total} 分钟，${
        total >= 150 ? "已达到每周 150 分钟目标。" : "离每周 150 分钟目标还差一点。"
      }`,
    };
  }

  if (dim === "diet") {
    const data = ANALYSIS_MOCK.diet;
    const avg = Math.round(data.reduce((s, d) => s + d.kcal, 0) / data.length);
    const peak = data.reduce((m, d) => (d.kcal > m.kcal ? d : m), data[0]);
    return {
      chart: { chartType: "diet", data, meta: { unit: "kcal" } },
      insight: `本周日均约 ${avg} 大卡，${peak.day}偏高（${peak.kcal} 大卡）。`,
    };
  }

  const { daily, tir } = ANALYSIS_MOCK.glucose;
  return {
    chart: { chartType: "glucose", data: daily, meta: { tir } },
    insight: `过去 7 天 ${tir.inRange}% 时间血糖在健康范围内 (3.9–10)，整体${
      tir.inRange >= 70 ? "平稳" : "波动偏大"
    }。`,
  };
}
