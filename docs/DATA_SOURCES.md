# Datakällor – Trav Analyzer

Senast manuellt granskad: 2026-11-20. Detta är en rättighets- och tekniköversikt, inte ett påstående om att automatiska anslutningar är driftsatta.

## Spelformer efter november 2026

Enligt [ATG:s pressmeddelande den 17 september 2026](https://www.mynewsdesk.com/se/atg/pressreleases/v75-r-tillbaka-paa-loerdagarna-premiaer-28-november-3467622) återkommer V75 lördagen **28 november 2026**, med **60 öre/rad**. V85 pausas då tills vidare. [ATG:s kundservice om V85](https://atg-extern.kb.kundo.se/guide/information-angaende-v85) anger **50 öre/rad** för V85. Datumet för en omgång räcker inte som bevis på spelform: läs V75/V85 från verifierad omgångsinformation och kontrollera alltid radpris mot aktuell spelprodukt före inlämning. Den nuvarande appversionen beräknar V75 med 60 öre/rad, och kan därför överskatta kostnaden för äldre V75-omgångar.

| Område | Källa | Läget för återanvändning |
| --- | --- | --- |
| Startlistor, historiska starter SE, kuskar, tränare, skor, vagn | Svensk Travsport | Publikt läsbara uppgifter men uttryckligt upphovsrätts- och databasskydd. **Ingen automatisk kopiering/återpublicering utan tillstånd.** |
| Spelform, omgångar, streck och odds | ATG | Racinginfo är odokumenterat. Ingen verifierad rätt att samla in och återpublicera. Endast separat, uttryckligt manuellt experiment i appen; inte via Actions. |
| Häststarter Norge, Finland, Danmark, Frankrike | Rikstoto, Suomen Hippos/Heppa, Dansk Hestevæddeløb, LeTrot | Intressanta offentliga söksidor för manuell källkontroll; rätt till masshämtning ej fastställd. |
| Väderprognoser och observationer | SMHI öppna data | CC BY 4.0 SE; dokumenterade API:er, källhänvisning, uppge bearbetningar och undvik onödiga massanrop. Väder är **inte** liktydigt med banunderlag. |
| Väderprognoser för utländska och svenska banor | MET Norway Locationforecast | CC BY 4.0 med källangivelse. Kräver identifierande User-Agent och API-vänlig cachning; institutet avråder från direkta browseranrop. En kommande Actions-adapter kan använda källan med få uppslag per bana. |
| Banunderlag och sena strykningar | Arrangör/travbana | Kräver uppgiftens tidpunkt och källhänvisning; maskinläsbar återpubliceringsrätt behöver klarläggas. |
| TV4, TV4 Play och travprogram | TV4 | Upphovsrätt och särskilda villkor för Play. Ingen automatisk video-/textinsamling utan uttryckligt tillstånd. |
| ATG Live/ATG Play | ATG | ATG:s villkor beskriver livesändningar som privat bruk; annan användning kräver skriftligt godkännande. |
| Ytterligare gratis travsidor | Farsans Trav, Travat, v64startlista.se | Kan läsas manuellt eller användas som länkar, men villkoren ger inte generell rätt att bygga en återpublicerad databas. **Ej automatiserad Actions-källa.** |
| Kommersiellt nordiskt trav-API | Travmaskinen | Erbjuder JSON/API, men prissättningen för prognoser och databasen är inte kostnadsfri. **Inte aktuell inom våra kostnadsfria datakällor.** |

### Rättighetskontroll 20 november 2026

- [Svensk Travsports egen sida](https://www.travsport.se/svensk-travsport) anger uttryckligt copyright/databasskydd och förbud mot kopiering av publicerad hästsportinformation. En publikt läsbar startlista är därför **inte** automatiskt en godkänd källa för vår Actions-publicering.
- [Farsans Travs användarvillkor](https://farsanstrav.se/anvandarvillkor/) tillåter korta citat med källhänvisning, men inte systematisk uttagning utan avtal. [v64startlista.se:s villkor](https://v64startlista.se/anvandarvillkor/) medger personligt bruk, men annan kopiering/återpublicering kräver skriftligt tillstånd. [Travats villkor](https://www.travat.se/anvandarvillkor) begränsar uttryckligen robotar/skrapning utan tillstånd.
- [Travmaskinens API-sida](https://travmaskinen.se/developers) annonserar betalprodukter för kommande startlistor och historik; prisuppgifter som kontrollerades 20 november 2026 var 1 499 respektive 2 499 kr/månad. Ingen gratis produktlicens eller fri återpubliceringsrätt har verifierats.
- Utomlands (Norge, Finland, Danmark och Frankrike) har vi ännu inte funnit en uttrycklig öppen återpubliceringslicens för kompletta travstartlistor. **Status: inte verifierad**, vilket inte är samma sak som att sådan licens aldrig kan finnas.

### Frågor att få skriftligt svar på innan automatisering

1. Finns ett dokumenterat API eller en officiell fil med rätt för automatiserad hämtning av omgång, hästar, kuskar, tränare, utrustning och tidigare starter?
2. Får dessa data lagras i GitHub Actions och återpubliceras som JSON på en **offentligt åtkomlig** GitHub Pages-webbplats, även om appen är gratis?
3. Gäller tillståndet också ATG:s speldata (streck/odds) och eventuella internationella resultatrader, eller krävs flera separata rättighetshavare?
4. Vilka attribut, länkar, rate limits, cachetider och skyldigheter att uppdatera strykningar gäller? Finns en kostnadsfri kvot?
5. Hur ska tillståndet dokumenteras och får `source.permission_url` i vårt öppna projekt länka till avtalet eller en offentlig licenstext?

Fram tills svar finns: behåll GitHub Pages-kalendern tom, använd uttryckligen importerad CSV/JSON där användaren har rätt att använda uppgifterna, och länka till primärkällor för manuell kontroll. Inga inloggningar, betalväggar, robotskydd eller videor kringgås.

## Kontrollerade primärkällor

- [Svensk Travsports webbplats: upphovsrätt/databasskydd](https://www.travsport.se/svensk-travsport)
- [SMHI:s villkor för öppna data](https://www.smhi.se/data/om-smhis-data/villkor-for-anvandning)
- [MET Norway API – officiella användningsvillkor](https://docs.api.met.no/doc/TermsOfService.html)
- [MET Norway FAQ om separat godkännande av API-villkor](https://api.met.no/doc/FAQ)
- [TV4:s allmänna webbplatsvillkor](https://www.tv4.se/artikel/5742a60ffca38f120d00046b/allmanna-anvandarvillkor-for-tv4-s-tjanster)
- [ATG:s allmänna kontovillkor, avsnitt 4.2 livesändningar](https://api-backend.atg.se/services/cms/doc/d91bf644d7d955571f0bb8ca5fdf90a6f53afa3aa18f444eb8dd1fa03103173d/ATG%20Allma%CC%88nna%20Villkor%2023jan2023_version19.pdf)

## För en kommande automatiserad kalenderkälla

1. Spara skriftligt tillstånd eller tydlig återpubliceringslicens som URL i `source.permission_url`; kontrollera även rate limits och attribution.
2. För in verifierad omgångsdata i `data/calendar-source.json`; `source.rights_status` sätts till `approved` **endast efter mänsklig rättighetskontroll**.
3. Kör `python -m unittest discover -s tests -v` och `python scripts/build_site.py --output site`.
4. Valideringsfel ska stoppa hela Pages-publiceringen. `generated_at` är byggtid och är **aldrig** bevis för att sportdatan är ny. Sportuppgifternas datum är `verified_at`.
5. Browsern visar bara verifierade poster från senaste 72 timmarna; äldre uppgifter blir inte automatiskt "nya" av att en Actions-körning uppdateras.

Denna första version **hämtar inte** tävlingsuppgifter externt från GitHub Actions: det vore för tidigt utan rättighetsklarerad källa.
