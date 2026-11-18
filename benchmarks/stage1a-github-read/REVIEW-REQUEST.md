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
