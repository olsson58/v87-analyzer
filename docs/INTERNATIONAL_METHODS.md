# Internationella kod- och metodreferenser – Trav Analyzer

Granskad 2026-11-22. Detta är en **metodinventering**, inte ett påstående om att koden har installerats, tränats, integrerats eller kopierats. Länkarna går till de identifierade originalprojekten. Vi har inte gjort en uttömmande världsomspännande granskning.

## Prioriterade öppna projekt

| Originalprojekt | Område | Kodlicens enligt granskad projektsida | Intressant för oss | Beslut |
| --- | --- | --- | --- | --- |
| [mervees/Horse-Racing-Analytics](https://github.com/mervees/Horse-Racing-Analytics) | Generell hästkapplöpning | MIT uppges i README | Tydlig dataläckagegrind före start, modell-oberoende marknadsjämförelse, oddsnormalisering, riskflaggor, tidsordnad backtest | **Hög prioritet som metodreferens**. Projektet använder även syntetiska exempel; ingen uppgiven modellavkastning överförs till V85. |
| [jerrydaphantom/hkjc-ml-research](https://github.com/jerrydaphantom/hkjc-ml-research) | Hongkong | MIT | En rad per häst och lopp; tidigare häst/kusk/tränarprestationer; före-start-funktioner; tidsbaserad validering och Brier/log loss; separat marknadsfri/marknadsmedveten modell | **Hög prioritet** för vårt framtida historik- och utvärderingsschema. HKJC-data ingår inte med fri vidareanvändningsrätt. |
| [cyrustt/jockey-predictor](https://github.com/cyrustt/jockey-predictor) | Hongkong | MIT | Distansspecifik modell, osäkerhetsfördelning för sluttider, Monte Carlo-loppsimulering, syntetiska regressionsprov | **Senare**. Kräver betydligt fler jämförbara travtider och startvillkor än vi har verifierat. Skrapningsdelar återanvänds inte. |
| [bamboostack/au-racing-open-data](https://github.com/bamboostack/au-racing-open-data) | Australisk trav-/kapplöpningsdata | Ingen kod-/datalicens fastställd vid denna granskning | Dokumenterade kurvradier, 800/400 m-positioner, spårbredd och positionsförändringar som idéer till löpförloppsanalys | **Metodinspiration**. Inga australiska data ska användas som svenska loppdata; kontrollera rättigheter innan eventuell import. |
| [mathis-dumont/horse-racing-prediction](https://github.com/mathis-dumont/horse-racing-prediction) | Franskt trav/PMU | Ingen uttrycklig licens fastställd | Lager för rättighetskontrollerad import, lagring, modell och användargränssnitt | **Arkitekturidé**, ingen kod kopieras utan tillstånd/licens. |
| [EqulipseSE/TRAV](https://github.com/EqulipseSE/TRAV) | Svenskt trav | Ingen uttrycklig licens fastställd | Favoritens streckprocent jämfört med faktisk historisk vinstfrekvens, streckintervall, rådata/proveniens | **Metodreferens endast**. Projektets odokumenterade ATG Racinginfo-API får inte aktiveras i vår kod utan klarlagd rätt till automatiserad åtkomst. |
| [kjkalliojarvi/sjoden](https://github.com/kjkalliojarvi/sjoden) | Svenskt trav | Ingen uttrycklig licens fastställd | Rå-JSON-arkiv, DuckDB-normalisering, stabila ID:n, käll-/schemakontroll; påminner om att förhandssnapshots inte kan återskapas i efterhand | **Datamodell-idé endast**; automatiska Racinginfo-anrop spärrade. |
| [tsukasaI/keiba-ai](https://github.com/tsukasaI/keiba-ai) | Japansk galopp | Ingen uttrycklig licens fastställd | Uppdelade modeller/tester för odds, kalibrering, senaste 3/5 starter och kusk/tränare | **Idé endast**; varken galoppvariabler eller påstådd ROI överförs direkt till nordiskt trav. |

*Licensstatus avser **kod** enligt det som kunde verifieras på projektsidan. Det innebär inte tillstånd att kopiera träningsdata, API-svar, användaridentiteter eller webbplatsinnehåll. Om kod faktiskt kopieras från MIT-licensierat projekt ska copyright- och licenstext behållas i en separat `THIRD_PARTY_NOTICES` och kodens ursprung dokumenteras.*

## Prioriterad utvecklingsplan för vår testgren

1. **Datakvalitet först.** Granska import per stabilt häst-ID och lopp-ID. Mät matchningsgrad, dubletter, antal starter före dagens lopp, okända datum och utländska starter; aldrig gissa ihop två hästar med liknande namn. Använd bara filer vi får behandla.
2. **Rätt tidsordning.** Behåll spärren mot historik från tävlingsdagen och senare, och stärk den med enhetstester för verkliga datumformat och tidszoner. I varje förhandsprognos sparas då känd information, inte efterhandsuppgifter.
3. **Enkel jämförbar modell.** Börja med tydliga statistiska baslinjer innan mer komplex AI. Jämför våra val mot en separat marknadsbaslinje och mot manuellt införda gratisrankingar. Uttryck inte externa rankpoäng som vinstchanser.
4. **Mätning först när den är möjlig.** Spara prognos före spelstopp och verifierad resultatrad efter loppet. Utvärdera träffar bland topp-1/topp-3, bortvalsflaggornas precision, Brier/log loss och kalibreringsdiagram endast för verkligt frysta prognoser med verifierade resultat. Träna och testa i kronologisk ordning.
5. **Loppbild och störningar.** När tillåtna och jämförbara data finns: beräkna vila sedan förra starten, prestation nära aktuell distans, galopprisk, startmetod, spår, kusk/häst-kombination, tränartrend samt positionsförluster och utrustningsändringar. Redovisa datatäckningen bredvid varje slutsats.
6. **Osäkerhetssimulering senare.** Monte Carlo eller inlärd ranker kan testas när antalet historiska lopp är tillräckligt stort och tidsvalidering genomförts; fram till dess behåll enkla, kontrollerbara poängregler.

## Omedelbar rättighets- och teknikkontroll

- Inga nya bibliotek eller system har installerats genom denna inventering.
- Inga tredjepartsfiler, skyddad data, betting-API:er eller skrapningsskript har kopierats till Trav Analyzer.
- Den enda befintliga kupongen är fortfarande balanserad, standardbudget 300 kr enligt nuvarande kod. En eventuell separat överenskommen engångsbudget är inte en permanent ändring av denna standard.
- Pågående Safari-/startlistearbete kräver fortsatt verifierad källa eller användarens rättighetsklarerade export; öppen GitHub-kod är inte en genväg förbi leverantörsvillkor.

**Status:** forsknings- och arkitekturreferens. Ingen verifierad förbättring i förutsägelseförmåga kan ännu påstås.
