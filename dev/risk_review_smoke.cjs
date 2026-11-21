// Synthetic pre-race fixtures only. No scraping, subscriptions or live data.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("index.html", "utf8");
let code = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert(code, "Inline app script missing");
code = code.slice(0, code.lastIndexOf("configureGame(preferredGameType("));
const nodes = new Map();
function dom(id) {
  if (!nodes.has(id)) nodes.set(id, {
    value: "", innerHTML: "", textContent: "",
    querySelectorAll: () => [],
    addEventListener: () => {},
    insertAdjacentHTML(_position, content) {this.innerHTML = content + this.innerHTML;},
  });
  return nodes.get(id);
}
const ctx = vm.createContext({
  document: {getElementById: dom}, window: {},
  localStorage: {getItem: () => null, setItem: () => {}},
  Date, String, Number, console,
});
vm.runInContext(code, ctx);
vm.runInContext("save=()=>{};", ctx);
dom("budget").value = "300";

function horse(num, opts = {}) {
  return {num, name: `Häst ${num}`, selected: num === 1,
    form: 5, development: 5, driver: 5, conditions: 5,
    position: 5, equipment: 5, reliability: 5, streak: "",
    ...opts};
}
function fixture(legs, horses) {
  const data = Array.from({length: legs}, (_, i) => ({
    horses: Array.from({length: horses}, (_, j) => horse(j + 1, {name: `Avd ${i + 1} häst ${j + 1}`})),
  }));
  vm.runInContext(`configureGame("${legs === 7 ? "V75" : "V85"}",true); races=${JSON.stringify(data)};`, ctx);
}
function evaluate(source) {return vm.runInContext(source, ctx);}

// The missing long shot must appear before start even when omitted from the ticket.
fixture(8, 6);
const fiveStarts = Array.from({length: 5}, (_, j) => ({
  date: `2026-11-${String(10 + j).padStart(2, "0")}`,
  country: j === 0 ? "NO" : "SE", place: j % 2 ? 2 : 1, distance: 2140,
  source: "Testfixture – egen källa",
}));
evaluate(`races[2].horses[5]={...races[2].horses[5],num:12,name:"Bortvald skräll",streak:"2.1",form:9,development:8,driver:8,history:${JSON.stringify(fiveStarts)}};`);
const audit = evaluate("reviewExcluded()");
assert.equal(audit.length, 40, "Every omitted horse in eight legs must be reviewed");
const twelve = audit.find(h => h.leg === 3 && h.num === 12);
assert(twelve, "The omitted #12 should be visible");
assert.equal(twelve.severity, "high");
assert(twelve.edge > 4, "Difference vs market should be visible");
assert.equal(twelve.historyCount, 5);
assert.equal(twelve.foreignStarts, 1);
assert(twelve.reasons.join(" ").includes("streck"));
evaluate("renderRiskReview()");
assert.match(dom("riskreview").innerHTML, /Bortvald skräll/);
assert.match(dom("riskreview").innerHTML, /Granska särskilt/);

// No result dated at/after the current round may inform its earlier forecast.
dom("date").value = "2026-11-21";
const beforeLateResult = evaluate("score(races[2].horses[5])");
evaluate(`races[2].horses[5].history.push({date:"2026-11-22",place:1,country:"SE",source:"Test – too late"},{place:1,country:"SE",source:"Test – undated"});`);
assert.equal(evaluate("historyStats(races[2].horses[5]).count"), 5);
assert.equal(evaluate("historyStats(races[2].horses[5]).excludedByDate"), 2);
assert.equal(evaluate("score(races[2].horses[5])"), beforeLateResult);
evaluate("renderRiskReview()");
assert.match(dom("riskreview").innerHTML, /historikposter på\/efter omgångsdagen/);

// Missing / invalid market data never becomes an artificial +edge.
assert.equal(evaluate("rank(0)[0].edge"), null);
evaluate('races[0].horses[1].streak="-5"; races[0].horses[2].streak="150";');
assert.equal(evaluate("rank(0).find(h=>h.j===1).edge"), null);
assert.equal(evaluate("rank(0).find(h=>h.j===2).edge"), null);
const snapshot = evaluate("makeForecastSnapshot()");
assert.equal(snapshot.verifiedResult, null, "Never invent actual results");
assert.equal(snapshot.historyCutoffDate, "2026-11-21");
assert.equal(snapshot.excludedAudit.length, 40);
assert.equal(snapshot.legs[2].horses.find(h => h.num === 12).selected, false);
assert.equal(snapshot.legs[2].horses.find(h => h.num === 12).history.length, 7, "Raw evidence is retained for audit");
assert.equal(snapshot.legs[2].horses.find(h => h.num === 12).historyExcludedByDate, 2);
assert.equal(snapshot.legs[0].horses[0].streakPct, null);

// One balanced ticket, exactly 300 kr when available: V85 600 x 0.50;
// V75 500 x 0.60. No extra system is generated.
evaluate("buildBalancedSystem()");
assert.equal(evaluate("races.reduce((p,r)=>p*r.horses.filter(h=>h.selected).length,1)"), 600);
assert.match(dom("system").innerHTML, /300 kr/);
assert.equal(evaluate("makeForecastSnapshot().costKr"), 300);
assert(evaluate("races.reduce((n,r)=>n+(r.horses.filter(h=>h.selected).length===1),0)") <= 2);

fixture(7, 6);
evaluate("buildBalancedSystem()");
assert.equal(evaluate("makeForecastSnapshot().rows"), 500);
assert.equal(evaluate("makeForecastSnapshot().costKr"), 300);

fixture(8, 2);
evaluate("buildBalancedSystem()");
assert.equal(evaluate("makeForecastSnapshot().rows"), 256);
assert.equal(evaluate("makeForecastSnapshot().costKr"), 128);
assert.match(dom("system").innerHTML, /Exakt budget gick inte att nå/);
console.log("Excluded-horse audit, unverified pre-race snapshot, market-data gaps and exact 300-kr V85/V75 systems OK");
