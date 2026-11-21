# Trav Analyzer – plan för privat drift

**Status: förberedd i testgren, inte driftsatt.** Ingen privat inloggning har skapats, ingen datakälla har köpts och inget befintligt GitHub Pages-bygge har flyttats. Den publika sidan får inte stängas innan den privata lösningen är verifierad och ägaren godkänt bytet.

## Rekommenderad lösning

1. Privat GitHub-arkiv för källkod, tester och GitHub Actions. Hemliga API-nycklar ska ligga i Actions Secrets eller värdtjänstens separata hemlighetshantering, **aldrig i kod, HTML, JSON eller webbläsaren**.
2. Cloudflare Pages bygger statiska filer ur en särskild testgren. Föreslaget byggkommando: `python scripts/build_site.py --output site`; byggkatalog: `site`; Python-version: `3.12`.
3. Cloudflare Access kräver inloggning för **alla** vägar till appen: produktion `projekt.pages.dev`, förhandsvisning `*.projekt.pages.dev` och eventuell egen domän. Policy: tillåt endast användarens **bekräftade** e-postadress. E-postkod (one-time PIN) är ett tillgängligt alternativ.
4. Datahämtning ska ske i Actions eller bakom en autentiserad serverfunktion, aldrig via ett tredjeparts-API med hemlig nyckel direkt i Safari. All utdata ska ha källhänvisning, tidsstämpel och kontrollerad användningsrätt.

`deploy/cloudflare/_headers` följer med i det byggda `site/` och ger `Cache-Control: private, no-store` och några extra webbsäkerhetsrubriker på **statiska** Cloudflare Pages-svar. **Det är inte ett lösenordsskydd.** Skyddet måste komma från Cloudflare Access innan någon privat eller licensierad information läggs där. Serverfunktioner måste sätta egna headers.

## Säker ordning för flytt

1. Bekräfta vilket konto och vilken e-post som ska ha ensam åtkomst. Inga inloggningsuppgifter behöver delas i ChatGPT eller GitHub.
2. Skapa ett separat Cloudflare Pages-testprojekt med endast våra nuvarande **tomma** demonstrations-/kalenderdata. En ny Pages-adress kan vara offentlig innan Access aktiveras; inga privata data får laddas upp i detta steg.
3. Aktivera Access för både `projekt.pages.dev` och varje förhandsvisningsadress. Cloudflare anger att det vanliga alternativet *Enable access policy* först endast skyddar preview – komplettera därför separat skydd av produktionsdomänen enligt deras anvisningar.
4. Testa från en privat/utloggad Safari-flik: `index.html`, `/data/calendar.json`, varje `/data/games/*.json` samt samtliga alternativa produktions-, preview- och egna domännamn måste kräva inloggning. Testa också att fel e-post **inte** får åtkomst. Kontrollera sedan att rätt e-post kommer in och att samma-origin `fetch()` fungerar i Safari efter inloggning.
5. Testa GitHub Actions, byggning, budgettak på 300 kr och V75/V85 utan några verkliga licensierade uppgifter. Lägg inte in en köpt källa förrän avtalet uttryckligen tillåter automatiserad hämtning, lagring hos GitHub/Cloudflare och visning bakom privat inloggning.
6. Först efter godkänt iPhone-test: ändra GitHub-arkivets synlighet till **private**, kontrollera att Cloudflares GitHub-koppling fortfarande fungerar och avpublicera den gamla GitHub Pages-sidan. Github Free kan avpublicera Pages automatiskt när ett arkiv görs privat. Ägaren godkänner den här synlighets- och driftsändringen i samband med sluttestet.
7. Testa utloggad åtkomst på nytt efter flytten och kontrollera inga gamla offentliga länkar längre visar analysdata. Notera att redan publicerade eller cachade kopior historiskt inte kan återkallas genom att göra ett repo privat.

## Kontroller för data och säkerhet

- Ingen hemlighet får läsas från `index.html`, statisk JSON, JavaScript eller repots historik.
- `data/calendar-source.json` och eventuella lokala `.env`-filer ska inte publiceras i `site/` (verifieras av test).
- Ingen `Access-Control-Allow-Origin: *` ska aktiveras för privat sportdata.
- Cloudflare Pages `_headers` skyddar inte Pages Functions. Eventuella funktioner måste validera autentisering, behörighet, cache och svar själva.
- Saknad källa ska visas som **saknad**, aldrig som verklig hästhistorik eller en verifierad spikomgång.
- Enbart användaren får ha en Allow-policy; test med fel e-post måste misslyckas.

## Kontrollerade leverantörslänkar (20 november 2026)

- [GitHub: när ett offentligt repo görs privat](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [Cloudflare Pages: Git-koppling stöder privata repo](https://developers.cloudflare.com/pages/get-started/git-integration/)
- [Cloudflare Pages: produktions- och preview-skydd](https://developers.cloudflare.com/pages/platform/known-issues/)
- [Cloudflare Pages: egna statiska svarsrubriker](https://developers.cloudflare.com/pages/configuration/headers/)
- [Cloudflare Access: engångskod via e-post](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/)

**Kvarstående blockerare:** Cloudflare-konto och en verifierad e-post för ensam åtkomst behöver väljas/konfigureras av ägaren. Ingen Cloudflare-anslutning är aktiv från vårt verktyg. Verkliga travstartlistor behöver fortfarande rättighetsklareras separat.
