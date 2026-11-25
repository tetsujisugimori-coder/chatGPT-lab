# Stage 1-B Codex Local 読取・停止・回収の結果

**匿名パイプによるローカル合成試験は9件 PASS、25秒発火対照は1件 FAIL。現行サンドボックスでのループバック TCP 接続は BLOCKED。共通ベンチマークの実測開始は HOLD。**

[Draft PR #9](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/9) の開始 HEAD は `6e46e2d00ebeb8062d6ed16807f90a075e788153`、tree は `a0cd7b3332f1441f10d56beef11c5cd35ade045e`。元の差分は Stage 1-B の計画、製品経路停止記録、curl 対照コードの3ファイル。今回の追加はこのディレクトリ内です。

## 実行環境

| 項目 | 観測 |
| --- | --- |
| クライアントと比較 ID | Codex Desktop のローカル実行、Codex CLI 0.170.0、CODEX-LOCAL 候補 |
| OS と実行系 | Windows 11 x64、NT 10.0.26300.9974、PowerShell 7.6.9、Python 3.14.7 x64 |
| 場所と主体 | ローカル Windows ワークスペース。Codex のシェルから同じ Windows ユーザーで Python を起動。実効管理者なし、委任なし。確認済みモデル識別子は UNKNOWN |
| 権限と制約 | managed、workspace-write、ネットワーク制限。ローカル試験は既定権限。IPv4 の 127.0.0.1 は bind/listen 成功、connect は WinError 10013 |
| 採用経路 | Windows 匿名パイプ2本を介し、Python 標準ライブラリで合成 CONNECT / HTTP GET の生フレームを読取 |
| 制御と回収 | Python 監督が Windows の Job Object に suspended で生成した読取プロセスを登録して再開。読取側が接続上限を執行し、監督が通常停止と強制停止を発行。Windows が Job とプロセスハンドルの終了状態を返す。監督自身の外側 Job 所属も確認 |

予備試行で `CREATE_NO_WINDOW` が試験専用の `conhost.exe` を Job に含める挙動を特定し、正式試行は `DETACHED_PROCESS` を使用した。テストの Job 累計は各試行で予期した1または2。IPC 初期対照で見つかったストリームの `flush` と `read1(0)` の実装不具合を修正し、各予備原票の出力を保持した。正式試行は `ipc-full-20261126` の新規出力で実施した。GitHub の管理操作は別経路で行った。

## 実測

計画・コードと試行条件は **2026-11-25 16:15:29.609362 UTC** に SHA-256 で固定した。以下は起動開始を原点とした単調時間の秒表示。比較と判定には原票の整数ナノ秒を使用した。停止要求の欄は通知ファイル公開の観測時刻、終了の欄はプロセスハンドルのサイン観測時刻。

| 条件 | 結果 | 停止要求 | 強制停止要求 | 終了観測 | 回収完了 | HTTP / 本文 / 終了コード |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 正常読取 | PASS | — | — | 0.188251 | 0.190430 | 200 / 20 B / 0 |
| 明示不存在 | PASS | — | — | 0.191915 | 0.192400 | 404 / 0 B / 4 |
| 接続待ち短縮 | PASS | 1.001696 | — | 1.014490 | 1.014753 | 未取得 / 0 B / 20 |
| 本文待ち短縮 | PASS | 1.000357 | — | 1.017917 | 1.018547 | 200 / 9 B / 21 |
| 接続待ち10秒 | PASS | 10.002433 | — | 10.016297 | 10.016596 | 未取得 / 0 B / 20 |
| 本文待ち、回収予算あり | PASS | 24.501574 | — | 24.518867 | 24.519411 | 200 / 9 B / 21 |
| 通常停止を受領して無視 | PASS | 24.501534 | 24.750437 | 24.755966 | 24.756506 | 200 / 9 B / 77 |
| 親子、通常停止を無視 | PASS | 24.508382 | 24.751464 | 24.757410、24.757421 | 24.758199 | 200 / 9 B / 77、77 |
| 境界前に本文受信完了 | PASS | — | — | 24.216125 | 24.221445 | 200 / 20 B / 0 |
| 25秒時点で停止を発火 | **FAIL** | 25.002293 | — | 25.015539 | **25.016008** | 200 / 9 B / 21 |

接続待ちでは IPC の CONNECT 応答を止め、読取側は接続期限を検知して終了コード20を返した。HTTP GET は発行されなかった。本文待ちでは部分応答9バイトを回収し、正常本文として受理しなかった。10件すべてで保持したハンドルから終了コードを取得し、Job の稼働数ゼロと治具スレッドの終了を確認した。25秒発火対照も残存ゼロで回収されたが、回収上限を16.0077 ms超過したため FAIL とした。正式試行のコマンド終了コード0は、意図した FAIL を含めて事前期待と一致したことを示す。

## 能力別の判定

| 能力 | 判定 | 範囲 |
| --- | --- | --- |
| 操作 | 限定 PASS | IPC で HTTP status を直接パース。200の本文全バイト一致と404の空本文を確認 |
| 制御 | 限定 PASS | 24.50秒停止・24.75秒強制停止の予算ありで25秒以内の親子回収を観測。25秒発火条件自体は FAIL。恒常的な25秒保証は UNKNOWN |
| 監査 | 保存・自己読戻し PASS、独立照合 NOT_TESTED | 原票、停止・回収ログ、原バイト、事前ロック、公開要約を照合し、承認済み案件領域に保存 |

TCP/TLS 経路での接続期限を含む試験は BLOCKED。Codex 本体と GitHub 接続サービス内部の停止は今回の観測対象外で、NOT_TESTED。Stage 1-A の REAL adapter、共通ベンチマークの登録実測、第3実験も NOT_TESTED。

## 証拠と提出

- [公開観測要約](observations-summary.json)には時刻、結果、応答のサイズとハッシュ、元ファイルのハッシュを掲載した。完全原票と停止・回収ログはローカル作業領域に保持している。
- Level 2 原証拠 ZIP は **93,788 B**、SHA-256 `450aeeb2f123db9345d29c0be73ac6cc787e0dcd09d8cfb0e77c1035c9f1ea0b`。所有者が承認した案件専用領域に 2026-11-25 16:21:11.4686468 UTC に新規保存し、同じ担当が 16:21:11.606099 UTC に保存先から読み戻した。原 ZIP と全バイト一致し、保存版の90エントリの集合、全 CRC、内部 manifest のサイズと SHA-256 は一致。保存受付は案件領域に記録。独立再取得は NOT_TESTED、ACL 全体・長期保持保証は UNKNOWN。中央規約の v0.3.0 への案件移行承認は確認できず、v0.2.0 の Level 2 契約を判断根拠とした。 [中央保全規約 v0.2.0](https://github.com/tetsujisugimori-coder/git-preservation-gate/blob/79740b1dfb3d9990094f6b847dcf619fc6edcb61/docs/v0.2.0/policy.md) [v0.3.0 採用 PR](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/25)
- GitHub の固定 HEAD と tree、実バイトの読戻しと正式 CI の結果は提出後に確認する。現行の Stage 1-A オフライン CI の自動発火パスに、このディレクトリは含まれない。
- [独立レビュー依頼](REVIEW-REQUEST.md)を使用して、期限と回収の判定の独立再現、承認済み保存先からの原証拠の独立取得を依頼する。回収予算の採用と TCP/TLS を使う実行候補の承認は、登録実測の前に個別に判断する。

根拠となる Windows API の契約。 [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) [Microsoft Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
