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

## Stage 0：ChatGPTの定義と比較区分（v0.2補訂案）

[研究対象・実行環境・能力帰属の定義](docs/chatgpt-research-definition.md)に、Chat/Work Cloud/Work Local/Codex Local/Codex Cloud/八兵衛（dot）の比較区分と、起動面・実行場所・委任を分ける規約を記載しています。関連 [Issue #5](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/5)・[Draft PR #6](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/6)。

v0.1は独立レビューを実施し**総合PARTIAL・文書受入NO・マージNO**。P2-01（未知の開始時ID）、P2-02（目的別比較可否）、P3-01（レビューと受入・実測開始のゲート分離）についてv0.2を補訂した。**v0.2の元40分類反例・10変異の独立再審査はNOT_TESTED**。v0.1の結果36/40 PASS・9/10拒否をv0.2の成功には読み替えない。Draft維持・Stage 1正式移行HOLD。旧実験001/002は変更していない。各機能の動的検証はNOT_TESTED。
