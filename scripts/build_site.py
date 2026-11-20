#!/usr/bin/env python3
"""Build a same-origin, rights-reviewed calendar for GitHub Pages.

Only repository-maintained source entries are accepted. This script deliberately
does not scrape ATG, Svensk Travsport, TV4, or any undocumented endpoint.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import shutil


GAME_LEGS = {"V75": 7, "V85": 8}
GAME_ID = re.compile(r"^V(?:75|85)[A-Za-z0-9_-]{1,90}$")


def verify_time(raw: object) -> str:
    if not isinstance(raw, str):
        raise ValueError("verified_at saknas")
    try:
        when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Felaktig verified_at") from exc
    if when.tzinfo is None or when.astimezone(timezone.utc) > datetime.now(timezone.utc):
        raise ValueError("verified_at ska ha tidszon och får inte ligga i framtiden")
    return when.isoformat()


def https_url(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("https://") or len(value) > 500:
        raise ValueError(f"{label} måste vara en HTTPS-adress")
    return value


def validate(source: dict) -> list[dict]:
    if source.get("schema_version") != 1 or not isinstance(source.get("games"), list):
        raise ValueError("calendar-source.json måste ha schema_version=1 och games-lista")
    if len(source["games"]) > 70:
        raise ValueError("För många omgångar")
    seen = set()
    games = []
    for entry in source["games"]:
        if not isinstance(entry, dict):
            raise ValueError("Varje omgång ska vara ett objekt")
        game_id = entry.get("id")
        game_type = entry.get("type")
        try:
            game_date = date.fromisoformat(entry.get("date", ""))
        except (TypeError, ValueError) as exc:
            raise ValueError("Felaktigt omgångsdatum") from exc
        if game_type not in GAME_LEGS or not isinstance(game_id, str) or not GAME_ID.fullmatch(game_id):
            raise ValueError("Omgångens ID eller V75/V85-spelform är ogiltig")
        if not game_id.startswith(game_type) or game_id in seen:
            raise ValueError("Dubbel eller felmärkt omgång")
        seen.add(game_id)
        source_info = entry.get("source", {})
        if not isinstance(source_info, dict) or source_info.get("rights_status") != "approved":
            raise ValueError(f"{game_id}: skriftligt kontrollerad återpubliceringsrätt krävs")
        source_url = https_url(source_info.get("url"), "source.url")
        permission_url = https_url(source_info.get("permission_url"), "source.permission_url")
        verified_at = verify_time(source_info.get("verified_at"))
        races = entry.get("races")
        if not isinstance(races, list) or len(races) != GAME_LEGS[game_type]:
            raise ValueError(f"{game_id}: fel antal lopp ({GAME_LEGS[game_type]} krävs)")
        for i, race in enumerate(races, 1):
            if not isinstance(race, dict) or not isinstance(race.get("starts"), list) or not race["starts"]:
                raise ValueError(f"{game_id}, avdelning {i}: startfält saknas")
            for start in race["starts"]:
                if not isinstance(start, dict) or not str(
                    start.get("horse", {}).get("name", "") if isinstance(start.get("horse"), dict) else ""
                ).strip():
                    raise ValueError(f"{game_id}, avdelning {i}: hästnamn saknas")
        games.append({
            "id": game_id,
            "type": game_type,
            "date": game_date.isoformat(),
            "source_url": source_url,
            "permission_url": permission_url,
            "verified_at": verified_at,
            "races": races,
        })
    return games


def build(root: Path, out: Path) -> dict:
    if out.resolve() == root.resolve() or out.resolve() == Path("/") or out.name != "site":
        raise ValueError("Utdatakatalogen måste heta site och får inte vara projektroten")
    source = json.loads((root / "data" / "calendar-source.json").read_text(encoding="utf-8"))
    validated = validate(source)
    if out.exists():
        shutil.rmtree(out)
    (out / "data" / "games").mkdir(parents=True)
    shutil.copy2(root / "index.html", out / "index.html")
    # Cloudflare Pages reads static response headers from the built asset root.
    # These headers reduce accidental exposure through caches/indexing; they
    # are NOT authentication and must be paired with Cloudflare Access.
    cloudflare_headers = root / "deploy" / "cloudflare" / "_headers"
    if cloudflare_headers.is_file():
        shutil.copy2(cloudflare_headers, out / "_headers")
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": 1,
        "status": "verified" if validated else "unavailable",
        "generated_at": now,
        "games": [],
    }
    for game in validated:
        manifest["games"].append({key: game[key] for key in (
            "id", "type", "date", "source_url", "permission_url", "verified_at"
        )})
        (out / "data" / "games" / (game["id"] + ".json")).write_text(
            json.dumps({"races": game["races"]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (out / "data" / "calendar.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("site"))
    args = parser.parse_args()
    result = build(args.root, args.output)
    print(f"Site built: {result['status']}, {len(result['games'])} licensed games")
