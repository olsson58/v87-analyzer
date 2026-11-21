# Trav Analyzer (utvecklingsgren)

Mål: iPhone-vänlig analys för V75 och V85 med balanserat **ett system på högst 300 kr**.

## Nytt i testversion 3.1: kontrollera alla bortval

- **Skrällgranskning** visar varje häst som inte kom med i systemet. Låg streckprocent, hög preliminär modellandel, kort avstånd till förstahästen och saknad/ofullständig historik kan utlösa manuella kontrollflaggor. Inga varningsflaggor är bevisad spelvinst eller automatisk kupongändring.
- **Förhandsprognos i JSON** exporterar vilka hästar som valts bort och varför, tillsammans med aktuella inmatade streck, historik, beräkning, tidsstämpel och kostnad. Resultatfältet är tomt innan utfall verifierats.
- **Säkrare hästmatchning (3.2, testversion):** ett angivet häst-ID får inte falla tillbaka till en osäker namnträff; dubletter, kollisioner i normaliserade namn och ID-täckning redovisas. Upprepad importerad historik räknas inte som nya starter.
- **Balanserat radantal** räknas fram över hela kupongen. När hästantalet tillåter hittar appen 600 V85-rader × 0,50 kr respektive 500 V75-rader × 0,60 kr = **exakt 300 kr**. Annars visas faktisk lägre kostnad. Endast ett system skapas.
- Länkar till öppna delar av **Travradarn** och **V85Modellen** hjälper manuell kontroll utan betalning, kopiering från skyddade API:er eller otestade integrationer.

Se [kriterier, begränsningar och förhandsprotokoll](docs/RISK_REVIEW.md). Ingen verklig historisk kalibrering eller automatisk resultatkoppling har ännu genomförts.

## Safari-kalender: första säkra steg

- `index.html` läser `./data/calendar.json` från samma webbplats som användaren öppnar (GitHub Pages eller Cloudflare Pages). Eventuella tävlingsuppgifter måste ha rättighetskontrollerats.
- Omgångslistan väljs från verifierad data, inte från en hårdkodad V75/V85-datumgräns.
- `scripts/build_site.py` validerar `data/calendar-source.json`, skapar kalender och startlistor i `site/`, samt kopierar befintlig `index.html`.
- `.github/workflows/pages-calendar.yml` kör test och bygget. På `main` kan det distribuera via GitHub Pages *när Pages har konfigurerats för GitHub Actions*. Pull requests kör bara tester och bygger artefakter utan produktion.
- Om inga rättighetsklarerade uppgifter finns visar kalendern tydligt att den är otillgänglig; **tomma källfiler är inte utgivna startlistor**.
- Valideringsfel avbryter arbetsflödet och ersätter inte senaste lyckade Pages-publicering.
- Den tidigare ATG-direktknappen är borttagen: [ATG:s gällande villkor](https://assets.ctfassets.net/hkip2osr81id/2xz0S91MO59bAzEpvDSXya/8434b4b49bd3d55fa397aa9bdc0e6db0/ATG_Allma%CC%8C_nna_Villkor_fr.o.m_1_maj_2026.pdf) förbjuder automatiserad extraktion, och webbläsartestet gav "Load failed".
- Om användaren har en startlista som får användas lokalt kan en komplett V75/V85-JSON med sju/åtta lopp och valfria historikrader importeras i **ett steg**. Gamla omgången ersätts först efter bekräftelse; ingen uppladdning till ATG sker.
- En iPhone-guide i importpanelen visar den officiella manuella Excel-exporten från Svensk Travsports Sportapp och vägen via Filer/ChatGPT till befintlig JSON-import. **XLSX/PDF tolkas ännu inte direkt i webbläsaren**. Automatisk serverhämtning kräver separat åtkomst och rättighetsgodkännande.
- För lokala filer som användaren får behandla finns `python scripts/convert_excel.py MINFIL.xlsx --inspect`. Generiska tabeller med tydlig avdelning/startnummer/häst kan omvandlas med `--game V85 --date ÅÅÅÅ-MM-DD --track Bana --output privat.json`.
- Den manuellt exporterade **Sportappen-Excel-filen** från Jägersro 21 november 2026 har använts för att testa *formatet*, utan att lägga tävlingsdata i arkivet. Filen innehöll vanliga lopp 1–12; efter separat verifiering av omgångskopplingen kunde **V85-1–8 = vanliga lopp 5–12** omvandlas till en privat JSON med 100 hästar, kuskar, tränare, skor och vagnar. Kommandot nedan kräver uttrycklig loppmappning och avbryter vid ofullständiga lopp eller ändrat rubrikformat. Hästhistorik och streckprocent läggs inte till på gissning:

  ```bash
  python scripts/convert_excel.py 'min-sportappen-export.xlsx' \
    --sportappen --first-race 5 --game V85 \
    --date 2026-11-21 --track Jägersro --output privat.json
  ```

  **Obs:** `--first-race 5` avser just denna verifierade omgång, inte en permanent V85-regel. Lokal JSON är för privat import; den och källfilen ska **inte** checkas in eller återpubliceras.
- [Plan för godkänd automatisk datainhämtning](docs/AUTOMATIC_STARTLISTS.md) beskriver Svensk Travsports officiella Race Data API, vilka tillstånd som saknas och en driftsmodell för GitHub Actions utan Safari-anrop till tredjepart.
- Om Cloudflare Access råkar returnera en inloggningssida som HTML i stället för JSON visas ett tydligt felmeddelande.

### Lokalt kontrollera

```bash
python -m unittest discover -s tests -v
node dev/calendar_smoke.cjs
node dev/risk_review_smoke.cjs
python scripts/build_site.py --output site
python -m http.server 8000 --directory site
```

Öppna sedan `http://localhost:8000`. I standardläget är kalendern markerad som *unavailable* eftersom **ingen travdatakälla ännu fått klartecken för automatisk återpublicering**. För ett verkligt system krävs godkänd källa och manuell kontroll av `source.permission_url`, uppgiftens datum och baninformation.

**Obs:** Publicering ska inte aktiveras på `main` förrän Pages-inställningen kontrollerats, arbetsflödet provats och användaren godkänt produktionsändringen. Befintlig `main` är orörd av detta förslag.

Se [Datakällor](docs/DATA_SOURCES.md), [Skrällgranskning](docs/RISK_REVIEW.md), [Internationella metodreferenser](docs/INTERNATIONAL_METHODS.md) och [Expertanalys](docs/EXPERT_ANALYSIS.md).
