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
