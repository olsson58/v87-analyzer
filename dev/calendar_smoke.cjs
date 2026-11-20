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
    eventHandlers: {},
    addEventListener(event, callback) {this.eventHandlers[event] = callback;},
  });
  return nodes.get(id);
};
let payload = {schema_version: 1, status: "unavailable", games: []};
let gamePayload = null;
let nextFetchError = null;
let mockContentType = "application/json";
const outbound = [];
const context = vm.createContext({
  document: {getElementById: dom},
  window: {},
  fetch: async url => {
    outbound.push(url);
    if (nextFetchError) {
      const error = nextFetchError;
      nextFetchError = null;
      throw error;
    }
    return {ok: true, headers: {get: () => mockContentType},
      json: async () => url.includes("/games/") ? gamePayload : payload};
  },
  AbortController, setTimeout, clearTimeout, Date, String, Number, console,
  confirm: () => true,
});
vm.runInContext(code, context);
dom("atgdate").value = "2026-11-21";
dom("gameType").value = "auto";

async function test() {
  // Reproduce the Safari error from the user's iPhone screenshot. It must be
  // handled without claiming that any real ATG calendar was fetched.
  nextFetchError = new TypeError("Load failed");
  let selected = await vm.runInContext("fetchAtgCalendar()", context);
  assert.equal(selected, null);
  assert.match(dom("atgstatus").textContent, /Load failed/);
  assert.match(dom("atgstatus").textContent, /CSV\/JSON/);

  // A stale Access login page can return HTTP 200 with HTML. It is not calendar data.
  mockContentType = "text/html";
  selected = await vm.runInContext("fetchAtgCalendar()", context);
  assert.equal(selected, null);
  assert.match(dom("atgstatus").textContent, /returnerade inte JSON/);
  mockContentType = "application/json";

  selected = await vm.runInContext("fetchAtgCalendar()", context);
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
  // Synthetic race data: no copyrighted or live start lists are included.
  // Verify that eight legs are loaded through the same-origin endpoint.
  const racesFor = legs => Array.from({length: legs}, (_, i) => ({
    id: `TEST_RACE_${i + 1}`,
    starts: [
      {startNumber: 1, horse: {name: `Provgång ${i + 1} A`}},
      {startNumber: 2, horse: {name: `Provgång ${i + 1} B`}},
    ],
  }));
  vm.runInContext("render=()=>{};renderHistoryOverview=()=>{};save=()=>{};fetchAllHorseHistory=async()=>{};buildBalancedSystem=()=>{};", context);
  gamePayload = {races: racesFor(8)};
  dom("atggameid").value = selected;
  assert.equal(await vm.runInContext("fetchAtgGame()", context), true);
  assert.equal(vm.runInContext("races.length", context), 8);
  assert.equal(vm.runInContext("races[0].horses.length", context), 2);
  assert.equal(dom("unit").value, "0.50");
  dom("budget").value = "750";
  assert.equal(vm.runInContext("enforceBudget()", context), 300);

  // V75: seven legs and 60-öre unit, including the upcoming 2026-11-28 rules.
  payload.games = [{...payload.games[0], id: "V75_TEST1", type: "V75"}];
  gamePayload = {races: racesFor(7)};
  selected = await vm.runInContext("fetchAtgCalendar()", context);
  assert.equal(selected, "V75_TEST1");
  dom("atggameid").value = selected;
  assert.equal(await vm.runInContext("fetchAtgGame()", context), true);
  assert.equal(vm.runInContext("races.length", context), 7);
  assert.equal(dom("unit").value, "0.60");

  // Malformed game data must not overwrite the previously loaded valid round.
  gamePayload = {races: racesFor(8)};
  assert.equal(await vm.runInContext("fetchAtgGame()", context), false);
  assert.equal(vm.runInContext("races.length", context), 7);
  assert.match(dom("atgstatus").textContent, /Tidigare sparad omgång finns kvar/);
  const provenance = vm.runInContext(`
    (() => {
      const horse = {history: []};
      mergeHorseHistory(horse, [{
        date: "2026-11-15", country: "SE", place: 2, source: "Min tillåtna källa"
      }], false, "Verifierad publicerad startlista");
      return horse.history[0].source;
    })()
  `, context);
  assert.equal(provenance, "Min tillåtna källa");
  assert(outbound.every(url => url.startsWith("./data/")), "No direct ATG request may be made");
  dom("jsonpaste").value = JSON.stringify([{avd:1,number:1,name:"Provrunner",driver:"Provgubbe"}]);
  const beforeImport = vm.runInContext("races[0].horses.length", context);
  vm.runInContext("importJSON(); importJSON()", context);
  assert.equal(vm.runInContext("races[0].horses.length", context), beforeImport + 1, "Repeated JSON should not duplicate horses");
  dom("csvfile").eventHandlers.change && await dom("csvfile").eventHandlers.change({
    target: {files: [{text: async () => "avd;nr;häst;kusk;streck;odds;skor;vagn\n1;2;Provrunner 2;Kusk;12;8,5;barfota;vanlig"}]},
  });
  assert.equal(vm.runInContext("races[0].horses.length", context), beforeImport + 2);
  assert.equal(vm.runInContext("races[0].horses[races[0].horses.length - 1].odds", context), "8.5");

  // One own JSON file can hold a full eight-leg start list and past starts.
  const ownRaces = racesFor(8);
  ownRaces[0].starts[0].history = [{
    date: "2025-11-09", country: "NO", track: "Bjerke", place: 1,
    distance: 2140, source: "Egen källhänvisad fil",
  }];
  dom("jsonpaste").value = JSON.stringify({date: "2026-11-21", track: "Solvalla", races: ownRaces});
  vm.runInContext("importJSON()", context);
  assert.equal(vm.runInContext("races.length", context), 8);
  assert.equal(vm.runInContext("races[0].horses[0].history.length", context), 1);
  assert.equal(vm.runInContext("races[0].horses[0].history[0].country", context), "NO");
  assert.equal(vm.runInContext("races[0].horses[0].history[0].source", context), "Egen källhänvisad fil");
  assert.match(dom("importstatus").textContent, /16 hästar, 8 avdelningar, 1 med historik/);
  dom("jsonpaste").value = JSON.stringify({races: ownRaces.slice(0, 6)});
  vm.runInContext("importJSON()", context);
  assert.match(dom("importstatus").textContent, /exakt 7 .*eller 8/);
  assert.equal(vm.runInContext("races.length", context), 8, "Malformed import must not replace a working round");
  assert.equal(vm.runInContext("typeof fetchAtgCalendarDirect", context), "undefined");
  assert(!html.includes("Prova ATG direkt"), "Undocumented ATG action must be removed from UI");
  assert(outbound.every(url => url.startsWith("./data/")), "No direct ATG request may be made");
  console.log("Safari error, Access login HTML, same-origin V75/V85, 300-kr cap and private JSON+history import OK");
}
test().catch(error => {console.error(error); process.exitCode = 1;});
