# Stage 1-A 共通GitHub読取ベンチマーク計画 v0.1.3

状態: **総合PARTIAL／計画限定受入HOLD／限定マージ推奨NO／Draft・未マージ／実製品実測NOT_TESTED・開始HOLD**。v0.1.2独立再レビュー実施済み（P2-02/P2-04はOPEN）、v0.1.3独立再レビューNOT_TESTED。旧ZIP保存BLOCKED、再取得NOT_TESTED。
関連 [Issue #7](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/7)、Stage 0 [Issue #5](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/5)、merged [PR #6](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/6)。

## 正本と開始時確認（2026-11-18 UTC）

開始main `560f2030a5065a98fb4cd2df10b6b8fcba7c4dad`、tree `94a2c07ff178d5d692ffc54c816420c126eeb6a0`。PR #6はclosed/merged、merge commitと開始mainが一致。
[Stage 0定義](../../docs/chatgpt-research-definition.md) §3〜§8を正本とする。文書限定受入YESは製品実測許可ではない。今回の依頼はStage 1計画ゲートの作業だけを許可する。
開始treeの全列挙は `target-tree.txt`。AGENTS.md、.agents/skills、.github/workflowsは存在しない。既存branchとIssue/PRを確認し、Stage 1-A重複なし。Issue #5と001/002のPLAN・RESULTS・検査器を確認。001/002の原票・結果・manifest・コードを変更しない。

## 実験対象と入力

固定対象は開始mainの完全SHA。提出branchのHEADとは別管理。正常path `README.md` は `expected-readme.txt` に **Git objectから**保存した設計fixture。不存在path `__stage1a_intentionally_absent__/negative-control.txt` は完全treeにない。このpathは作成しない。
サイズ・SHA-256・Git blob・treeは `protocol.json`。cloneとGit object照合は設計準備であり、製品読取の実測ではない。002の過去4操作を再実測も再採点もしない。
共通指示は `INSTRUCTIONS.txt`、入力schemaは `input.schema.json`、検査器は `verify.py`。10比較IDとUNKNOWNは正本§3を継承。UNKNOWNは11番目の分類でもFAILでもない。

## 事前固定の方法

1. `protocol.json`、schema、検査器、指示、正常byte、tree列挙の正確なbyteを `protocol.lock.json` のsize/SHAに固定。
2. 計画の提出commitとそのtree、lock自体のSHAを別の開始承認票に記録。自己参照のため計画自身に将来のcommit SHAを書き込まない。
3. 独立レビューで計画/schema/fixture/採点器を検証し、権限・環境・保全の個別条件を承認してからのみ実測開始可。現在のDraft版は未承認。
4. 実際の事前固定日時は結果取得より前に第三者が追跡できる参照で示す。合成の日時と全0のplan_commitは明示的なダミーであり、実測承認の証拠ではない。
5. 改訂時は別protocol_versionと別SHA、新しい開始承認を使用。旧版・原票・採点を保存する。事後目的補完や採点規則の緩和禁止。

## 帰属・環境・証拠

開始ID、ID状態/理由/候補/証拠、initial/current client、experience/variant、OS/app版、表示モデルと確認済みモデル、executor、区間別時刻/site/証拠、delegate_chainを分離。
DesktopだけでLocalを確定しない。モデル表示だけならmodel_verified=UNKNOWN。混在はlocal/cloud双方の区間証拠が必要。開始IDは現在の実行先と独立であり、IDから実行先を補完しない。訂正はold/new/reason/actor/time/evidenceを追記し元票を保つ。
dotへの依頼、委任、実処理先を別評価。委任成功をdot単独成功やモデル能力としない。委任・主体不明を確定済みID順位に混ぜない。

## 将来の測定手順（今回はNOT_TESTED）

順序 A-N→A-M→B-N→B-M。各経路は正常→不存在、両pathで同じtool・完全ref。
Aは対象製品で利用できる読取経路を事前登録する。同じtoolを全10 IDで利用できると仮定しない。利用不能はBLOCKED、未起動はNOT_TESTED。経路差は条件として記録。
Bは別プロセスの認証なしHTTPS GET Contents API。認証追加・設定変更・課金なし。同じGitHubが情報源なので別の真実源ではない。
各操作connect10秒/total25秒、通信失敗だけretry最大1回、初回と再試行は別票。4操作、最大8要求。権限拒否・機能制約・明示不存在・一般errorは反復しない。
**tool期限を強制できない経路は現計画の開始BLOCKED**。待機打切りを処理停止と呼ばない。002で期限を設定できなかった接続toolを、同じ条件で実測可能とは認定しない。期限制約を変えるなら別版で審査。
対象変更、未承認権限、停止不能、証拠欠落、容量不足、保存許可不足が判明したら停止。別経路の成功を元toolへ付け替えない。

操作ごとにrepo/ref/path/source/tool/GET/権限/期限/開始終了UTC/attempt/raw_response/body/exit/status直接有無を記録。UTCを正本とし表示JST=UTC+9。HTTP未提供はnull、error文から404を推測しない。base64本文だけを厳格復号し、error本文を対象ファイル内容としない。
正常本文は全byte/size/SHA-256/Git blobと固定期待値・Bを照合。負対照は対象固有の明示不存在、本文なし。0 bytes・timeout・一般errorだけでPASS不可。

## 結果と比較の分離

- PASS: 正常両経路のbyte照合、両負対照の明示不存在、Bで直接HTTP200/404、本文非返却が成立。Aのstatusは未提供でもよい。
- FAIL: 固定内容不一致や不存在の成功扱い等、明確な矛盾。
- BLOCKED: 権限/機能/実行条件で必要工程を完遂不能。
- UNKNOWN: timeout/一般error/正常・比較経路不足等で結論不能。
- NOT_TESTED: 未実行。

`record_validation`は記録整合性、`synthetic_run_outcomes`は架空票の分類、`experiment_outcome`は実製品実測。今回最後は常にNOT_TESTED。有効UNKNOWN/BLOCKED票を受理しても実験PASSではない。

比較profileはprotocol内の2種類を固定。指標は「正常読取と明示不存在の正確性」で速度・モデル能力順位ではない。全条件を証拠付きで記録し、fixture/permissionsは両profileの必須同値。controlled-rankingではagents/route/network/retry/timeout/測定境界/model条件も必須同値。
descriptiveではこれらの観測可能な差を列挙可能。timeoutの差は5秒以内だけ許容差、超過は既知の記述差（同条件順位不可）。測定手順25秒を変えた実測は、先に別の許可済みvariantが必要。合成値30/31は境界検査で本番許可ではない。
比較目的等の事前必須欄欠落は最優先REJECTED/MISSING_PREDECLARED_FIELD/比較不可。目的自動補完なし。
必須同値不一致・重要証拠UNKNOWN・停止条件・差の影響不明→比較不可。既知の事前許容記述差→条件差あり。残りは比較可能。比較未実施はNOT_TESTED。比較可能は実測PASSや能力優越の証明ではない。

## 検査器の境界

この版は合成入力専用。`REAL`はBLOCKEDで起動adapterを持たない。ネットワーク呼出し・製品起動・ファイル保存能力試験を含まない。
JSON Schemaの明示的な小規模subsetを標準ライブラリで検査し、未対応keywordは拒否。schemaとsemantic checksを両方通す。空集合・両側証拠欠落を一致として受理しない。JSON重複key、不正型、未知field、lock不一致も拒否。
**evidenceの参照文字列やexecution-logという申告の真正性を自動証明しない**。今回は `synthetic:` の架空参照。実原物の取得・来歴・権限・モデルの真偽は別の独立監査が必要。REAL adapterの設計/認可は次ゲート。

## 保全と独立レビューの別ゲート

原証拠は通常権限・案件専用領域、既存承認が適用する保管先だけに保存。秘密値・私有URL・内部IDは公開しない。保存受付、実物再取得、全byte/SHA/CRC/manifest、別担当の照合、ACL/長期保持保証を別記録。
今回はDraft提出と自己読戻しまで。独立レビューと独立保全監査を先取りせずNOT_TESTED。依頼資料はREVIEW-REQUEST.md。
001検査器のrepo-wide manifestはStage 0追加時点ですでに集合不一致。今回それを書き換えて成功化しない。基準版からの001/002全byte不変、002回帰、今回の新manifestを別々に確認する。
正式受入は独立レビュー後の別ゲート。計画限定受入の候補として提出するが、正式受入PENDING、実測開始HOLD、Stage 3/第3実験NOT_TESTED、マージNO。

## v0.1.1 P2補訂（旧v0.1.0原結果は履歴保持）

P2-01: `comparison_decision`は条件の比較可能性のみ。合成入力の`ranking_status`は常に`NOT_TESTED`。順位主張は両runがPASSでなければ拒否し、架空のPASSであっても実能力の順位としての主張は拒否する。P2-02: 操作時刻は重複しない実行区間のいずれか一つに完全包含される必要があり、対応不明・重複を拒否する。P2-03: `test_integrity.py`はコピー元とその配下を出力先に指定するとコピー前にexit 2で拒否する。これらは実測開始の承認ではなく、補訂後の別レビューが必要。

## v0.1.2 局所補訂（2026-11-19）

P2-02: 実操作（observation != not_tested）の所属区間が一意であることを求め、実操作を含む区間のexecutorとexecution_siteからrunの実行主体・siteの整合を判定する。操作なし末尾区間を実績の根拠にしない。単一executorに帰属できない場合はUNKNOWNを保持する。操作なしrunはNOT_TESTEDであり、観測環境情報を実績に格上げしない。

P2-04: started_atとended_atの差をtimezone-aware timedeltaとして正確に計算し、操作自身が申告したtimeout_secondsを超えたらOP_DEADLINE_EXCEEDEDで拒否する。25秒ちょうどは境界内、25.000001秒や26秒は拒否。検査対象の時刻は同じ測定境界・十分な精度で記録すること。オフラインの時刻整合は、実際の期限強制・connect10秒・プロセス停止の証明にはならない。

旧63件と新69件、旧HEADと新HEADは別版の記録として扱い、独立再レビュー完了までP2-02/P2-04 OPEN、計画限定受入HOLD、実測HOLD、マージNO。

## v0.1.3 共通日時精度契約の局所修正（2026-11-19）

- 対応日時は `YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`、秒小数部は**0～6桁（存在する場合1～6桁）**に制限。時刻帯は明示必須。時・分・秒・UTCオフセットの字句範囲を制限し、実在しない暦日は`datetime.fromisoformat`が拒否する。
- 7桁以上は末尾が0であっても拒否する。マイクロ秒への丸め・切捨て・黙示的な精度低下は禁止。schemaの7種類の日時フィールドと`verify.py:time()`の共通入口でチェックする。
- 対象はpreregistered_at、results_available_at、segments/operationsのstarted_at・ended_at、corrections.at。実処理区間包含、重複、期限、登録先後比較で同一精度契約を使用。
- 合成反例F41～F53（13件）、正常N19～N21（3件）を追加。旧69件を履歴として保持し、新総数85件。25.0000001秒、区間末尾+100ns、操作重複100nsはSCHEMA_PATTERNで拒否。25.000000秒正常、25.000001秒超過、UTC等値の別オフセットは維持。
- これは**合成入力の記録整合性**のみで、OS上の期限強制・実プロセス停止・原票真正性・実製品実測を証明しない。
- 新HEADでの自己試験・正式CI・別担当の独立再レビューは提出後の実績で判定する。P2-02/P2-04は独立再レビューまでOPEN、計画受入HOLD、マージNO。旧ZIP所在UNKNOWN・保存BLOCKED、外部再取得NOT_TESTEDは変わらない。
