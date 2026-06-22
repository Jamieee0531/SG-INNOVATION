import { test } from "node:test";
import assert from "node:assert/strict";
import { classifyQuestion, runAnalysis } from "./runAnalysis.mjs";

test("routes glucose questions", () => {
  assert.equal(classifyQuestion("我最近血糖怎么样"), "glucose");
});

test("routes exercise questions", () => {
  assert.equal(classifyQuestion("我这周运动够吗"), "exercise");
});

test("routes diet questions", () => {
  assert.equal(classifyQuestion("我吃得健康吗"), "diet");
});

test("unknown question defaults to glucose", () => {
  assert.equal(classifyQuestion("你好呀"), "glucose");
});

test("runAnalysis returns a chart spec and a non-empty insight", () => {
  const r = runAnalysis("血糖");
  assert.equal(r.chart.chartType, "glucose");
  assert.ok(typeof r.insight === "string" && r.insight.length > 0);
});

test("exercise analysis sums minutes", () => {
  const r = runAnalysis("运动");
  assert.equal(r.chart.chartType, "exercise");
  assert.ok(r.chart.data.length === 7);
});

test("every dimension returns a non-empty plan", () => {
  for (const q of ["血糖", "运动", "吃"]) {
    const r = runAnalysis(q);
    assert.ok(Array.isArray(r.plan.steps) && r.plan.steps.length > 0, `plan missing for ${q}`);
  }
});

test("glucose daily mock carries min/max for the range band", () => {
  const r = runAnalysis("血糖");
  assert.ok(r.chart.data.every((d) => typeof d.min === "number" && typeof d.max === "number"));
});
