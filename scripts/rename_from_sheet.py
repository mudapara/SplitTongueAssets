#!/usr/bin/env python3
"""
rename_sheet.csv の「旧→新」に従ってファイル名を一括変更する。
複数フォルダ（named_bust, named_transparent など）を同時に変更可能。

使い方:
  py scripts/rename_from_sheet.py --propose
  py scripts/rename_from_sheet.py --folders named_bust,named_transparent --dry-run
  py scripts/rename_from_sheet.py --folders named_bust,named_transparent
  py scripts/rename_from_sheet.py --write-index
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG", ".JPEG", ".WEBP"}
DEFAULT_FOLDERS = ("named_bust", "named_transparent")
COMPOSITION_SUFFIXES = ("_バスト正面", "_バスト斜め", "_顔アップ")
SHEET_FIELDS = ("old", "new", "note", "tag")


@dataclass
class SheetRow:
    old: str
    new: str
    note: str
    tag: str


def normalize_fieldnames(fieldnames: list[str] | None) -> dict[str, str]:
    if not fieldnames:
        raise ValueError("CSV にヘッダー行がありません")
    return {name.strip().lower(): name for name in fieldnames}


def resolve_column(fields: dict[str, str], *candidates: str) -> str | None:
    for key in candidates:
        if key in fields:
            return fields[key]
    return None


def strip_composition(filename: str) -> str:
    stem = Path(filename).stem
    ext = Path(filename).suffix or ".png"
    for suffix in COMPOSITION_SUFFIXES:
        if stem.endswith(suffix):
            return f"{stem[: -len(suffix)]}{ext}"
    return f"{stem}{ext}"


def propose_new_name(base: str, index: int, total: int) -> str:
    if total <= 1:
        return base
    stem = Path(base).stem
    ext = Path(base).suffix or ".png"
    return f"{stem}_{index:02d}{ext}"


def read_sheet(sheet_path: Path) -> list[SheetRow]:
    if not sheet_path.exists():
        raise FileNotFoundError(f"対応表がありません: {sheet_path}")

    rows: list[SheetRow] = []
    with open(sheet_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = normalize_fieldnames(reader.fieldnames)

        old_key = resolve_column(fields, "old", "旧", "旧名")
        new_key = resolve_column(fields, "new", "新", "新名")
        note_key = resolve_column(fields, "note", "メモ", "備考")
        tag_key = resolve_column(fields, "tag", "tab", "タグ", "タブ")
        if not old_key or not new_key:
            raise ValueError("CSV には old,new（または 旧,新）列が必要です")

        for row in reader:
            old_name = (row.get(old_key) or "").strip()
            if not old_name:
                continue
            rows.append(
                SheetRow(
                    old=old_name,
                    new=(row.get(new_key) or "").strip(),
                    note=(row.get(note_key) or "").strip() if note_key else "",
                    tag=(row.get(tag_key) or "").strip() if tag_key else "",
                )
            )

    return rows


def write_sheet(sheet_path: Path, rows: list[SheetRow]) -> None:
    with open(sheet_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(SHEET_FIELDS)
        for row in rows:
            writer.writerow([row.old, row.new, row.note, row.tag])


def propose_names(rows: list[SheetRow]) -> list[SheetRow]:
    grouped: dict[str, list[SheetRow]] = defaultdict(list)
    for row in rows:
        grouped[strip_composition(row.old)].append(row)

    proposed: list[SheetRow] = []
    for base in sorted(grouped):
        group = sorted(grouped[base], key=lambda r: r.old)
        total = len(group)
        for index, row in enumerate(group, start=1):
            proposed.append(
                SheetRow(
                    old=row.old,
                    new=propose_new_name(base, index, total),
                    note=row.note,
                    tag=row.tag,
                )
            )

    proposed.sort(key=lambda r: r.old)
    return proposed


def write_init_sheet(folder: Path, sheet_path: Path) -> int:
    if not folder.exists():
        raise FileNotFoundError(f"フォルダがありません: {folder}")

    files = sorted(
        p.name for p in folder.iterdir() if p.is_file() and p.suffix in IMAGE_EXTS
    )
    if not files:
        raise FileNotFoundError(f"画像がありません: {folder}")

    rows = [SheetRow(old=name, new="", note="", tag="") for name in files]
    write_sheet(sheet_path, rows)
    return len(files)


def rename_files(
    folder: Path,
    mappings: list[tuple[str, str]],
    *,
    dry_run: bool,
) -> tuple[int, int, int, int]:
    ok = 0
    skip = 0
    missing = 0
    conflict = 0

    for old_name, new_name in mappings:
        if not new_name:
            skip += 1
            continue
        if old_name == new_name:
            skip += 1
            continue

        src = folder / old_name
        dest = folder / new_name

        if not src.exists():
            print(f"  MISSING: {old_name}")
            missing += 1
            continue

        if dest.exists() and dest != src:
            print(f"  CONFLICT: {new_name} は既に存在（元: {old_name}）")
            conflict += 1
            continue

        if dry_run:
            print(f"  OK  {old_name} -> {new_name}")
        else:
            src.rename(dest)
            print(f"  OK  {old_name} -> {new_name}")
        ok += 1

    return ok, skip, missing, conflict


def file_exists(folder: Path, name: str) -> bool:
    return (folder / name).is_file()


def write_assets_index(
    sheet_path: Path,
    index_path: Path,
    folders: list[str],
) -> int:
    rows = read_sheet(sheet_path)
    folder_paths = {name: REPO_ROOT / name for name in folders}
    bust_folder = folder_paths.get("named_bust")
    transparent_folder = folder_paths.get("named_transparent")

    lines = [
        "# Assets Index",
        "",
        "rename_sheet.csv に基づく素材一覧。",
        "",
        "| new | old | tag | note | bust | transparent |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        bust = "o" if bust_folder and file_exists(bust_folder, row.new) else "-"
        transparent = (
            "o" if transparent_folder and file_exists(transparent_folder, row.new) else "-"
        )
        tag = row.tag.replace("|", "\\|")
        note = row.note.replace("|", "\\|")
        lines.append(
            f"| `{row.new}` | `{row.old}` | {tag or '-'} | {note or '-'} | {bust} | {transparent} |"
        )

    lines.extend(
        [
            "",
            "## 集計",
            "",
            f"- 行数: {len(rows)}",
            f"- 対象フォルダ: {', '.join(folders)}",
            "",
            "## 関連",
            "",
            "- [rename_sheet.csv](rename_sheet.csv)",
            "- [expression_index.md](expression_index.md)",
        ]
    )

    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def parse_folders(folder_arg: str | None, folders_arg: str | None) -> list[str]:
    if folders_arg:
        return [f.strip() for f in folders_arg.split(",") if f.strip()]
    if folder_arg:
        return [folder_arg]
    return list(DEFAULT_FOLDERS)


def main() -> int:
    parser = argparse.ArgumentParser(description="CSV 対応表でファイル名を一括変更")
    parser.add_argument("--folder", help="対象フォルダ1つだけ指定するとき")
    parser.add_argument(
        "--folders",
        default=",".join(DEFAULT_FOLDERS),
        help="対象フォルダ（カンマ区切り。既定: named_bust,named_transparent）",
    )
    parser.add_argument("--sheet", default="rename_sheet.csv", help="対応表 CSV")
    parser.add_argument("--init", metavar="FOLDER", help="フォルダ内の現ファイル名で CSV を作る")
    parser.add_argument("--propose", action="store_true", help="new 列を構図除去名で提案して CSV を更新")
    parser.add_argument("--write-index", action="store_true", help="assets_index.md を生成")
    parser.add_argument("--dry-run", action="store_true", help="確認のみ。変更しない")
    args = parser.parse_args()

    sheet_path = REPO_ROOT / args.sheet
    folders = parse_folders(args.folder, None if args.folder else args.folders)

    if args.init:
        folder = REPO_ROOT / args.init
        try:
            count = write_init_sheet(folder, sheet_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        print(f"作成しました: {sheet_path}")
        print(f"  {count} 行（old 列に現ファイル名、new 列は空）")
        return 0

    if args.propose:
        try:
            rows = read_sheet(sheet_path)
            proposed = propose_names(rows)
            write_sheet(sheet_path, proposed)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        print(f"提案しました: {sheet_path}")
        groups = defaultdict(list)
        for row in proposed:
            groups[strip_composition(row.old)].append(row)
        dup_groups = sum(1 for group in groups.values() if len(group) > 1)
        print(f"  {len(proposed)} 行 / 重複グループ {dup_groups}")
        for row in proposed[:5]:
            print(f"  {row.old} -> {row.new}")
        if len(proposed) > 5:
            print("  ...")
        return 0

    if args.write_index:
        index_path = REPO_ROOT / "assets_index.md"
        try:
            count = write_assets_index(sheet_path, index_path, folders)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        print(f"生成しました: {index_path} ({count} 行)")
        return 0

    try:
        rows = read_sheet(sheet_path)
        mappings = [(row.old, row.new) for row in rows]
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("=== CSV リネーム ===")
    if args.dry_run:
        print("（dry-run: 変更しません）")
    print(f"対象フォルダ: {', '.join(folders)}")
    print(f"対応表: {sheet_path}")
    print()

    total_ok = total_skip = total_missing = total_conflict = 0

    for folder_name in folders:
        folder = REPO_ROOT / folder_name
        print(f"--- {folder_name}/ ---")
        if not folder.exists():
            print("  SKIP: フォルダがありません")
            print()
            continue

        ok, skip, missing, conflict = rename_files(folder, mappings, dry_run=args.dry_run)
        total_ok += ok
        total_skip += skip
        total_missing += missing
        total_conflict += conflict
        print(f"  小計: 変更 {ok} / スキップ {skip} / 欠落 {missing} / 重複 {conflict}")
        print()

    print("=== 合計 ===")
    print(f"  変更: {total_ok}")
    print(f"  スキップ: {total_skip}")
    print(f"  見つからない: {total_missing}")
    print(f"  重複: {total_conflict}")

    return 1 if total_missing or total_conflict else 0


if __name__ == "__main__":
    raise SystemExit(main())
