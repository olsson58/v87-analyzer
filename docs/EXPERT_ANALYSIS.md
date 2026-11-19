# Förslag: video- och expertanalys

Ingen TV4-, ATG Play- eller ATG Live-video har hämtats eller analyserats. Automatisk transkription får bara aktiveras för material med uttrycklig rätt till åtkomst och bearbetning; inget kringgående av inloggning, DRM eller betalväggar.

## Datamodell för en observation

```json
{
  "id": "observerat-unik-id",
  "source_url": "https://example.org/tillaten-kalla",
  "source_kind": "text_or_licensed_transcript",
  "rights_status": "approved",
  "permission_url": "https://example.org/licens",
  "expert": "Namn eller redaktion",
  "published_at": "2026-11-21T09:00:00+01:00",
  "captured_at": "2026-11-21T09:15:00+01:00",
  "race_start_at": "2026-11-21T16:00:00+01:00",
  "game_id": "V85_EXEMPEL",
  "race_no": 1,
  "horse_id": "EXEMPEL-HAST",
  "tip_type": "spik",
  "claim": "Egen kort saklig sammanfattning, inte en kopierad artikel",
  "equipment_note": null,
  "form_note": null,
  "model_rank_at_capture": 2,
  "model_score_at_capture": null,
  "model_version": "3.0",
  "outcome": null
}
```

Observera att exemplet **inte är ett verkligt tips**. Tillåtna `tip_type`: `spik`, `skrall`, `utrustning`, `form`. Allt registreras med källa, datum och versionsnummer. Skor/vagn och form lagras som observationer, inte automatiskt som sanning eller modellbonus.

## Rättighetsgrind

| Status | Tillåten hantering |
| --- | --- |
| `approved` | Enbart inom dokumenterat tillstånd; referera källa och villkor |
| `manual_reference_only` | Sparad länk och *egen* saklig notering, ingen maskinskrapning/heltext |
| `unknown` / `restricted` | Ingen automatisk hämtning eller transkription |

## Historisk utvärdering

1. Frys tipsen, starttider och modellens ranking **innan** loppet; inga efterhandsjusteringar.
2. Koppla utfall från separat rättighetsklarerad källa. Dela upp på spik, skräll och total; redovisa antal bedömda lopp och period.
3. Mät spikarnas vinstfrekvens och skrällarnas vinstfrekvens. För samtliga experttips kan även topp-3 jämföras om måttet definierats på förhand.
4. Jämför med modellens toppval i **samma lopp**. En modellbedömning räknas bara en gång per lopp, även om flera experter tipsat samma lopp.
5. Om sannolikheter sparas före lopp, mät Brier score och kalibrering. Enbart rankordning räcker inte för kalibreringspåståenden.
6. Spara både vinster och missar; redovisa osäkerhet och urvalsbias. Spelvärde är inte detsamma som historisk träffprocent.

Ingen insamling är påslagen. Implementera först när källornas återanvändningsrätt och ett lagligt resultatflöde är kontrollerade.
