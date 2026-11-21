# Förhandsgranskning av bortvalda hästar (3.1, testgren)

Den 21 november 2026 gav användarens efteranalys av häst nummer 12 i V85-3 upphov till denna kontroll. Vi **har ännu inte rekonstruerat den faktiska förhandsrankningen eller orsaken till just det bortvalet**. Därför går det inte att tillskriva ett visst hästfaktum eller en viss regel ansvaret i efterhand. Funktionen är en *förebyggande* modellkontroll för kommande omgångar.

## Vad ändringen gör

1. Alla hästar som inte valts på **den enda balanserade kupongen** listas per avdelning och finns med i ett exporterat JSON-protokoll, även om de har låg streckprocent eller saknar historik.
2. Programmet visar relativ modellandel, aktuell *inmatad* streckprocent, skillnad i procentenheter, antal importerade starter och om historiken är ofullständig. Ogiltiga/saknade streck (tom sträng, mindre än 0, över 100) ger `null` i stället för skenbar spelvärdessignal.
3. **Granska särskilt** om en bortvald häst har minst 6 % modellandel och minst +4 procentenheters skillnad mot strecken, samtidigt som modellandelen minst är 1,5 gånger streckprocenten; alternativt om hästen ligger högst 0,75 betygssteg bakom loppets etta och har minst 12 % modellandel. Detta är en *heuristisk granskningsflagga*, inte en automatisk rekommendation att lägga till hästen.
4. **Dubbelkolla** andra bortval med minst 7 % modellandel, högst 0,75 betygsstegs avstånd från topprankad, eller minst +2 procentenheters positiv skillnad mot streck. Även bortval utan särskild flagga syns.
5. Varje bortval med färre än fem importerade starter, ofullständig historik eller saknad streckprocent får en tydlig datavarning. Kontrollera 5–10 starter, distans, startmetod, spår, motstånd, kusk, tränare, utrustning, strykningar och värmning manuellt där öppna data finns.
6. När omgångsdatum är angivet utesluts historikrader utan daterad start eller daterade **på/efter omgångsdagen** ur modellpoäng och landstatistik. Råposterna finns kvar i exportfilen för granskning, med antal uteslutna. Om datum saknas varnar systemet och vägrar exportera en daterad förhandsprognos.

**Modellandel är inte en kalibrerad vinstprognos.** Nuvarande poäng vägs av sju manuella kriterier samt en begränsad historikbonus. `exp(poäng/2)` normaliseras inom loppet. Att jämföra den med streckprocent kan belysa hypoteser om spelvärde, men detta är inte en statistiskt verifierad edge. Ingen skrällgräns har tränats eller validerats mot faktiska förhandsprognoser.

## En kupong, rätt radantal

Systembyggaren använder en begränsad sökning över antal val per avdelning i stället för att öka ett lopp i taget. Målet är högst den angivna budgeten och **exakt 300 kr om radantal och antalet tillgängliga hästar medger det**. Inom möjliga kombinationer prioriteras maximalt två spikar och en försiktig sammanvägd täckningspoäng. Det betyder inte att de valda spikarna är säkra.

| Spel | Radpris | Max rader vid 300 kr | Exempel på heltalspassage |
| --- | ---: | ---: | --- |
| V85 | 0,50 kr | 600 | 1 × 1 × 2 × 2 × 2 × 3 × 5 × 5 = 600 |
| V75 | 0,60 kr | 500 | 1 × 1 × 2 × 2 × 5 × 5 × 5 = 500 |

Om ett lopp har för få inlästa hästar för detta visar programmet den faktiska lägre kostnaden. Ett enda system skapas. Räknemodellen har kontrollerats med syntetiska testomgångar för både V75 och V85; verkligt spel kräver kontroll mot officiell radkostnad och aktuell spelform.

## Jämförelse med fria verktyg

- [Travradarn](https://travradarn.se/) visar öppen historik för häst, kusk, tränare och bana. Använd den som **manuell faktakontroll** och styrk eventuella upptäckter med en separat källa. Webbplatsens tekniska datakälla är inte ett generellt tillstånd att masskopiera dess API.
- [V85Modellen](https://v85modellen.se/) har öppna Ranking, Form Index, Live och Prestanda. Deras poäng behandlas som **separata jämförelseindikatorer**, aldrig som kalibrerade vinstsannolikheter. Deras medlemsdel Alpha används inte.
- [Svensk Travsport](https://www.travsport.se/) och officiella resultat är kontrollkällor där hämtning, behandling och återanvändning är tillåtna. Ingen automatiserad åtkomst till skyddad tjänst eller dold endpoint ingår.

Denna version importerar **inte** automatiskt siffror från Travradarn eller V85Modellen. Att öppna deras fria sidor innebär varken en integration eller ett löfte om att all deras data kan återanvändas.

## Granskningsbar historik och efteranalys

Knappen **Spara förhandsprognos (JSON)** exporterar på användarens enhet skapandetid i ISO-format, spelform, lopp, enhetspris, radantal, kostnad, vald/bortvald markering, modellandel, känd streckprocent, flaggor och den historik som verkligen importerats. `verifiedResult` är uttryckligen `null` vid export. Filen kallas *tidsstämplad men inte verifierad* (`forecastKind: unverified_timestamped_snapshot`); den är bara en verklig före-start-prognos om tidsstämpeln visar att den sparades före start.

- Spara filen **före första start**. Kontrollera att dateringen är rätt och ändra inte filen efteråt.
- Efter omgången: samla faktiska vinnare, återbetalning och eventuella strykningar från verifierbara officiella källor. Särhåll förhandsprognos och efterhandsutfall.
- Bara när tillräckligt många **verkligt frysta** prognoser och verifierade utfall finns kan träffprocent, Brier score, log loss, kalibrering och effekten av skrällflaggorna beräknas. Saknad historik får inte fyllas i retroaktivt som om den var känd före start.
- Exporten skapar **inte** i sig någon löpande databas eller automatisk resultatkoppling. Inga ekonomiska utfall har beräknats eller registrerats av denna ändring.

## Test och status

```bash
node dev/risk_review_smoke.cjs
node dev/calendar_smoke.cjs
python -m unittest discover -s tests -v
```

Testet använder bara syntetiska lopp: exkluderad häst nummer 12 med låga streck, saknat/ogiltigt marknadsvärde, exkludering av sen/odaterad historik, tidsstämplad export utan resultat, V85 600 × 0,50 kr = 300 kr, V75 500 × 0,60 kr = 300 kr och en omgång där exakt budget **inte** kan nås. Testet är inte någon backtest av riktigt travutfall.

Förändringen ligger på en **utvecklingsgren** och ska inte slås ihop med publik `main` innan den verifierats i en mobil webbläsare med rättighetsklarerade startlistor och användaren godkänt publicering.
