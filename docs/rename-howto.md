# 素材リネーム手順

`raw/` に置いた生成画像を、`rename_map.json` に従って `named/` へ整理する手順。

---

## 前提

| フォルダ / ファイル | 役割 |
|---|---|
| `raw/` | Firefly 等で生成した直後の画像 |
| `named/` | リネーム済みの正本 |
| `rename_map.json` | 旧名 → 新名の対応表（35枚分） |
| `expression_index.md` | 表情・舌・構図の索引 |

命名規則: **`表情_舌_構図.png`**（例: `穏やか_舌しまい_バスト正面.png`）

---

## クイックスタート（PC）

1. 画像を `raw/` に入れる
2. `rename_map.json` の `from` を実ファイル名に書き換える
3. リポジトリ直下で `rename.bat` を実行

```bat
rename.bat --dry-run
rename.bat
```

`named/` にコピーされる。元ファイルは `raw/` に残る。

移動したい場合:

```bat
rename.bat --move
```

---

## rename_map.json の編集

各エントリの形式:

```json
{
  "from": "Firefly_20250705.png",
  "to": "穏やか_舌しまい_バスト正面.png",
  "stars": 3,
  "vol": 4,
  "memo": "採用候補"
}
```

| キー | 必須 | 説明 |
|---|---|---|
| from | ○ | `raw/` 内の元ファイル名 |
| to | ○ | `named/` への新ファイル名 |
| stars | — | 1〜3（★の数） |
| vol | — | Vol 番号（未割当は null） |
| memo | — | メモ |

初期状態では `from` が `REPLACE_ME_01.png` などのプレースホルダになっている。  
実ファイル名に差し替えるまで、その行はスキップされる。

---

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `rename.bat` | Python 優先で実行（なければ PowerShell） |
| `rename.bat --dry-run` | 実行内容の確認のみ |
| `rename.bat --move` | コピーではなく移動 |
| `rename.bat --map 別名.json` | 別マップを使用 |
| `python scripts/rename.py --help` | Python 版ヘルプ |
| `powershell -File scripts/rename.ps1 -DryRun` | PowerShell 版 |

---

## Cursor / Agent との連携

### PC（Agent がリポジトリにアクセスできる場合）

1. `raw/` に画像を追加
2. チャットで依頼:

```
raw/ に 35 枚追加した。
rename_map.json の from を埋めて、★★★ 候補を expression_index.md に反映して。
```

3. `rename.bat --dry-run` で確認 → `rename.bat` 実行
4. 変更を GitHub に push

### iOS（手動でマップを受け取る場合）

1. GitHub App で `raw/` に Upload
2. Cursor iOS でリネーム表を依頼（[ios-workflow.md](ios-workflow.md) 参照）
3. 返ってきた表を `rename_map.json` に反映（PC または次回 Agent 作業時）
4. `named/` を GitHub で確認

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| `[miss] raw/ に ○○ がありません` | `from` の綴り・拡張子を確認 |
| `[skip] 未設定スロット` | `REPLACE_ME_xx` を実名に変更 |
| `[skip] 既に存在 named/...` | 同名ファイルあり。削除するか `to` を変更 |
| Python がない | PowerShell 版が自動で動く |
| 35枚全部 miss | `raw/` にファイルが無い、または from 未設定 |

---

## 作業後のチェックリスト

- [ ] `named/` に意図したファイル名で入っている
- [ ] 舌超長・おばあちゃん感NGの画像を除外した
- [ ] `expression_index.md` の stars / vol を更新した
- [ ] GitHub に commit（10〜20枚ずつ推奨）

---

## 関連

- [expression_index.md](../expression_index.md)
- [ios-workflow.md](ios-workflow.md)
