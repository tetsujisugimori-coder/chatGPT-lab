# ChatGPT研究対象・実行環境・比較基準（Stage 0 / v0.1 案）

- 作成日: 2026-11-18 JST
- 状態: **提案 / 独立レビュー未実施 / 研究用規約の正式受入前**
- 対象: `chatGPT-lab` および横断実験の比較・報告
- 議論の起点: このプロジェクトの2026-11-17〜18の会話
- 関連: [Issue #5](https://github.com/tetsujisugimori-coder/chatGPT-lab/issues/5)、既存実験001/002
- 目的: 「ChatGPTに何ができるか」という主張の対象と証拠の帰属先を揃える。製品全体、個別モデル、クライアント、ツール、外部サービスを混同しない。

## 1. 研究上の定義

**ChatGPT**: OpenAIが提供する対話型AI製品。利用者が接するChatなどの機能、選択・利用されるAIモデル、利用可能な実行機構や接続機構などを含む製品として扱う。**ChatGPT = 特定の1モデル**、または**ChatGPT = すべての接続先の能力**とは定義しない。

**Chat**: 主に会話する利用形態。モデルによる回答と、接続ツールの結果を分けて観測する。

**Work**: 継続した手順・成果物の作成などを扱う利用形態。本規約では `Work Cloud` と `Work Local` を別区分とする。

**Codex**: ソフトウェア開発向けの利用形態。ローカル実行（CLI/IDE/デスクトップ等）とクラウド実行を区別する。ChatGPT製品画面からの導線だけで実行場所を決めない。

**八兵衛（dot）**: ChatGPT内のdotとして設定された継続的な作業の依頼先。dot自身のクラウドコンピューターでの処理、承認されたローカルPCでの処理、Work/Codexなどに委任した処理を分ける。依頼受付と実実行の同一性を仮定しない。

**モデル**: 回答生成や推論に使われるモデル。画面表示と実際に使用されたモデルが同じと確認できる範囲を明記し、証明できない場合はUNKNOWN。

**ツール・プラグイン・MCP・接続アプリ**: モデルの外で情報取得や操作を行う経路。表示上の接続可能、認可済み、呼出し成功、結果の正しさは別々の事実。

## 2. 概念上の6層（内部実装図ではない）

| 層 | 分類 | 例 | 分離する理由 |
|---|---|---|---|
| L1 | 製品・クライアント | ChatGPT Web/desktop/mobile | UI機能と導線の差 |
| L2 | 利用形態 | Chat / Work / Codex / dot | 課題を誰に依頼したか |
| L3 | モデル | 表示されたモデル・実際のモデル（不明可） | 推論能力の帰属 |
| L4 | 実行・制御環境 | ローカル端末/クラウド環境/委任 | ファイル・ブラウザ・OS・承認境界 |
| L5 | 接続機構 | 内蔵機能/プラグイン/MCP/API/ブラウザ | 操作の具体的経路 |
| L6 | 外部システム | GitHub/Drive/外部AI等 | 応答する相手と真実源 |

この6層は**観測結果を分類する概念モデル**であり、OpenAIの非公開内部構造を確定するものではない。利用形態と製品導線は実際には交差するため、階層として排他的だとは扱わない。

## 3. 初期の10比較ID（製品公式エディション名ではない）

| 実験ID | 利用形態 | 起動クライアント | 実行先（設計上の区別） |
|---|---|---|---|
| CHAT-WEB | Chat | Web | 観測して記録。自動でcloud/local認定しない |
| CHAT-DESKTOP | Chat | desktop | 同上 |
| CHAT-MOBILE | Chat | iOS/Android | 同上。OS種別を補記 |
| WORK-CLOUD-WEB | Work Cloud | Web | cloud |
| WORK-CLOUD-DESKTOP | Work Cloud | desktop | cloud |
| WORK-CLOUD-MOBILE | Work Cloud | iOS/Android | cloud |
| WORK-LOCAL | Work Local | desktop | local（利用可否・使用PCは実測） |
| CODEX-LOCAL | Codex Local | CLI/IDE/desktop | local。起動UIも記録 |
| CODEX-CLOUD | Codex Cloud | 対応する起動面 | cloud。起動面は別記 |
| DOT | 八兵衛（dot） | dotへの依頼面 | 自身のcloud/local/委任先を別記 |

このIDは開始時の**分類ラベル**であり、実行先の証拠ではない。表示・利用可否はプラン、ワークスペース、権限、リリース時期、OSなどで変わり得る。未提供を実行失敗とは見なさない。Work Localがデスクトップで実行された場合でも、メッセージ等の情報がクラウドに保存され得ることと区別する。

### 2軸以上で記録する原則

1. `client_surface`: Web/desktop/iOS/Android/CLI/IDE/その他/UNKNOWN
2. `selected_experience`: Chat/Work/Codex/dot/UNKNOWN
3. `execution_site`: local/cloud/mixed/UNKNOWN（実測できる範囲）
4. `executor`: 実際の処理主体、特定できなければUNKNOWN
5. `delegate_chain`: 依頼元→委任先の識別と証拠、未確認ならUNKNOWN

**例**: DesktopからWork Cloudを起動した場合は `client_surface=desktop` と `execution_site=cloud` の両方を残す。「desktopだからlocal」としない。dotがCodex Cloudへ委任した実行はDOT単独成功として数えず、「dotによる依頼・委任」と「Codex Cloudによる実処理」を別評価する。

## 4. 共通実験の最低記録項目

| 分類 | 必須項目 |
|---|---|
| 識別・版 | `protocol_id`, `protocol_version`, `run_id`, `UTC/JST日時`, `plan_commit` |
| 実行の帰属 | 10 ID、client_surface、OS/アプリ版（取得できたとき）、selected_experience、execution_site、executor、delegate_chain、model_display、model_verified |
| 権限と操作 | 対象repo/commit/tree、ツール名・経路、読取/書込/外部送信の区別、承認範囲、実際の操作、リトライとtimeout |
| 観測と照合 | 成功・失敗原票、サイズ/SHA-256/Git blob（適用時）、終了状態、外部応答と別経路比較、実測と合成対照の分離 |
| 保存と審査 | 証拠の保存先種別、原物の再取得可否、独立担当の実行範囲、未実施・限界・残余リスク |

機密情報・内部URL・認証トークン・個人情報をPublic repositoryに転載しない。非公開の所在や証拠は本人認可された保管先に残し、公開には必要最低限の照合情報のみ載せる。

## 5. 能力帰属と判定

- `PASS`: 当該主体・環境・対象・操作・時刻・証拠の範囲で、事前に定義した成功条件を満たした。
- `FAIL`: 定義済みの検証を実施し、期待条件を満たさなかった。
- `BLOCKED`: 権限・保存・環境などにより、要求した検証を完遂できなかった。
- `NOT_TESTED`: 対象の操作・検査を実施していない。
- `UNKNOWN`: 観測したが確定できない属性や、裏付け不足の事項。

ツール呼出しの成功 ≠ モデル自身の能力、保存受付 ≠ 再取得一致、GitHub APIの応答 ≠ GitHub以外への一般化、複数の取得経路 ≠ 独立した真実源、担当枠の分離 ≠ 別基盤での独立性、通信往復時間 ≠ モデル推論速度、CIの不存在 ≠ CI PASSとする。

## 6. 複数リポジトリで同一課題を比較する規約

**chatGPT-lab**: 共通プロトコルの正本、採点方法、対象範囲、比較表、限定結論を管理。

**Codex-Cloud-Lab**: Codex Cloudによる実行と、担当リポジトリ内の原票・差分・証拠を管理。

**Hachibei-Lab**: 八兵衛（dot）による実行と、委任有無・実処理先・原票・証拠を管理。

- 共通実験の指示文、入力fixture、期待値、採点器、制限時間、再試行規則、許可権限を`protocol_version`とSHAで固定する。
- repoが異なる場合、HEAD SHAが等しいと期待しない。比較対象となるfixtureの内容・tree・設定差分、AGENTS.md、承認権限を照合・台帳化する。
- 各担当は原票をそれぞれのrepoに置き、chatGPT-labは証拠への参照と比較結論を保持。偽装・上書き・過去実験の遡及変更をしない。
- 初期課題は非秘密の固定GitHub読取を候補とする。読取と書込、操作能力とアクセス権、各形態の起動可能性を混同しない。
- 比較結果は「比較可能 / 条件差あり / 比較不可」を理由付きで分類し、成功率・時間・再現性だけでなく、権限制約・証拠品質・独立性も扱う。
- 単一の成功から他モデル、他モード、全クライアント、非公開データ、MCP全般、全環境への一般化をしない。

## 7. 研究の順序と既存記録

1. Stage 0: 本規約案の文書化・独立レビュー・反例チェック・限定受入。
2. Stage 1: 共通ベンチマークの計画と検査器設計（最初は読取のみ）。
3. Stage 2: Chat、Work Cloud/Local、Codex Local/Cloud、dotの個別実測。
4. Stage 3: 横断比較を経てファイル保存/再取得、接続、継続・委任を段階的に検証。

実験001/002は当時の対象版・主体・限定PASS/総合PARTIAL等の歴史的記録を保持し、この分類への後付けで実行したことにしない。第3実験「ファイル生成・保存・再取得」はStage 0のレビュー後に着手する案である。Stage 0文書提出は、モデルやWork、Codex、dotの機能検証を新たに実施したことを意味しない。

## 8. 未確定事項・レビューの観点

- 実験IDの粒度（Windows/macOS、iOS/Android、CLI/IDE等の下位分類）は必要に応じて増やす。既存IDの意味は黙って変えない。
- クライアントが実際に使用したモデルの厳密な同一性、dot委任内部の全経路、Cloud/Local混在の切り分けは観測できない場合UNKNOWNを保持する。
- クライアント差と実行場所差を混同していないか、別repoの設定差を比較結果のバイアスとして記録しているかを独立レビューする。
- Stage 0は**文書範囲のみ**。実装・実測・CI・独立レビュー・証拠保存のPASSはそれぞれ別記録とする。

## 9. 公開参考資料（2026-11-18閲覧）

- [ChatGPT Work and Codex（OpenAI Help Center）](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex): Work Cloud/Local、起動クライアント、Codex Localの区分。
- [Agent security and local work sync in ChatGPT](https://help.openai.com/ja-jp/articles/20001548-agent-security-and-local-work-sync-in-chatgpt): ローカル・クラウド作業の切替条件と同期の制約。
- [Getting started with your dot](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot): dot自身のクラウド・ローカルへのアクセス・Codexへの委任。
- [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes): Chat/Work/Codexの位置づけ。

以上の公式資料は公開仕様の根拠であり、個々の実行経路・契約・アクセス権・内部実装を実測した証拠ではない。
