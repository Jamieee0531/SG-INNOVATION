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
