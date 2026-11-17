# 002 GitHub不存在ファイル読取: 事前固定計画

固定日: 2026-11-17 UTC。対象は tetsujisugimori-coder/chatGPT-lab（公開）。
実行主体: 八兵衛の担当エージェント、クラウドLinux。画面上モデル名 UNKNOWN。
通常ChatGPT会話全般、モデル比較、速度、非公開権限、書込能力、MCP全般へ一般化しない。

## 対象と事前確認
開始main / 固定実験対象commit: `3e559a5a12c087ad22d3e1cc146d3aad0866ba33`
commitオブジェクトが指すtree: `8fa307eb94c1bdfe98bb0afc34cc0cbf01473742`
Git Trees API recursive=1の結果は truncated=false、12 entry（9 blob / 3 tree）。README.mdは2237 bytes、blob `1eb8a6e2871aea631191c2465a5be84eb1bd8a38`。
完全列挙にAGENTS.md、workflow、002実験はない。既存branch2件・PR #2のみ・Issue #1のみで重複実験なし。
PR #2は2026-11-17T09:04:24Z merge済み。旧本文/RESULTSのNO/NOT_TESTEDと、後の再レビュー5935603676の限定YESを区別し、旧記録を書き換えない。
既存9ファイルは同treeのblobとの一致を確認し、研究マップ、001 PLAN/RESULTS/verifyを読んだ。

負対照path: `experiments/002-github-missing-path/__intentionally_absent_20261117__.txt`
tree全entryに当該pathはない。このpathを作成しない。
正常対照path: `README.md`。
実験対象commitと提出branch HEADは別。専用branch `codex/002-github-missing-path` にこのPLANをcommitし、そのSHAと読戻しを記録してから以下の実測を開始する。main変更・PR #2再利用・マージなし。

## 固定手順・経路
順序: A-N → A-M → B-N → B-M。各経路で正常N→負M。補助操作はA/B本試行と別記録。
A: 接続GitHub `fetch_file`、encoding=base64、両caseとも上記repository/ref、line制限なし。
Aのtool schemaには期限引数がない。callerによる実処理期限強制はできず、その制約を明記する。待機打切りを処理停止と呼ばない。
B: 別curlプロセスによる認証なしHTTPS GET、
`https://api.github.com/repos/tetsujisugimori-coder/chatGPT-lab/contents/{path}?ref=3e559a5a12c087ad22d3e1cc146d3aad0866ba33`。
curl -q（設定無視）、--connect-timeout 10、--max-time 25、--request GET、Accept: application/vnd.github+json。Authorizationなし、CLI認証追加なし。HTTPエラーも本文保存し、exitとstatusを別記録。
各操作の再試行は通信失敗時だけ最大1回（最大8要求）、初回・再試行を別原票に残す。確定不存在、権限/機能制約には再試行しない。一般的なtoolエラーは通信失敗と断定せず再試行なし。
Bが環境制約で実行不能でもAを他toolで成功へ付け替えない。同じGitHub提供元の別取得経路であり、別真実源ではない。

## 保存と照合
case ID/経路/toolまたはコマンド/repository/commit/path/source/開始終了UTC/attempt/応答本文・エラー/exit code/HTTP status提供有無/観測分類を記録。
Aのstatusが返らなければ「未提供」(null)とし、error文中の404をstatus欄へ推測転記しない。エラーをファイル本文にしない。
正常本文はA base64応答の本文欄を復号（別表現なら実際の構造を記録）、BはContents JSONのencoding=base64/contentを復号。全byte・size/SHA-256/Git blobを両経路およびtreeのREADME blob/sizeと照合。復号不能はUNKNOWN。
秘密値・認証ヘッダー・私有URLは公開しない。接続APIの必要な応答を原票として保持し、メタデータとファイル本文を区別する。

## 期待値・固定判定
観測分類（success / explicit_missing / communication_failure / permission_or_feature_constraint / general_error / not_tested）と実験判定を分離する。
- PASS: 正常対照の本文取得・別経路照合が成立し、負対照は当該対象の明示的不存在応答、対象ファイルの本文なし。AにHTTP status未提供でも、明示的不存在エラーとBの根拠を別々に示せれば限定PASS。
- FAIL: 不存在pathを取得成功として扱う、別path内容や生成内容をファイル本文として返す等、事前期待と明確な矛盾。
- BLOCKED: 権限・機能・環境制約で予定操作が実行不能。
- UNKNOWN: timeout、一般的error、比較経路/正常対照不成立等で不存在への正しい応答を判断不能。
- NOT_TESTED: 未実行。
通信失敗・0 bytesだけでPASSにしない。判定を結果で緩めない。
複合結果は各case/経路ごとに記録し、全実験PASSは上記PASS条件全てが必要。明確な矛盾がなければFAILとせず、必要な比較が欠けた場合はUNKNOWN（操作自身のBLOCKEDは併記）。

## 成果物・検査・提出
PLAN/RESULTS/observations/manifest/verify.pyを002下に置く。verifyはオフライン記録検査でネットワーク代替ではない。
必須項目/型/case集合/固定SHA/path/判定根拠/size/SHA/blobを検査し、空・両側欠落・改変・誤PASSを拒否。正しいUNKNOWN原票の整合性PASSと実験PASSを分ける。
001の原PLAN/observations/過去結果を保持。必要なら001検査のscopeのみ002を正確に分離し、必須/集合/欠落/改変検査を保持して互換性調整を別報告する。
README/研究マップへ追記。新CI/依存なし。専用Issue・Draft PR、最終固定HEADから全変更pathを再取得し全byte/SHA照合。Actions/check 0は未実施。
案件専用領域を使用。原票・事前計画・結果・検査票を本人限定Libraryへ保管し、別pathへ実物再取得、size/SHA/ZIP CRC/manifest照合。自己確認・読戻し・独立レビューを区別、未実施はNOT_TESTED。Draft解除・マージなし。
