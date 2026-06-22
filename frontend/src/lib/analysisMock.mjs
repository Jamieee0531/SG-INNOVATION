// 7-day mock health data for Analysis mode. Self-contained, no backend.
// Internally consistent: the high-glucose day (周三) lines up with the
// highest-kcal, zero-exercise day, so a later cross-dimension story reads well.
export const ANALYSIS_MOCK = {
  glucose: {
    daily: [
      { day: "周一", avg: 7.2, min: 5.8, max: 9.4 },
      { day: "周二", avg: 6.9, min: 5.5, max: 8.6 },
      { day: "周三", avg: 9.1, min: 6.9, max: 12.8 },
      { day: "周四", avg: 7.6, min: 6.0, max: 10.1 },
      { day: "周五", avg: 7.0, min: 5.6, max: 9.0 },
      { day: "周六", avg: 8.3, min: 6.4, max: 11.2 },
      { day: "周日", avg: 7.1, min: 5.7, max: 9.2 },
    ],
    tir: { inRange: 78, below: 6, above: 16 },
  },
  exercise: [
    { day: "周一", minutes: 30 },
    { day: "周二", minutes: 45 },
    { day: "周三", minutes: 0 },
    { day: "周四", minutes: 25 },
    { day: "周五", minutes: 40 },
    { day: "周六", minutes: 0 },
    { day: "周日", minutes: 20 },
  ],
  diet: [
    { day: "周一", kcal: 1820 },
    { day: "周二", kcal: 1760 },
    { day: "周三", kcal: 2300 },
    { day: "周四", kcal: 1900 },
    { day: "周五", kcal: 1850 },
    { day: "周六", kcal: 2150 },
    { day: "周日", kcal: 1880 },
  ],
};
