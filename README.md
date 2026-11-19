# Trav Analyzer (utvecklingsgren)

Mål: iPhone-vänlig analys för V75 och V85 med balanserat **ett system på högst 300 kr**.

## Safari-kalender: första säkra steg

- `index.html` läser `./data/calendar.json` från samma GitHub Pages-domän. Eventuella tävlingsuppgifter måste ha rättighetskontrollerats.
- Omgångslistan väljs från verifierad data, inte från en hårdkodad V75/V85-datumgräns.
- `scripts/build_site.py` validerar `data/calendar-source.json`, skapar kalender och startlistor i `site/`, samt kopierar befintlig `index.html`.
- `.github/workflows/pages-calendar.yml` kör test och bygget. På `main` kan det distribuera via GitHub Pages *när Pages har konfigurerats för GitHub Actions*. Pull requests kör bara tester och bygger artefakter utan produktion.
- Om inga rättighetsklarerade uppgifter finns visar kalendern tydligt att den är otillgänglig; **tomma källfiler är inte utgivna startlistor**.
- Valideringsfel avbryter arbetsflödet och ersätter inte senaste lyckade Pages-publicering.
- Direktkopplingen till ATG finns kvar som **separat manuellt experiment**, men är aldrig en automatisk serverkälla eller en garanti i Safari.

### Lokalt kontrollera

```bash
python -m unittest discover -s tests -v
python scripts/build_site.py --output site
python -m http.server 8000 --directory site
```

Öppna sedan `http://localhost:8000`. I standardläget är kalendern markerad som *unavailable* eftersom **ingen travdatakälla ännu fått klartecken för automatisk återpublicering**. För ett verkligt system krävs godkänd källa och manuell kontroll av `source.permission_url`, uppgiftens datum och baninformation.

**Obs:** Publicering ska inte aktiveras på `main` förrän Pages-inställningen kontrollerats, arbetsflödet provats och användaren godkänt produktionsändringen. Befintlig `main` är orörd av detta förslag.

Se [Datakällor](docs/DATA_SOURCES.md) och [Expertanalys](docs/EXPERT_ANALYSIS.md).
