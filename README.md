# chatGPT-lab

ChatGPTを中心に、モデル、接続アプリ、MCP、外部AI・ソフトとの接続と実行能力を、事前計画と観測記録で研究します。公式な内部実装を解明したと主張する研究ではありません。

## 初回に分かったこと

2026-11-17、八兵衛の担当エージェントがGitHub接続ツールで、固定commitのREADME・既存Issue・既存PRを実際に取得しました。別のHTTPS取得経路との照合はG01〜G03すべてPASS。ただしIssue比較の初回はタイムアウトし、1回の再取得で一致しました。失敗履歴は保持しています。

これは当該公開対象・当該時刻・当該実行主体の読取に限ります。モデル名はUNKNOWN。全モデル、非公開リポジトリの権限境界、任意のMCP/外部ツール、書込一般、引継ぎの独立性は未検証です。

- [研究マップ](docs/research-map.md)
- [001 事前計画](experiments/001-github-read/PLAN.md)
- [001 実測結果と限界](experiments/001-github-read/RESULTS.md)
- [最小実行証拠](experiments/001-github-read/observations.json)
- [Issue #1](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/1)

## 実験の追加方法

1. `experiments/NNN-name/PLAN.md`に対象・主体・環境・日時・期待値・停止条件・権限を先に固定する。
2. 実測と合成試験、接続先の存在・読取・書込を分ける。
3. `RESULTS.md`にPASS / FAIL / BLOCKED / NOT_TESTED / UNKNOWNを根拠とともに記録する。
4. 秘密値を含まない最小証拠とhashを保存し、別経路比較の可否を明記する。
5. 専用branchとDraft PRで提出する。main直接変更・マージ・外部通知・設定変更・有料API使用は別承認。

今回CIや依存を追加していません。提出作業の成功は、事前計画のない書込能力実験のPASSとは扱いません。

## P2修正追補

[検査器の修正と110のオフライン対照](experiments/001-github-read/RESULTS.md)を追記。原観測と事前計画は維持。修正担当による自己検証であり、独立再レビューはNOT_TESTED。総合PARTIAL・限定マージNO・Draft維持。

## 第2実験（2026-11-17）
[002 不存在ファイル読取](experiments/002-github-missing-path/RESULTS.md)は固定公開commitのREADME正常対照と不存在path負対照に限りPASS。fetch_fileの明示NOT_FOUNDと認証なしHTTPSの404を区別し、正常本文2237 bytesを別経路照合した。総合PARTIAL、通常ChatGPT全般・モデル比較・非公開境界・MCP全般へ一般化しない。
前工程PR #2は後の再レビューを経てmerge済み。上記旧P2修正追補のNO/NOT_TESTEDは当時の履歴であり、原記録を保持する。今回の提出/保全/独立レビューは002とPRの結果を参照。

## Stage 0：ChatGPTの定義と比較区分（v0.2 文書限定受入）

[研究対象・実行環境・能力帰属の定義](docs/chatgpt-research-definition.md)に、Chat/Work Cloud/Work Local/Codex Local/Codex Cloud/八兵衛（dot）の比較区分と、起動面・実行場所・委任を分ける規約を記載しています。関連 [Issue #5](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/5)・[Draft PR #6](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/6)。

v0.1は当時の独立レビューで**総合PARTIAL・文書受入NO・マージNO**。v0.2でP2-01（未知の開始時ID）、P2-02（目的別比較可否）、P3-01（レビューと受入・実測開始のゲート分離）を補訂し、[独立再審査](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/6#pullrequestreview-5947211731)で**元40分類/40 PASS・10変異/10 PASS（文書規則のみ）**、旧P2 2件・P3 1件CLOSED、追加13件は12 PASS・1 FAILを確認した。新P3-02（C32/C39の入力説明逆転）は非blockingで、本版に訂正を反映。v0.1の36/40・9/10をv0.2の結果として流用していない。v0.2証拠ZIPはLibraryに保存し、別担当による実物再取得・全byte/SHA-256/CRC/manifest一致がレビュー上報告された。同一基盤・共有workspace・履歴継承の独立性制約、ACL全体・長期保持保証UNKNOWN、レビュー投稿後の読戻し記録が当該ZIPに含まれない点を維持する。

**文書限定受入YES・総合PARTIAL**。Stage 1正式移行・実測開始はHOLDであり、今回の文書限定マージ承認は製品機能や自動分類器の実測開始を許可しない。旧実験001/002は変更しておらず、動的Chat/Work/Codex/dot比較と当該文書のCIはNOT_TESTED。C25/C26の元入力の目的欠落による`REJECTED`と、目的を追加した説明用の仮想シナリオを区別する。
