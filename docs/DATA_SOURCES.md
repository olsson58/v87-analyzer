# Datakällor – Trav Analyzer

Senast manuellt granskad: 2026-11-19. Detta är en rättighets- och tekniköversikt, inte ett påstående om att automatiska anslutningar är driftsatta.

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

## Kontrollerade primärkällor

- [Svensk Travsports webbplats: upphovsrätt/databasskydd](https://www.travsport.se/svensk-travsport)
- [SMHI:s villkor för öppna data](https://www.smhi.se/data/om-smhis-data/villkor-for-anvandning)
- [MET Norway API – officiella användningsvillkor](https://docs.api.met.no/doc/TermsOfService.html)
- [TV4:s allmänna webbplatsvillkor](https://www.tv4.se/artikel/5742a60ffca38f120d00046b/allmanna-anvandarvillkor-for-tv4-s-tjanster)
- [ATG:s allmänna kontovillkor, avsnitt 4.2 livesändningar](https://api-backend.atg.se/services/cms/doc/d91bf644d7d955571f0bb8ca5fdf90a6f53afa3aa18f444eb8dd1fa03103173d/ATG%20Allma%CC%88nna%20Villkor%2023jan2023_version19.pdf)

## För en kommande automatiserad kalenderkälla

1. Spara skriftligt tillstånd eller tydlig återpubliceringslicens som URL i `source.permission_url`; kontrollera även rate limits och attribution.
2. För in verifierad omgångsdata i `data/calendar-source.json`; `source.rights_status` sätts till `approved` **endast efter mänsklig rättighetskontroll**.
3. Kör `python -m unittest discover -s tests -v` och `python scripts/build_site.py --output site`.
4. Valideringsfel ska stoppa hela Pages-publiceringen. `generated_at` är byggtid och är **aldrig** bevis för att sportdatan är ny. Sportuppgifternas datum är `verified_at`.
5. Browsern visar bara verifierade poster från senaste 72 timmarna; äldre uppgifter blir inte automatiskt "nya" av att en Actions-körning uppdateras.

Denna första version **hämtar inte** tävlingsuppgifter externt från GitHub Actions: det vore för tidigt utan rättighetsklarerad källa.
