# スプリットタン婆 iOS 運用マニュアル（最小版）

PC なし・Cursor for iOS のみで、素材整理・相談・作業指示を回すための手順。

---

## 基本方針

| 役割 | ツール |
|---|---|
| 素材・リストの正本 | **GitHub** |
| 相談・判断・指示 | **Cursor iOS チャット** |
| バックアップ | iCloud / Google Drive（Agent 用ではない） |

**Agent は iCloud や PC ローカルにはアクセスできない。**  
GitHub に上げたものだけ自動処理できる。

---

## リポジトリ構成

### SplitTongueAssets（素材）

```
raw/                  … 生成直後の画像
named/                … リネーム済み
rename_map.json       … 35枚分のリネーム表
rename.bat            … PC 用ワンクリック実行
scripts/rename.py     … リネーム本体（Python）
scripts/rename.ps1    … リネーム本体（PowerShell）
expression_index.md   … 表情・舌・構図の索引
docs/rename-howto.md  … リネーム手順（PC）
docs/ios-workflow.md  … このマニュアル
```

### AnimeFactory（企画・台本）

```
docs/vol3-list.md
docs/vol4-list.md
マニュアル.md
```

---

## 日常フロー（5ステップ）

① 生成（Firefly 等）→ 写真アプリに保存  
② GitHub App で `raw/` に Upload（10〜20枚ずつ）  
③ 作業中だけ Public に変更  
④ Cursor iOS で指示  
⑤ 結果を GitHub で確認 → Private に戻す  

---

## 画像を GitHub に上げる

1. GitHub App でリポジトリを開く
2. **raw** フォルダをタップ
3. Add file → Upload files
4. 画像を選択（10〜20枚ずつ）
5. Commit changes

※ 必ず `raw` フォルダの中から Upload。

---

## Agent に読ませる

1. Settings → Change visibility → **Public**
2. Cursor iOS チャットに貼る：

```
Repo: https://github.com/mudapara/SplitTongueAssets
Public にした。raw/ に ○枚追加。

【依頼】（リネーム / Vol割当 / ★候補 など）

【制約】
- 舌超長は却下
- 昭和おばあちゃん感優先
```

3. 作業後 **Private** に戻す

---

## チャット指示テンプレ

### ■ 素材リネーム（マップ更新）

```
SplitTongueAssets raw/ に 35 枚追加。Public にした。
rename_map.json の from を埋めて、表情_舌_構図 で to を確定。
★★★ 候補を expression_index.md に反映して。
```

### ■ リネーム表だけ欲しい（PC で実行する場合）

```
raw/ のファイル一覧を見て、rename_map.json 用の from/to 案を出して。
却下候補も理由付きで。
```

### ■ Vol リスト相談

```
Vol.4 本音と建前編の32枚リストを見直して。
```

### ■ 生成プロンプト

```
穏やか_舌しまい_バスト正面 の Firefly プロンプト出して。
```

### ■ AnimeFactory 台本

```
フォーマット6、テーマ「建前と本音」のコマンド例を出して。
```

---

## PC がある場合のリネーム

iOS だけでは `rename.bat` は動かせない。PC で：

1. リポジトリを clone / pull
2. Agent が更新した `rename_map.json` を確認
3. `rename.bat --dry-run` → `rename.bat`
4. `named/` を commit & push

詳細は [rename-howto.md](rename-howto.md)。

---

## やってはいけないこと

- iCloud / PC パス指定 → 見えない
- 35枚以上一括 Upload → 重い
- 動画・PSD を GitHub → 408 エラー
- Public のまま放置 → 公開されたまま
- `REPLACE_ME_xx` のままリネーム実行 → 全部スキップされる

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| Repository not found | Public にする |
| push 408 | 10〜20枚ずつ |
| named/ が増えない | `rename_map.json` の from を確認。PC で `rename.bat` |
| 1〜3枚だけ | チャットに直接添付 |
| マップと画像が合わない | `expression_index.md` と突き合わせ |

---

## 関連リンク

- 素材: https://github.com/mudapara/SplitTongueAssets
- 台本: https://github.com/mudapara/AnimeFactory
- LINE: https://store.line.me/stickershop/author/4631928/ja
- リネーム手順: [rename-howto.md](rename-howto.md)
- 表情索引: [expression_index.md](../expression_index.md)
