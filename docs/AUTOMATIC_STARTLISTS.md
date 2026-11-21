# Automatisk startlistehämtning – rättighetsstyrd driftsplan

Granskad 2026-11-21. **Ingen skarp automatisk startlistehämtning är aktiverad.**

## Verifierat API-spår

Svensk Travsport har GitHub-kontot [Troperty](https://github.com/Troperty) med
[exempel för Race Data API](https://github.com/Troperty/racedata-node-samples)
och en [simulator](https://hub.docker.com/r/troperty/customerapi-mb2-simulator).
Simulatorn dokumenterar autentisering med `key`/`secret` till en bearer-token,
`GET /customerapi/events` och händelsetyper som `RacingCardRaceTrot`,
`ShoeInfoChanged`, `SulkyInfoChanged`, `ScratchingTrot` och `TrackConditionTrot`.
Detta är starka tekniska indikationer på att officiell maskinleverans finns;
**simulatorns demonstrerade nycklar och token ger inte åtkomst till produktionsdata**.

Svensk Travsport beskriver uttryckligen [sportdatakunder](https://www.travsport.se/svensk-travsport/om-webbplatsen/integritetspolicy),
och att sportdata säljs till kunder. Inget kostnadsfritt privat API-konto, ingen
API-nyckel och ingen återpubliceringslicens har verifierats för Trav Analyzer.
Att en startlista kan läsas eller Excel-exporteras manuellt är inte samma sak
som tillåtelse att automatisera hämtning eller publicera filen.

## Begär detta först

Kontakta [Svensk Travsport](https://www.travsport.se/svensk-travsport/organisation/kontakta-oss)
(`kundtjanst@travsport.se`) och be att få frågan vidarebefordrad till ansvarig
för **Sportdata / Race Data API**. Fråga om:

1. En kostnadsfri eller lågkostnadslicens för **privat, inloggningsskyddad**
   analys av V75/V85-startlistor (inkl. kusk, tränare, utrustning, strykningar,
   historiska starter, banunderlag), utan egen försäljning eller öppna datanedladdningar.
2. Dokumentation, produktionsadress, autentiseringsmetod, kundkonto och testdata.
3. Uttryckligt medgivande till automatisk hämtning, bearbetning, mellanlagring,
   cachning och eventuell visning via Cloudflare Access; villkor, avgift, tider,
   attribution, personuppgifter och gränser för uppdateringsfrekvens.
4. Hur man säkert hittar **V75/V85-avdelning ↔ vanligt loppnummer**; själva
   Race Data API-exemplen visar inte denna spelproduktsmappning. För streck och
   odds kan separat avtal med ATG behövas.

### Förslag till förfrågan (skicka först efter användarens granskning)

> Ämne: Förfrågan om privat användning av Race Data API / Sportdata
>
> Hej! Jag utvecklar Trav Analyzer, ett privat och åtkomstskyddat hjälpmedel
> för egen analys av V75/V85. Jag ser att Svensk Travsport/Troperty har
> publicerat exempelkod och simulator för Race Data API. Finns möjlighet till
> kostnadsfri, personlig eller lågkostnadslicens för automatiserad hämtning av
> startlistor, strykningar, skor/vagn, historiska starter och banförhållanden?
> Vi önskar varken sprida rådata offentligt eller sälja vidare tjänsten.
> Vi kan begränsa anrop och lagring enligt era villkor samt ange källan.
> Vem kan lämna API-dokumentation och skriftligt besked om tillåten användning?
> Tack på förhand!

## Teknik när tillstånd och dokumentation finns

1. Lägg produktionsuppgifter som **GitHub Actions secrets** (t.ex. kundnyckel
   och hemlighet), aldrig i JavaScript, i ett offentligt repo eller i Actions-loggar.
   Github Actions har ingen generell åtkomst till användarens ATG-appsession.
2. En begränsad Actions-körning hämtar tillåtna Race Data API-händelser enligt
   officiella scheman/rate limits, sparar en checkpoint för händelseströmmen,
   och kan ta emot uppdateringar om strykning, utrustning och banförhållanden.
   Välj lagring/checkpoint utifrån licensen; använd inte publika Actions-
   artefakter eller publik GitHub-branch för licensskyddade data.
3. Koppla startlistans **vanliga loppnummer** till avdelningar genom en
   *separat verifierad* V75/V85-omgångsidentifiering. Validera 7/8 lopp,
   unika hästnummer, tävlingsdatum, källtidsstämpel och strykningar. Avbryt
   helt vid ofullständig eller motsägelsefull data; återanvänd aldrig gammal
   lista under ny datumstämpel.
4. Publicera enbart det som avtalet tillåter via ett autentiserat API eller
   privat objektlager bakom **Cloudflare Access på såväl produktionsdomän som
   förhandsadresser**. Att GitHub-repot eller Cloudflare-förhandsvisningen är
   privat uppfyller inte i sig dataleverantörens rättighetsvillkor.
5. Webbläsaren hämtar endast från **samma skyddade ursprung**. Fel ska visa
   status och senast *verifierad* källdata, inte Safari-`Load failed` från
   tredjepartsanrop. Testa i Safari med verklig, tillåten testomgång innan merge.
6. Bygg först en **syntetisk adapter** till simulatorn och integrationstester
   för autentiseringsfel, dubbletter, försenade uppdateringar och nätbortfall.
   Slå inte på produktionsschemat förrän alla ovanstående punkter är uppfyllda.

## Nuvarande reservväg

Användaren kan via Svensk Travsports *Exportera allt* spara Excel för egen
lokal bearbetning. `scripts/convert_excel.py --sportappen --first-race N`
konverterar ett observerat, noga validerat format till privat JSON utan att
gissa historik eller streck. Testad på användarens Jägersro-export 2026-11-21,
men det är **manuellt** och ersätter inte ett godkänt API. Originalfil och JSON
ska inte läggas i GitHub-repot.

Se även [källornas rättighetsstatus](DATA_SOURCES.md).
