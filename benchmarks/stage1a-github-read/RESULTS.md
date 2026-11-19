# Stage 1-A 自己検証・提出前結果

## 判定の分離

- 計画・オフライン検査基盤の**自己検査PASS**。正式な計画限定受入は独立レビュー待ちPENDING（現時点では正式受入済みとしない）。
- 独立レビューNOT_TESTED。依頼資料のみ作成。自己検査を別担当レビューと呼ばない。
- Chat/Work/Codex/dot実製品の横断実測NOT_TESTED、実測開始HOLD。第3実験NOT_TESTED、マージNO。
- 恒久保全・独立保全監査は未成立。新しいStage 1-A証拠束への保存承認の適用範囲が確認できないため、本人限定Library等への新規保存は行わない。ローカル原票と公開提出物の読戻しを分離して報告する。

## 対象と変更

開始main `560f2030a5065a98fb4cd2df10b6b8fcba7c4dad` / tree `94a2c07ff178d5d692ffc54c816420c126eeb6a0`。Stage 0 PR #6はmerged。
branch `feat/stage1a-common-benchmark`、Issue #7。新規`benchmarks/stage1a-github-read/`とREADME参照だけ。実験001/002と正本Stage 0定義は変更しない。
固定READMEは4831 bytes、blob `cf60f8abfaccd6b2afbfef1bae1fbd5aa4818642`。これは設計fixtureをGitから得たもので、製品呼出しの実験結果ではない。

## 合成検査

`python -B benchmarks/stage1a-github-read/test_verify.py <new-output-directory>`

標準ライブラリのみ、cloud Linux/Python（正確な版はresults/final-results.json）。各ケース別プロセス、15秒上限、stdout/stderr/exit/入力SHAと期待・実判定を保存。

- 最終 **56/56期待一致**。26正常整合（UNKNOWN/BLOCKED/FAIL/NOT_TESTEDという架空runを正しく保持する正常記録を含む）、29不正票拒否、1 REALモードBLOCKED。分母は新Stage 1-A独自合成集合であり旧Stage 0の50件ではない。
- 必須反例F01 Desktop→Local誤認、F02表示だけのモデル確定、F03 UNKNOWN→PASS、F04目的欠落、F05証拠なしPASS、F06条件差隠蔽ランキング、F07 dot委任→単独能力をすべて拒否。
- N04/N05は同じネットワーク差をdescriptiveなら条件差あり、controlled-rankingなら比較不可。N12/N13は許容差5秒の内外。これは合成の境界検査で本番timeout変更の許可ではない。
- 初回 **53/54**。N16のfixture生成で、故障対照F27と共有した配列を変更し、正常再試行入力までexplicit_missingへ変えていた。検査器はその不正なretryを正しく拒否。N16を通信失敗へ訂正して **54/54**。採点基準の緩和なし。
- 自己点検でexecutor/segment整合・事前固定時刻と操作時刻の境界を補強し、F28/F29を追加。56/56。正常本文を期待fixtureと全byte比較する補強後に同じ56件を再実行し56/56。
- 初回失敗入力と初回結果、fixture修正後結果、最終結果を別ファイルで保持。作成担当自身の修正であり独立レビュー指摘とは呼ばない。
- 新manifest/lockの正常・改変・欠落・余剰・入れ子manifestの5対照は`test_integrity.py`で実行。結果はresults/integrity-results.json。

`verify.py`のexit0は記録整合性のみ。実製品結果は常にNOT_TESTED。架空evidence参照や自己申告の真正性を証明しない。実証拠の来歴・取得・別担当監査は次ゲート。

## 既存001/002への影響

開始mainを別領域へgit archiveして旧verifyを実行。001は**開始時点でFAIL: manifest: file set mismatch**（Stage 0文書とREADME変更を旧manifestへ取り込んでいない）。これを今回の変更で生じた失敗とせず、また削除・更新して成功化もしない。
002は保存済み原票の整合検査PASS、25/25合成対照期待一致。出力中のnetwork_experiment PASSは旧002原票の分類で、今回の再測定ではない。
001/002全28ファイルとStage 0定義書1件の計29件を開始Git objectと全byte/SHA比較し不変。legacy-immutability.jsonに個別記録。
001全repo manifestの将来的scope契約は別途審査が必要。今回新基盤は独自manifestで集合・欠落・改変を検査し、旧範囲を勝手に変更しない。

## 提出・保全と残件

全提出物を最終固定HEADから再取得し全byte/size/SHAを自己照合する。最終HEAD/tree/変更一覧/CI確認/読戻しの実績は自己参照を避けPR追補に記す。新workflow・依存追加なし。run/checkが0ならCI NOT_TESTED。
ローカルZIP作成・CRC・manifest自己確認と、承認済み外部保管先への保存・再取得・別担当監査は別。後者の承認範囲を確認できておらずNOT_TESTED/承認確認BLOCKED。ACL全体・長期保持保証UNKNOWN。
次は固定版の独立レビューと、証拠保存先の本件適用範囲の確定。計画受入後も、製品ごとの実行可否・経路・有限停止・権限・保全・開始承認が整うまで実測HOLD。

## v0.1.1 P2補訂の記録（2026-11-19）

旧56/56・manifest 5/5・002 25/25はv0.1.0時点の歴史的結果。P2-01の順位ゲート、P2-02の操作区間検査、P2-03のコピー先拒否を実装し、反例F30〜F36の7件を追加（新合成計63件）。`test_safety.py`は元ディレクトリ自身・配下への出力指定を一時コピー上で拒否確認する。新規試験の実行結果、CI、独立再レビュー、原ZIPの外部保全・独立再取得は本文の補訂だけでPASSと扱わない。新HEADの独立実行結果を別途追記する。計画限定受入PENDING、実測開始HOLD、マージNO。
