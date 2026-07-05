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
raw/     … 生成直後の画像
named/   … リネーム済み
docs/    … このマニュアル・索引
expression_index.md

### AnimeFactory（企画・台本）
docs/vol3-list.md
docs/vol4-list.md
マニュアル.md

---

## 日常フロー（5ステップ）

① 生成（Firefly 等）→ 写真アプリに保存
② GitHub App で raw/ に Upload（10〜20枚ずつ）
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

※ 必ず raw フォルダの中から Upload。

---

## Agent に読ませる

1. Settings → Change visibility → Public
2. Cursor iOS チャットに貼る：

Repo: https://github.com/mudapara/SplitTongueAssets
Public にした。raw/ に ○枚追加。

【依頼】（リネーム / Vol割当 / ★候補 など）

【制約】
- 舌超長は却下
- 昭和おばあちゃん感優先

3. 作業後 Private に戻す

---

## チャット指示テンプレ

■ 素材リネーム
SplitTongueAssets raw/ に ○枚追加。Public にした。
表情_舌_構図 でリネーム案と ★★★ 候補を出して。

■ Vol リスト相談
Vol.4 本音と建前編の32枚リストを見直して。

■ 生成プロンプト
穏やか_しまい_バスト正面 の Firefly プロンプト出して。

■ AnimeFactory 台本
フォーマット6、テーマ「建前と本音」のコマンド例を出して。

---

## やってはいけないこと

- iCloud / PC パス指定 → 見えない
- 35枚以上一括 Upload → 重い
- 動画・PSD を GitHub → 408 エラー
- Public のまま放置 → 公開されたまま

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| Repository not found | Public にする |
| push 408 | 10〜20枚ずつ |
| named/ が増えない | チャットでリネーム表を受け取る |
| 1〜3枚だけ | チャットに直接添付 |

---

## 関連リンク

- 素材: https://github.com/mudapara/SplitTongueAssets
- 台本: https://github.com/mudapara/AnimeFactory
- LINE: https://store.line.me/stickershop/author/4631928/ja
