# 001 GitHub read: 事前計画
固定日時: 2026-11-17T03:42:23.650Z (UTC; JST=UTC+9)

## 主体と範囲
実行主体は八兵衛の担当エージェント（ChatGPT dot、クラウドLinux作業環境）。画面上のモデル名は UNKNOWN。
GitHub接続ツールを主経路Aとし、認証なしHTTPS（curlによるGitHub REST/raw）を比較経路Bとする。同じGitHub提供元であり、別の真実源や別担当ではない。同じ応答の再読ではなく別取得経路での照合。
公開リポジトリの読取3操作だけを測定する。提出の書込は別の作業記録とし、書込能力試験と呼ばない。

## 先に固定する対象・手順・期待値
|ID|対象|経路A|期待結果と比較|
|---|---|---|---|
|G01|Hachibei-Lab / README.md @ 303ff502124681a519b6da8cb64a0232c9a73968|GitHub fetch_file（base64を要求）|本文全バイトを経路Bのraw取得と照合。Git blob IDとSHA-256も計算する。|
|G02|Hachibei-Lab Issue #45|GitHub fetch_issue|number=45、title/state/body/updated_atを取得。REST別取得と各値完全一致。|
|G03|Hachibei-Lab PR #46|GitHub get_pr_info|number=46、title/state/body、base/headのref・SHAとupdated_atを取得。REST別取得と各値完全一致。|

URL基点: https://github.com/tetsujisugimori-coder/Hachibei-Lab
G01: /blob/303ff502124681a519b6da8cb64a0232c9a73968/README.md
G02: /issues/45
G03: /pull/46

各リクエストの開始/終了UTCを記録する。比較時にupdated_atが異なれば変更競合としてUNKNOWNにし、内容不一致FAILと混同しない。
接続ツールが必須項目を返さない場合、欠落を明記する。補助fetchが必要なら独立した補助経路A2として記録し、元操作へ成功を付け替えない。
比較経路が取得不能なら取得の観測を残し照合UNKNOWN。認証回避、設定変更、依存導入は行わない。

## 判定（結果を見て緩和しない）
PASS: 全必須項目/本文を取得し、必要な別経路比較が一致。
FAIL: 実行できたが固定期待を満たさず、更新競合でもない。
BLOCKED: 権限/機能等で実行不能。
NOT_TESTED: 未実行。
UNKNOWN: 比較不能、更新競合、証拠不足。
モデル比較、非公開リポジトリ権限、速度ベンチマーク、LLM内部処理、MCP全般、引継ぎ独立性は今回NOT_TESTED。

## 安全性・記録
公開GitHubの必要フィールドのみ証拠に保存。認証値、個人メール、私有URLは転載しない。取得元・時刻・SHAを記録。
今回のchatGPT-labは初期READMEのみ、tree列挙にAGENTS.md/workflowなし。main直接変更禁止、専用branchの文書のみ、Draft PR、マージなし。
