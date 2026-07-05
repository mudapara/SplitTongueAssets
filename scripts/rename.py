#!/usr/bin/env python3
"""raw/ の画像を rename_map.json に従って named/ へコピーまたは移動する。"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
NAMED_DIR = ROOT / "named"
DEFAULT_MAP = ROOT / "rename_map.json"


def load_map(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    raise ValueError("rename_map.json は配列か { \"items\": [...] } 形式にしてください")


def resolve_source(raw_dir: Path, name: str) -> Path | None:
    direct = raw_dir / name
    if direct.is_file():
        return direct

    matches = sorted(raw_dir.glob(name))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"[skip] 複数一致: {name}", file=sys.stderr)
        return None
    return None


def run(map_path: Path, dry_run: bool, move: bool) -> int:
    items = load_map(map_path)
    RAW_DIR.mkdir(exist_ok=True)
    NAMED_DIR.mkdir(exist_ok=True)

    ok = 0
    skipped = 0
    failed = 0

    for i, item in enumerate(items, start=1):
        src_name = item.get("from", "").strip()
        dst_name = item.get("to", "").strip()

        if not src_name or not dst_name:
            print(f"[skip] #{i}: from/to が空です")
            skipped += 1
            continue

        if src_name.startswith("REPLACE_ME"):
            print(f"[skip] #{i}: 未設定スロット {src_name}")
            skipped += 1
            continue

        src = resolve_source(RAW_DIR, src_name)
        if src is None:
            print(f"[miss] #{i}: raw/ に {src_name} がありません")
            failed += 1
            continue

        dst = NAMED_DIR / dst_name
        action = "move" if move else "copy"

        if dry_run:
            print(f"[dry] {action}: {src.name} -> named/{dst_name}")
            ok += 1
            continue

        if dst.exists():
            print(f"[skip] #{i}: 既に存在 named/{dst_name}")
            skipped += 1
            continue

        if move:
            shutil.move(str(src), str(dst))
        else:
            shutil.copy2(src, dst)

        stars = item.get("stars", "")
        star_txt = f" ({'★' * stars})" if stars else ""
        print(f"[ok] {src.name} -> {dst_name}{star_txt}")
        ok += 1

    print(f"\n完了: ok={ok}, skip={skipped}, miss={failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="rename_map.json に従い raw/ → named/ へ整理")
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP, help="マップ JSON（既定: rename_map.json）")
    parser.add_argument("--dry-run", action="store_true", help="実行せず表示のみ")
    parser.add_argument("--move", action="store_true", help="コピーではなく移動する")
    args = parser.parse_args()

    if not args.map.is_file():
        print(f"マップが見つかりません: {args.map}", file=sys.stderr)
        return 1

    return run(args.map, args.dry_run, args.move)


if __name__ == "__main__":
    raise SystemExit(main())
