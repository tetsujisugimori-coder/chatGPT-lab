# Stage 1-A v0.1.4 独立再審査条件（2026-11-20）

**総合PARTIAL／P2-02・P2-04は同梱検査器限定CLOSED／新規P3は独立再審査待ち／計画受入HOLD／マージNO／実測NOT_TESTED・開始HOLD。**

新固定HEADを独立取得し、公開Schemaの日時7項目に対するDraft 2020-12標準検証器の全文一致（余計な末尾文字・改行・秒付きオフセット・小数秒7桁以上の拒否）、正常日時とUTC同値オフセットの受理、同梱検査器の判定との一致を確認する。専用test_schema_standard.py（98対照）、既存合成85件、manifest5、コピー先2、002回帰25、正式CI、差分・lock・manifestを確認し、P3のCLOSED可否を判断する。

旧v0.1.3のCI・評価は履歴として保持する。旧ZIPの探索・保存・再生成は今回の対象外。Draft解除・マージ・実製品実測は実施しない。

---

# 最新独立再レビュー依頼（Stage 1-A v0.1.3 / 2026-11-19）

**総合PARTIAL／P2-02・P2-04 OPEN／計画限定受入HOLD／限定マージ推奨NO／Draft・未マージ／実製品実測NOT_TESTED・開始HOLD。** [v0.1.2独立再レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/8#pullrequestreview-5969848402)は実施済みで、共通日時パーサーの小数秒7桁目以降の切捨てを指摘した。**v0.1.3の独立再レビューはNOT_TESTED**（既存レビューの流用禁止）。

新しい固定HEADをGitHubから独立取得し、変更ファイル全byte・SHA・Git blob・lock・manifest・正本との整合性を確認してください。合成**85件**（旧69件＋N19～N21/F41～F53）、manifest変異5件、コピー先拒否2件、002回帰25件、001既知FAIL、正式CIを新しい環境で確認してください。

重点反例：25.000000s受理、25.0000001s拒否、25.000001s期限超過拒否、区間末尾+100ns拒否、操作重複+100ns拒否、7桁目0・登録日時・結果取得日時・区間始終・操作始終・訂正日時の過精度拒否。UTC同値+09:00/-05:00、6桁小数は受理。日時を丸めて成功扱いにしないこと。タイムゾーン欠落、不正オフセット、無効暦日も探索してください。schemaを通さない`time()`自体の過精度拒否と、Python 3.12系/3.13系のパース差の影響も確認してください。

固定HEAD、tree、parent、実行環境、期待/実際/終了コード/理由、旧版からのRED→GREEN、残存反例、独立性の限界を記載してください。P2-02/P2-04を独立にCLOSED/OPEN判定し、計画受入、マージ、実測許可、保全を混同しないこと。旧ZIPの所在UNKNOWN・保存BLOCKED・独立再取得NOT_TESTEDは別ゲート。

以下は過去版作成時のレビュー依頼履歴であり、最新のレビュー状況ではありません。

---

# 現行独立再レビュー依頼（Stage 1-A v0.1.2 / 2026-11-19）

**総合PARTIAL／計画限定受入HOLD／限定マージ推奨NO／実製品実測NOT_TESTED・開始HOLD**。旧HEAD `96ff7ffe` に対する[独立再レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/8#pullrequestreview-5967735453)は実施済みで、P2-01・P2-03限定CLOSED、P2-02・P2-04 OPEN。以下の初版「独立レビュー依頼資料（未実施）」は当時の履歴であり、現行のレビュー状況を示さない。

今回の修正版v0.1.2は**独立再レビューNOT_TESTED**。新しい固定HEADから別セッションが取得し、合成69件（旧63件＋N17/N18/F37〜F40）、manifest対照5件、コピー先対照2件、既存002回帰25件、001の既知FAIL、CI、全提出pathを確認する。P2-02は操作なし末尾区間のexecutor/site偽装、P2-04は25秒境界と25.000001秒・26秒の拒否を確認する。

旧ZIPの保全・再取得は別ゲートでBLOCKED/NOT_TESTED。合成PASSを実測PASSへ昇格させず、Draft解除・マージ・有料API・実測を開始しない。

---

# 独立レビュー依頼資料（未実施）

対象: このDraft PRの固定HEAD/treeとprotocol.lock.json。レビュー実施は今回の作業外で、状態NOT_TESTED。作成担当の自己検査を独立レビューPASSへ変換しない。

## 最小再現手順

`python -B benchmarks/stage1a-github-read/check_artifacts.py`

`python -B benchmarks/stage1a-github-read/test_verify.py <案件専用の未存在出力dir>`

既存002: `python -B experiments/002-github-missing-path/test_verify.py <新規出力dir>`

上記はオフライン合成/保存記録検査のみ。stdout/exit/個別input SHAとexpected/actualを確認する。初回53/54とfixture修正後54/54、帰属・日時境界補強後56/56を区別し、旧票を上書きしない。

## 観点

1. merged Stage 0の10 ID/UNKNOWN、開始時分類と実処理・モデル・委任の分離。
2. 必須項目欠落が先にREJECTEDになること、目的・同値・許容差の版固定。
3. 同じ2runがdescriptive/controlled-rankingで異なる判定になる根拠。
4. 7必須反例 F01〜F07の同じ入力での再検証、追加境界条件の探索。
5. 原票未取得のPASS、未知を補完するPASS、自己検査を独立監査扱いするPASSを拒否。
6. lockの自己参照回避、提出commitとの結合、実物再取得とACL/保持保証の区別。
7. REAL adapterを使えないこと。将来の製品実測には別計画・有限停止条件・許可・証拠監査が必要。
8. schema/semantic検査が証拠文字列の真正性を証明しない限界。
9. 原実験001/002不変、001の既存manifest不一致を隠していないこと。
10. 検査器の不足はP1/P2/P3、再現可能fixture、期待/実際/根拠付きで報告。修正後は同じ反例で再審査。

独立担当は使用AI、executor/環境、共有workspace・履歴継承・同一アカウント等の限界を記す。今回作成担当は八兵衛配下の担当AI、cloud Linux、モデル実体UNKNOWN。人間や別権限主体による監査ではない。

## 受入判断

計画限定の正式受入、実測開始、Stage 3、マージを別々に判定する。今回の最終自己検査56/56は計画基盤の候補としての根拠であり、独立レビュー完了・製品実測PASS・開始承認ではない。

## v0.1.1 追加審査条件（2026-11-19）

新固定HEADの読み戻し後に、`check_artifacts.py`、`test_verify.py <新規かつstage外のdir>`、`test_integrity.py <新規かつstage外のdir>`、`test_safety.py`を実行。F30〜F36の原入力・期待reason・実際exitを個別照合し、旧56件と新63件を区別する。順位主張と条件比較、操作と非重複区間、出力先の書込み前拒否をそれぞれ追加検証。原ZIPの保全と別担当再取得は別ゲート。
