// Integration-like check without a browser. No external network calls.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("index.html", "utf8");
let code = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert(code, "Inline script missing");
// Avoid app startup (requires real DOM and localStorage). Exercise real calendar functions.
code = code.slice(0, code.lastIndexOf("configureGame(preferredGameType("));
const nodes = new Map();
const dom = id => {
  if (!nodes.has(id)) nodes.set(id, {
    value: "",
    textContent: "",
    innerHTML: "",
    querySelectorAll: () => [],
    addEventListener: () => {},
  });
  return nodes.get(id);
};
let payload = {schema_version: 1, status: "unavailable", games: []};
const outbound = [];
const context = vm.createContext({
  document: {getElementById: dom},
  window: {},
  fetch: async url => {
    outbound.push(url);
    return {ok: true, json: async () => payload};
  },
  AbortController, setTimeout, clearTimeout, Date, String, Number, console,
});
vm.runInContext(code, context);
dom("atgdate").value = "2026-11-21";
dom("gameType").value = "auto";

async function test() {
  let selected = await vm.runInContext("fetchAtgCalendar()", context);
  assert.equal(selected, null);
  assert.match(dom("atgstatus").textContent, /Ingen färsk .*V75\/V85-omgång är verifierad/);
  payload = {
    schema_version: 1,
    status: "verified",
    games: [
      {id: "V85_TEST1", date: "2026-11-21", type: "V85",
       source_url: "https://example.org/source", permission_url: "https://example.org/lic",
       verified_at: new Date().toISOString()},
    ],
  };
  selected = await vm.runInContext("fetchAtgCalendar()", context);
  assert.equal(selected, "V85_TEST1");
  assert.match(dom("atgstatus").textContent, /Verifierad publicerad kalender/);
  assert(outbound.every(url => url.startsWith("./data/calendar.json")));
  console.log("Calendar functions OK (no remote ATG call)");
}
test().catch(error => {console.error(error); process.exitCode = 1;});
