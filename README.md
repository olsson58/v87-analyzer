# Trav Analyzer (utvecklingsgren)

Mål: iPhone-vänlig analys för V75 och V85 med balanserat **ett system på högst 300 kr**.

## Safari-kalender: första säkra steg

- `index.html` läser `./data/calendar.json` från samma webbplats som användaren öppnar (GitHub Pages eller Cloudflare Pages). Eventuella tävlingsuppgifter måste ha rättighetskontrollerats.
- Omgångslistan väljs från verifierad data, inte från en hårdkodad V75/V85-datumgräns.
- `scripts/build_site.py` validerar `data/calendar-source.json`, skapar kalender och startlistor i `site/`, samt kopierar befintlig `index.html`.
- `.github/workflows/pages-calendar.yml` kör test och bygget. På `main` kan det distribuera via GitHub Pages *när Pages har konfigurerats för GitHub Actions*. Pull requests kör bara tester och bygger artefakter utan produktion.
- Om inga rättighetsklarerade uppgifter finns visar kalendern tydligt att den är otillgänglig; **tomma källfiler är inte utgivna startlistor**.
- Valideringsfel avbryter arbetsflödet och ersätter inte senaste lyckade Pages-publicering.
- Den tidigare ATG-direktknappen är borttagen: [ATG:s gällande villkor](https://assets.ctfassets.net/hkip2osr81id/2xz0S91MO59bAzEpvDSXya/8434b4b49bd3d55fa397aa9bdc0e6db0/ATG_Allma%CC%8C_nna_Villkor_fr.o.m_1_maj_2026.pdf) förbjuder automatiserad extraktion, och webbläsartestet gav "Load failed".
- Om användaren har en startlista som får användas lokalt kan en komplett V75/V85-JSON med sju/åtta lopp och valfria historikrader importeras i **ett steg**. Gamla omgången ersätts först efter bekräftelse; ingen uppladdning till ATG sker.
- Om Cloudflare Access råkar returnera en inloggningssida som HTML i stället för JSON visas ett tydligt felmeddelande.

### Lokalt kontrollera

```bash
python -m unittest discover -s tests -v
node dev/calendar_smoke.cjs
python scripts/build_site.py --output site
python -m http.server 8000 --directory site
```

Öppna sedan `http://localhost:8000`. I standardläget är kalendern markerad som *unavailable* eftersom **ingen travdatakälla ännu fått klartecken för automatisk återpublicering**. För ett verkligt system krävs godkänd källa och manuell kontroll av `source.permission_url`, uppgiftens datum och baninformation.

**Obs:** Publicering ska inte aktiveras på `main` förrän Pages-inställningen kontrollerats, arbetsflödet provats och användaren godkänt produktionsändringen. Befintlig `main` är orörd av detta förslag.

Se [Datakällor](docs/DATA_SOURCES.md) och [Expertanalys](docs/EXPERT_ANALYSIS.md).
