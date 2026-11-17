# 001 GitHub read: 実測結果

## 判定と事前固定

G01 / G02 / G03の固定された公開読取はPASS。文書基盤の整備は限定完了、研究全体は未測定領域を残す。初回Issue比較のタイムアウトを成功に書き換えない。

事前計画は[58413d39](https://github.com/tetsujisugimori-coder/chatGPT-lab/commit/58413d39e20f0a8abc3fd1cac2ced5921d122c75)でGitHubへ固定した後に実測した。対象リポジトリの正式表記は `chatGPT-lab`。開始mainは `a7b16e8860f90ecdd7d7ee1ba32e7c92c032f697`、treeは `9f74e1728781c4bc1aba4535265267520f7f114a`。初期README 1件だけで、Issue/PRは0件、AGENTS.md・workflow・必須検査定義はtree上に存在しなかった。mainの初期化は本人が済ませており、こちらでは行っていない。

## 実行主体と取得経路

- 主体: 八兵衛の担当エージェント。アプリ: ChatGPT dot。利用者の通常ChatGPT会話そのものを測定した結果ではない。
- 環境: クラウドLinux x86_64、Python 3.12.14、git 2.52.0、curl 8.14.1。画面上のモデル名: UNKNOWN。
- A: 接続済みGitHub用tool。認証先loginを確認して開始した。
- B: 別のcurlプロセスによる認証なしHTTPS GET、GitHub REST/raw。AとBは同じGitHubを情報源とし、別運営者による真偽保証ではない。別担当の独立レビューでもない。
- `gh` CLIは未ログインで利用BLOCKED。接続ツールの認証とCLI認証が別であることを観測。認証設定は変更していない。
- 取得・照合日時は下表のUTC。JSTは+9時間（03:42〜03:43 UTC = 12:42〜12:43 JST）。時刻とtool応答の選択フィールドは[observations.json](observations.json)。基盤内部の完全ログではない。

## 3操作

|ID|固定対象・tool|A開始→終了 UTC (2026-11-17)|Bの取得時刻 UTC|結果・照合|
|---|---|---|---|---|
|G01|[README](https://github.com/tetsujisugimori-coder/Hachibei-Lab/blob/303ff502124681a519b6da8cb64a0232c9a73968/README.md)、`github_fetch_file` base64|03:42:45.858→03:42:46.203|03:43:04.193→03:43:12.669|PASS。2067 bytes全byte一致、Git blob一致|
|G02|[Issue #45](https://github.com/tetsujisugimori-coder/Hachibei-Lab/issues/45)、`github_fetch_issue`|03:42:46.203→03:42:46.566|初回03:43:12.670→03:43:37.687、再取得03:43:52.855→03:43:58.228|PASS（比較再取得）。番号・title/state/body/updated_at一致|
|G03|[PR #46](https://github.com/tetsujisugimori-coder/Hachibei-Lab/pull/46)、`github_get_pr_info`|03:42:46.566→03:42:46.936|03:43:37.687→03:43:41.064|PASS。番号・title/state/body/updated_at・base/head refとSHA一致|

G01固定commit: `303ff502124681a519b6da8cb64a0232c9a73968`。Git blob `769f35bf09bbe2d6236d59614d8a2419a2eaebf7`、SHA-256 `8d6e847a6609e40e1a3e32317df7ad6d8c727d624361a1f10c0f60926438affc`。
G02はopen、updated_at=`2026-11-16T12:47:43Z`。G03はclosed/merged、updated_at=`2026-11-16T11:46:47Z`。比較中の更新差はなかった。PR本文に残る過去の「Draft維持」は履歴であり、現在のstate/mergedフィールドとは分けて読んだ。

G02比較の初回はcurl exit 28、25秒タイムアウト、0 bytesで照合BLOCKED。1回の上限20秒付き再取得で成功した。継続的可用性や性能保証ではない。事前期待項目は変えていない。

## 開始確認と提出の記録

- 接続ツールのリポジトリ一覧検索とAPIで正式名称を確認し、同名別リポジトリや重複PRを作らなかった。
- Issues/PRの既存集合0件を確認し[Issue #1](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/1)を作成。専用branch `codex/research-map-github-read`を使用。
- workflow一覧endpointは接続ツールで未対応(400)、curlでもtimeoutだった。workflowファイル不存在は完全tree列挙で確認した。設定や外部連携の網羅検査を実施したとはしない。
- tree APIへmain/commitを渡すと応答のsha欄にcommit値が表示されたため、HEAD→treeはGit commitオブジェクトのtreeを用い、そのtree SHA指定でも内容を取得した。commit SHAとtree SHAを同一視しない。
- Git Data APIによる通常commit・非force branch更新を使用。これは提出経路でありG01〜G03の実験ではない。最終提出HEADと読戻し結果はPR本文に記録する（自己参照を避ける）。

## 検証・証拠の範囲

`python experiments/001-github-read/verify.py`で記録の期待集合、本文hash、比較値、Git blob、manifest、ローカル文書リンクを自己確認する。観測証拠を独立再取得するスクリプトではない。
証拠は公開済みの必要フィールドに限定し同じPRへ収録。秘密/認証値・個人メール・私有保管URLは含めない。外部Library/Spaceへの別保存は今回は行っていない。GitHub提出後の実物読戻し・SHA-256照合は行い、PRへ結果を記録する。
既存必須CIなし、新CI/依存/ブラウザ試験追加なし。独立レビューはNOT_TESTED、実施した確認は自己確認。CI run/checkが0件でもCI PASSではない。

## 分かったこと・限界・次候補

接続toolが表示されるだけでなく、固定公開README本文とIssue/PRの必要情報を実際に読めた。別経路比較も成立した。一方、接続toolとCLIの認証は共有されていなかった。
モデル別性能、権限拒否の正確性、非公開境界、外部AI、書込一般、継続・引継ぎ、未公開内部処理はNOT_TESTED/UNKNOWN。既存研究のPASSは今回の実測へ流用していない。

次は「固定commitの存在しないpathを読む負対照」を1件提案する。成功する読取だけでなく、不存在を誤って成功扱いしないか、toolのエラーと内容欠落を区別できるかを小規模・非破壊に確認できる。まだ実行していない。


## 2026-11-17 P2 修正追補（オフライン自己検証）

基準 HEAD `9f4a642ec4139b8f9ce93307a71fce793a502e5e`、tree `0f74e0760a0b016b37699d07cd446b07e71104d0`。
[独立レビューのP2二件](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/2#pullrequestreview-5933827456)への修正。今回の担当は初回実装担当と同一であり、以下を独立再レビューとは呼ばない。

- P2-01: repository root の `.git` ディレクトリ／worktree pointerだけを対象外にし、manifest自身の除外は正確な1 pathに限定。全提出ファイルの集合、必須6ファイル、サイズ、SHA検査を維持。他のhiddenファイルは除外しない。symlinkは暗黙追跡せず拒否。
- P2-02: G01本文・byte長・SHA-256・Git blobを両snapshotで再計算。G02のnumber/title/state/body/updated_at、G03の追加base/headと各ref/shaの存在・型を検査。matchesの必要キー集合と厳密なbool trueを要求し、snapshotを再比較。空bodyは受理。
- 同じ110対照を旧・新版へ適用。旧版66/110期待一致、新版110/110期待一致。44件は同じ入力のRED→GREEN、残り66件は既存の受理／拒否維持。これは110種類のネットワーク実測ではなく局所複製データの試験。
- 通常展開、実git init＋commit checkout、実git worktree（.gitファイル）の正常対照、片側／両側必須項目欠落、型不正、空／不足／非bool matches、値不一致、空body、ファイル欠落・改変・size/SHA・余剰hidden・別pathのmanifestを検査。内容反例は毎回manifestを再計算してから実行。起動不能ではなく検査器の応答と終了codeで判定。
- [反例コード](test_regressions.py)と[各caseの旧新出力・終了code](P2-regression-results.json)を参照。引数は旧版7ファイル展開、現版展開、新規の案件別出力先。作成したfixtureを保持し、原票は変更しない。
- 原observations.json、PLAN.md、研究マップ、G02初回timeout履歴は全byte不変。G01〜G03をネットワーク再実測していない。不在path・モデル比較・MCP・ブラウザ実験は未実施。
- 自己検証上P2二件は修正済み。独立再レビューはNOT_TESTED、総合PARTIAL、限定マージNO、Draft維持。旧読取限定PASSの証拠範囲は変えない。
- 今回のCI、提出後照合、本人限定保全の結果はPR最終コメントに追補する。run/check 0をCI成功に扱わない。
