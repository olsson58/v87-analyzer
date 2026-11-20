"""Convert a user-provided, explicitly mapped .xlsx startlist to local V75/V85 JSON.

This script does not fetch, publish, or license racing data. It deliberately
rejects ambiguous race numbers and unknown source-column layouts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from datetime import date as CalendarDate
from pathlib import Path


NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_XML_SIZE = 8 * 1024 * 1024
MAX_ROWS = 10000
ALIASES = {
    "avd": {"avd", "avdelning", "v85avd", "v75avd", "v85avdelning", "v75avdelning"},
    "number": {"nr", "nummer", "startnr", "startnummer", "horse number", "number"},
    "horse": {"hast", "hastnamn", "horse", "horse name", "name"},
    "driver": {"kusk", "kusk namn", "kuskens namn", "driver", "driver name"},
    "shoes": {"skor", "skoinfo", "shoes"},
    "cart": {"vagn", "vagninfo", "sulky", "cart"},
    "streak": {"streck", "streckprocent", "spelprocent", "streck %"},
}


class FormatError(ValueError):
    """Unrecognized or incomplete user-supplied startlist."""


def normal(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text).strip().lower())
    return re.sub(r"[^a-z0-9% ]", "", "".join(c for c in text if not unicodedata.combining(c))).strip()


def column_number(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref.upper())
    if not letters:
        raise FormatError(f"Felaktig cellreferens: {ref}")
    index = 0
    for char in letters.group():
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def safe_xml(archive: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        item = archive.getinfo(name)
    except KeyError as exc:
        raise FormatError(f"Excel-filen saknar {name}") from exc
    if item.file_size > MAX_XML_SIZE:
        raise FormatError(f"Excel-del för stor: {name}")
    return ET.fromstring(archive.read(item))


def read_workbook(path: Path) -> list[tuple[str, list[list[str]]]]:
    if path.suffix.lower() != ".xlsx" or path.stat().st_size > MAX_FILE_SIZE:
        raise FormatError("Välj en Excel-fil (.xlsx) på högst 20 MB.")
    try:
        with zipfile.ZipFile(path) as archive:
            if len(archive.namelist()) > 10000:
                raise FormatError("Excel-filen har för många delar.")
            strings: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                root = safe_xml(archive, "xl/sharedStrings.xml")
                strings = ["".join(t.text or "" for t in entry.findall(".//m:t", NS))
                           for entry in root.findall("m:si", NS)]
            workbook = safe_xml(archive, "xl/workbook.xml")
            rels = safe_xml(archive, "xl/_rels/workbook.xml.rels")
            targets = {}
            for relation in rels.findall("p:Relationship", NS):
                if relation.attrib.get("TargetMode") == "External":
                    continue
                targets[relation.attrib["Id"]] = relation.attrib.get("Target", "")
            result = []
            for sheet in workbook.findall("m:sheets/m:sheet", NS):
                name = sheet.attrib["name"]
                target = targets.get(sheet.attrib.get(f'{{{NS["r"]}}}id', ''), '')
                if target.startswith("/"):
                    part = target.lstrip("/")
                else:
                    part = "xl/" + target.lstrip("/")
                parts = []
                for segment in part.split("/"):
                    if segment == "..":
                        if not parts:
                            raise FormatError("Otillåten sökväg i Excel-filen.")
                        parts.pop()
                    elif segment not in {"", "."}:
                        parts.append(segment)
                part = "/".join(parts)
                if not part.startswith("xl/worksheets/"):
                    raise FormatError(f"Oväntad kalkylbladsfil: {part}")
                root = safe_xml(archive, part)
                rows = []
                for row in root.findall("m:sheetData/m:row", NS):
                    if len(rows) >= MAX_ROWS:
                        raise FormatError("Kalkylbladet har för många rader.")
                    values = {}
                    for cell in row.findall("m:c", NS):
                        idx = column_number(cell.attrib.get("r", ""))
                        kind = cell.attrib.get("t", "")
                        if kind == "inlineStr":
                            text = "".join(n.text or "" for n in cell.findall(".//m:t", NS))
                        else:
                            value = cell.find("m:v", NS)
                            text = value.text if value is not None and value.text is not None else ""
                            if kind == "s" and text:
                                try:
                                    text = strings[int(text)]
                                except (ValueError, IndexError) as exc:
                                    raise FormatError("Felaktig Excel-strängreferens.") from exc
                        values[idx] = text
                    if values:
                        rows.append([values.get(i, "") for i in range(max(values) + 1)])
                result.append((name, rows))
            return result
    except (zipfile.BadZipFile, ET.ParseError, OSError) as exc:
        raise FormatError("Kunde inte läsa Excel-filen som giltig .xlsx.") from exc


def identify_header(row: list[str]) -> dict[str, int]:
    keys = {}
    for col, value in enumerate(row):
        normalized = normal(value)
        for field, aliases in ALIASES.items():
            if normalized in aliases and field not in keys:
                keys[field] = col
    return keys


def convert(sheets: list[tuple[str, list[list[str]]]], *, game: str, date: str, track: str) -> dict:
    count = {"V75": 7, "V85": 8}.get(game)
    if count is None or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise FormatError("Ange V75 eller V85 samt datum ÅÅÅÅ-MM-DD.")
    try:
        CalendarDate.fromisoformat(date)
    except ValueError as exc:
        raise FormatError("Ogiltigt kalenderdatum.") from exc
    if not track.strip():
        raise FormatError("Bana måste anges.")
    legs: dict[int, list[dict]] = defaultdict(list)
    seen: set[tuple[int, int]] = set()
    for sheetname, rows in sheets:
        for offset, row in enumerate(rows):
            cols = identify_header(row)
            if not {"horse", "number"}.issubset(cols):
                continue
            named_game = re.match(r"(V75|V85)", sheetname.strip(), re.I)
            if named_game and named_game.group(1).upper() != game:
                raise FormatError(f"Blad '{sheetname}' gäller {named_game.group(1)}, inte {game}.")
            normalized_headers = {normal(x) for x in row}
            if ("v75avd" in normalized_headers and game != "V75") or ("v85avd" in normalized_headers and game != "V85"):
                raise FormatError(f"Blad '{sheetname}' har avdelningsrubrik för fel spelform.")
            sheet_leg = re.fullmatch(r"(?:V75|V85)[-_ ]?(\d+)|Avd(?:elning)?\s*(\d+)", sheetname.strip(), re.I)
            guessed_leg = int(next(g for g in sheet_leg.groups() if g)) if sheet_leg else None
            if "avd" not in cols and guessed_leg is None:
                raise FormatError(f"Blad '{sheetname}' har hästar men saknar avdelningskolumn. "
                                  "Banans vanliga loppnummer får inte gissas som V75/V85-avdelning.")
            for row in rows[offset + 1:]:
                field = lambda name: str(row[cols[name]]).strip() if name in cols and cols[name] < len(row) else ""
                horse, number = field("horse"), field("number")
                if not horse and not number:
                    continue
                if not horse or not re.fullmatch(r"\d{1,2}", number):
                    raise FormatError(f"Ofullständig hästrad i blad '{sheetname}'.")
                legtext = field("avd")
                if "avd" in cols and not re.fullmatch(r"\d{1,2}", legtext):
                    raise FormatError(f"Ogiltig avdelning för hästen '{horse}'.")
                leg = int(legtext) if "avd" in cols else guessed_leg
                number_int = int(number)
                if not 1 <= leg <= count or not 1 <= number_int <= 30:
                    raise FormatError(f"Ogiltig V75/V85-avdelning eller startnummer för '{horse}'.")
                if (leg, number_int) in seen:
                    raise FormatError(f"Dubbelt startnummer {number_int} i avdelning {leg}.")
                seen.add((leg, number_int))
                entry = {"startNumber": number_int, "horseName": horse}
                for column, key in [("driver", "driverName"), ("shoes", "shoes"), ("cart", "cart"), ("streak", "streak")]:
                    if field(column):
                        entry[key] = field(column)
                legs[leg].append(entry)
            break  # A single clearly identified table per worksheet.
    missing = [i for i in range(1, count + 1) if not legs[i]]
    if missing:
        raise FormatError(f"Omgången är inte komplett. Saknade avdelningar: {', '.join(map(str, missing))}. "
                          "Inga befintliga analysuppgifter ersätts.")
    return {
        "date": date, "track": track.strip(),
        "source": {"type": "user_supplied_excel", "permission_status": "not_verified_for_publication"},
        "races": [{"name": f"Avdelning {i}", "starts": sorted(legs[i], key=lambda h: h["startNumber"])}
                  for i in range(1, count + 1)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xlsx", type=Path, help="Egen Excel-fil från Filer")
    parser.add_argument("--inspect", action="store_true", help="Visa blad/rubrikrader utan att skapa JSON")
    parser.add_argument("--game", choices=["V75", "V85"])
    parser.add_argument("--date", help="ÅÅÅÅ-MM-DD")
    parser.add_argument("--track")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        sheets = read_workbook(args.xlsx)
        if args.inspect:
            for name, rows in sheets:
                matches = [(i + 1, row) for i, row in enumerate(rows) if {"horse", "number"}.issubset(identify_header(row))]
                print(f"Blad: {name}; {len(rows)} ifyllda rader; rubriker: {matches[:2]}")
            return 0
        if not args.game or not args.date or not args.track or not args.output:
            parser.error("--game, --date, --track och --output krävs för omvandling")
        result = convert(sheets, game=args.game, date=args.date, track=args.track)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Skapade lokal {args.game}-JSON: {sum(len(r['starts']) for r in result['races'])} hästar, {len(result['races'])} avdelningar")
        return 0
    except FormatError as exc:
        print(f"Import stoppad: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
