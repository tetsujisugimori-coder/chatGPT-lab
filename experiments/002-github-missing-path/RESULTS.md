# 002 GitHub不存在ファイル読取: 実測結果

## 判定
実験限定PASS、総合PARTIAL。八兵衛の担当エージェント／クラウドLinux／この公開repositoryの固定commit／2path／2経路のみ。通常ChatGPT全般への一般化、速度・モデル比較、非公開境界、一般書込能力、MCP全般はNOT_TESTED。

## 事前固定と開始
mainは指定どおり `3e559a5a12c087ad22d3e1cc146d3aad0866ba33`、tree `8fa307eb94c1bdfe98bb0afc34cc0cbf01473742`。更新差なし。PR #2は09:04:24 UTCにmerge済み。09:03:55 UTCの[再レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/2#pullrequestreview-5935603676)は前工程限定PASS/YES。PR本文/001 RESULTSの旧NO/NOT_TESTEDは当時の履歴として保持した。
完全tree 12 entry・9 blob・truncated=false。AGENTS.md/workflowなし。既存branch2、PR #2、Issue #1のみで002重複なし。既存9ファイルは固定treeのblobと全一致を検査して再利用した。参照文書を直接読んだ。

[事前計画commit](https://github.com/tetsujisugimori-coder/chatGPT-lab/commit/d4a337f922eb698fa474f56ee9189023c1d0859f)は11:10:37 UTC。PLAN全文を読戻し全byte一致確認してから11:10:58.721 UTCに実測開始。PLANは以後変更していない。
正常はREADME.md。負は `experiments/002-github-missing-path/__intentionally_absent_20261117__.txt`。全treeに当該pathなし。負対象は一度も作成していない。提出branch HEADと対象commitは分離。

## 実測（2026-11-17 UTC）
|case|開始→終了|観測|HTTP status|判定|
|---|---|---|---|---|
|A-N|11:10:58.721→11:10:59.068|fetch_file base64本文取得|未提供|PASS|
|A-M|11:11:00.073→11:11:00.379|isError=true、NOT_FOUND、Not Found、ファイル本文なし|未提供|限定PASS|
|B-N|11:11:15.620486→11:11:20.600158|認証なしcurl Contents API、exit 0|200を直接取得|PASS|
|B-M|11:11:20.601764→11:11:23.026257|同curl、exit 0、Not Found、ファイル本文なし|404を直接取得|PASS|

実施4操作、各1回、再試行0、未実施0。A-Mのerror文とerror_data.status="404"は原票に保持するが、transport HTTP status欄ではないため推測でstatusを埋めない。Bはcurlのhttp_codeを直接記録。エラーJSON141 bytesをファイル本文とは扱わない。Aのtool schemaには期限引数がなくcallerの実処理期限強制なし。Bはconnect 10秒・total25秒、curl -q、認証ヘッダーなし。CLI認証・設定変更なし。新たな通信実測による追試はしていない。

## byte照合・復号
A: response.structuredContent.content（encoding=base64）の改行を除き復号。B: HTTP response JSONのcontent（encoding=base64）を復号。復号した本文はraw/A-N-1.fileとraw/B-N-1.fileに保存。エラーのcontentブロックを本文として抽出しない。
両経路の2237 bytesが全byte一致。SHA-256 `fcc2ac0d4629d4b994f2bec8e80a815ee415d72dde7de4f8aa4073b099861ac5`、Git blob `1eb8a6e2871aea631191c2465a5be84eb1bd8a38`。固定treeのsize/blob、各応答のblobとも一致。
同じGitHubを情報源とする別取得経路であり、別真実源ではない。結果を見て事前規則は変更していない。

## オフライン検査と001互換性
verify.pyは保存記録の必須項目・型・case/試行集合・固定SHA/path・rawとの対応・分類根拠・比較・size/SHA/blob・manifest完全集合を検査する。ネットワークを再実測しない。正しいUNKNOWN原票は記録整合性PASS/実験UNKNOWNとして受理する。正常・反例25件は25/25期待一致（有効UNKNOWN 2件を含む）。反例と結果はtest_verify.py / verification-results.json。
001は002の正確なsubtreeだけを集合検査から分離し、独自manifestを002に置いた。001の他ファイル集合、必須ファイル、欠落・改変・hidden余剰・hash検査は削除しない。001 test_regressions.pyのfixture manifest生成にも同じ境界を適用。README/研究マップの追記とverify/helper変更に対応して001 manifestのみ更新する。
001の原PLAN・observations・RESULTS・P2-regression-resultsは全byte保持し、旧検証結果を上書きしない。互換性回帰の今回票は002のcompatibility-results.jsonに保存。既存110対照は旧66/110・今回110/110期待一致で既存修正契約を維持。新依存・CI追加なし。

## 提出・保全・独立性
[Issue #3](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/3)、専用branch `codex/002-github-missing-path`。Draft提出、マージなし。
提出固定HEADから全変更ファイルを再取得して照合し、本人限定保存先からZIP実物を別pathに再取得する。最終HEAD/tree・Actions/checks・実際の提出照合/保全結果は自己参照を避けPR最終報告に記載する。計画だけを完了扱いしない。
独立審査で検査器の固定経路契約不足P2を発見。raw.tool欠落/別tool、B method POST、B raw.source異値の4複製反例が初回は誤受理された。rawと正規化票のtool/source一致およびGET methodを検査する修正を加え、同じ4反例を拒否、25件は25/25期待一致。原ネットワーク票に誤帰属は確認されておらず、ネットワーク追試なし。初回・修正後の試験票を別に保全する。
修正後の別担当独立再レビューPASS、P2-R1限定CLOSED。同じ4反例の拒否、25/25・001 110/110の独立再実行を確認した。詳細は[独立票](INDEPENDENT-REVIEW.md)と初回/修正後のcounterexamplesを参照。独立レビューと提出後読戻し・保全は別の確認。経路排他性・担当の情報独立性はUNKNOWN。

## 残件・次の最小工程
この2pathの不存在応答は確認できたが、可用性・他path・他ref・権限境界を保証しない。次は固定提出版の独立審査であり、対象を増やす新実験は別の計画・依頼として扱う。
