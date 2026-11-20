# 現行判定（Stage 1-A v0.1.4／2026-11-20）

**総合PARTIAL。公開Schemaの日時全文一致P3はCLOSED、P2-02・P2-04は同梱検査器の範囲でCLOSED。計画・オフライン検査の技術審査は限定PASS。計画・オフライン基盤の正式受入はYES（Stage 1-Aの対象範囲に限定）、限定マージ推奨NO、Draft維持。実製品実測と第3実験はNOT_TESTED、開始HOLD。**

- **独立再審査完了**：[固定HEADの独立COMMENTレビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/8#pullrequestreview-5990128452)は `18b216a791ae7d42aaa30c5a987321603c0584b8`（tree `5ca241f4bf9a757a27888847b3a4a78667cd5533`）を対象に、別セッション・別検証領域で実施した。
- **Schemaと回帰の確認**：日時7項目の98対照で、旧Schemaは負対照42件を誤受理し、v0.1.4は98/98で期待どおり。追加70対照も同梱検査器と判定が一致した。合成85/85、manifest対照5/5、コピー先対照2/2、002回帰25/25、整合性検査はPASS。001のmanifest不一致は旧新で同じ。旧審査版からの変更10件はGitHubの別取得経路と全バイトが一致し、manifest 26件・lock 6件も整合した。
- **審査対象版の正式CI**：[run 44638486790](https://github.com/tetsujisugimori-coder/chatGPT-lab/actions/runs/44638486790) の `offline-tests` は成功。CIのcheckout `8829b9ed6b41ee042681e0b77a2ce543918f44ed` は審査対象HEADと同一tree。[v0.1.3のCI](https://github.com/tetsujisugimori-coder/chatGPT-lab/actions/runs/44477613986) と下記の判定は履歴。
- **正式受入の判断根拠**：共通読取計画・プロトコル、公開Schema、合成fixture、オフライン検査器を受け入れる。P2-01・P2-03の既存限定CLOSEDとP2-02・P2-04の同梱検査器限定CLOSEDを確認した。独立再審査の対象は `18b216a791ae7d42aaa30c5a987321603c0584b8`。受入判断時の `f9e1de654cd2cfcc47edac8d44f0040efcef41d5` との差分は `RESULTS.md` とそのmanifest登録だけで、[判断時の正式CI](https://github.com/tetsujisugimori-coder/chatGPT-lab/actions/runs/44735881040)も成功した。
- **実測開始HOLD**：各操作の25秒期限を強制できる読取経路の確認、実行・証拠保存の個別承認が必要。提出時の `PLAN.md` と `REVIEW-REQUEST.md` の判定は履歴として参照する。
- **保全の状況**：旧ZIPは今回の反映対象外（所在UNKNOWN・保存BLOCKED・独立再取得NOT_TESTED）。今回の独立再審査の新規検証原票は永続保存未実施。

---

以下は提出・補訂時点の履歴です。

# 現行判定（2026-11-19 / Stage 1-A v0.1.3 補訂）

**総合PARTIAL／P2-02・P2-04 OPEN／計画限定受入HOLD／限定マージ推奨NO／Draft・未マージ／実製品実測NOT_TESTED・開始HOLD。**

- [v0.1.2固定HEADの独立再レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/8#pullrequestreview-5969848402)（`1237709862c07ffa378d485e989cb77695723d09`）は実施済み。日時の7桁目以降を黙って切捨てることによる区間外・重複・25秒超過の偽PASSを再現し、**P2-02/P2-04 OPEN**と判定した。旧69/69、manifest5/5、コピー先2/2、002回帰25/25、旧CI PASSはv0.1.2時点の事実。
- v0.1.3補訂では共通日時パーサーとschemaの日時7種を統一、最大6桁を超える小数秒をパース前に拒否する。F41～F53、N19～N21の合成16件を追加し、標準集合は**85件**。旧入力・旧結果は保存し、検査前にPASSを宣言しない。
- **v0.1.3新HEADに対する独立再レビューはNOT_TESTED**。この版の正式CI、GitHub読戻し、実測結果は別途提出後に確認する。独立再レビューの判定が出るまでP2正式CLOSEDとしない。
- 旧ZIP所在UNKNOWN、Archive保存BLOCKED、外部独立再取得NOT_TESTED。新規検証原票の永続保存も未成立。旧ZIPの再生成で代用しない。
- 以下のv0.1.2・v0.1.1・v0.1.0記録は作成時の**履歴**であり現行判定を上書きしない。

---

# 現行判定（2026-11-19 / Stage 1-A v0.1.2補訂）

- **総合PARTIAL／計画限定受入HOLD／限定マージ推奨NO／Draft未マージ**。Chat/Work/Codex/dot実製品実測NOT_TESTED、開始HOLD。
- [v0.1.1独立再レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/8#pullrequestreview-5967735453)は固定HEAD `96ff7ffeb70515b78d888d9fc566ae3c578c9141` について **P2-01・P2-03限定CLOSED／P2-02・P2-04 OPEN** と判定。合成63/63、manifest5/5、コピー先2/2、002回帰25/25、当時のCI PASSは旧HEADの履歴。
- 今回はP2-02（操作区間の実行主体・site）とP2-04（厳密な25秒上限）を局所修正、合成6件を追加して69件とした。**新HEADの独立再レビューは未実施、両P2は正式CLOSED未認定**。新HEADの自己検査・CIは提出後の別証拠で判定する。
- 旧ZIPの所在UNKNOWN、Archive保存BLOCKED、保存先からの独立再取得NOT_TESTED。新検証原票の永続保存も未成立。旧ZIPの再生成は保全の代替としない。
- 下記「自己検証・提出前結果」以降はv0.1.0〜v0.1.1当時の歴史的記録であり、現行判定ではない。旧原票・旧結果は削除や上書きをしない。

---

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
