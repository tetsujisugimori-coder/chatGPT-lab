# ChatGPT研究対象・実行環境・比較基準（Stage 0 / v0.2 補訂案）

- 作成日: 2026-11-18 JST（v0.1）
- 更新日: 2026-11-18 JST（v0.2 補訂）
- 状態: **補訂案 / v0.1独立レビュー実施済み / v0.2独立再審査未実施 / 文書限定受入前**
- レビュー履歴: [v0.1独立レビュー](https://github.com/tetsujisugimori-coder/chatGPT-lab/pull/6#pullrequestreview-5945761782)は総合PARTIAL、P2-01/P2-02・P3-01未閉鎖、文書受入NO。元の「独立レビュー未実施」は**v0.1作成時点**の状態であり、v0.2の現状態を表さない。
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

### P2-01：開始時のIDが未確定の場合

- 必須の `comparison_id` は上表の10 ID、または**特別値 `UNKNOWN`** のいずれかとする。`UNKNOWN` は11番目の製品分類ではなく、判定保留の記録値であり、実行失敗（FAIL）でも未実施（NOT_TESTED）でもない。
- 開始時に利用形態やクライアントを確認できず10 IDを一意に決められない、または「Work」しか判明せずCloud/Localを識別できない場合は、推定で割り当てず `comparison_id=UNKNOWN` とする。`comparison_id_reason`（どの識別情報が欠けるか）と `comparison_id_candidates`（根拠ある候補、または `UNKNOWN`）を必須で記録し、`comparison_id_status=UNRESOLVED` とする。
- 一意に識別できた開始時IDは `comparison_id_status=CONFIRMED` とし、根拠（画面・操作・ログ等の `comparison_id_evidence`）を残す。**実行先が観測でUNKNOWNでも、開始時IDが確定できるとは限らず、その逆も同様**。IDの確定と実行場所の確定を別々に審査する。
- 開始後の画面切替、cloud/local混在、委任を理由に**開始時IDを無言で上書きしない**。`initial_client_surface` と `current_client_surface`、各処理区間の `segment_id`・時刻・クライアント・観測実行先・実処理主体・委任証拠を記録する。証拠のない区間はUNKNOWNであり、推定したmixedを確定値として扱わない。
- 後から開始時分類の新証拠が出た場合、元値・新値・根拠・変更者・変更時刻を**追記型の訂正履歴**に記録し、元原票を遡及改竄しない。分類の解決まで当該IDを必要とする能力別集計・順位付けは保留し、別途「帰属未確定」と明記する。

### 2軸以上で記録する原則

1. `client_surface`: Web/desktop/iOS/Android/CLI/IDE/その他/UNKNOWN
2. `selected_experience`: Chat/Work/Codex/dot/UNKNOWN
3. `execution_site`: local/cloud/mixed/UNKNOWN（実測できる範囲）
4. `executor`: 実際の処理主体、特定できなければUNKNOWN
5. `delegate_chain`: 依頼元→委任先の識別と証拠、未確認ならUNKNOWN

**例**: DesktopからWork Cloudを起動した場合は `client_surface=desktop` と `execution_site=cloud` の両方を残す。「desktopだからlocal」としない。dotがCodex Cloudへ委任した実行はDOT単独成功として数えず、「dotによる依頼・委任」と「Codex Cloudによる実処理」を別評価する。

補足：`execution_site=mixed` は同一対象run内でlocal/cloud双方を示す証拠が揃う場合の観測値であり、**不明だからmixed**とはしない。開始時の `comparison_id`、現在の利用面、区間別の実行証拠は独立したフィールドとする。

## 4. 共通実験の最低記録項目

| 分類 | 必須項目 |
|---|---|
| 識別・版 | `protocol_id`, `protocol_version`, `run_id`, `UTC/JST日時`, `plan_commit` |
| 実行の帰属 | `comparison_id`（10 IDまたはUNKNOWN）、`comparison_id_status`、`comparison_id_evidence`、UNKNOWN時の`comparison_id_reason`・`comparison_id_candidates`、`initial_client_surface`、`current_client_surface`、区間別記録、client_surface、OS/アプリ版（取得できたとき）、selected_experience、execution_site、executor、delegate_chain、model_display、model_verified |
| 権限と操作 | 対象repo/commit/tree、ツール名・経路、読取/書込/外部送信の区別、承認範囲、実際の操作、リトライとtimeout |
| 観測と照合 | 成功・失敗原票、サイズ/SHA-256/Git blob（適用時）、終了状態、外部応答と別経路比較、実測と合成対照の分離 |
| 保存と審査 | 証拠の保存先種別、原物の再取得可否、独立担当の実行範囲、未実施・限界・残余リスク |
| 横断比較（実施する場合） | 事前固定した `comparison_purpose`・`metric`・`required_equivalences`（同値条件）・`allowed_deviations`（許容差）・`stop_conditions`・`protocol_sha`、両runの差分証拠、`comparison_decision`・`decision_reason`。比較を実施しない場合はNOT_TESTEDとする |

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

### P2-02：比較可否の決定規則（各比較ペアに適用）

1. **結果を確認する前に** `comparison_purpose`（問い）、`metric`（評価指標）、`required_equivalences`（その問いの成立に不可欠な同値条件）、`allowed_deviations`（比較可能のまま容認する差と数量的な許容幅）、`stop_conditions`（証拠欠落・条件違反時の停止条件）をプロトコル版・SHAとともに固定する。固定後に変更するなら**別の比較版**として扱い、旧版を残す。
2. 目的は少なくとも `descriptive`（異なる条件を記述し相違を明らかにする）と `controlled-ranking`（同条件の能力・性能順位）を区別する。たとえば `required_equivalences` にfixture内容、操作権限、AGENTS.md、通信条件、再試行設定、時間測定境界などのうち目的上必要なものを具体的に列挙する。すべてを無条件で同一必須にするわけではないが、重要性の判断を**事後変更**しない。
3. 判定の優先順位：入力検査で目的・指標・同値条件定義などの事前必須項目が欠けた場合は **`protocol_validation=REJECTED`** とする。比較判定を求めた試行では **`comparison_decision=比較不可`（理由：`MISSING_PREDECLARED_FIELD`）** を返し、欠落値を自動補完しない。入力検査を通過した比較でも、必須同値条件に不一致、重要な証拠不足、事前停止条件に抵触、差の影響不明の場合は **比較不可**。次に **条件差あり**＝不可の条件がなく、重要な差を根拠付きで列挙でき、その差を含めた記述比較が事前目的で許される場合（差を無視した順位付けは不可）。残る **比較可能**＝必須条件が証拠で同値と確定し、その他の差が事前許容幅内に収まる場合。各判定には適用規則と両側の証拠参照を記録する。
4. `controlled-ranking` で順位に影響する権限・設定・ネットワーク等の必須条件が異なる場合は**比較不可**。`descriptive` で、その差を観測でき、目的が同じ課題の条件差の記述であり、必要な最低限の共通条件を満たす場合に限って**条件差あり**。この場合も「同一条件でAが優秀」とは結論しない。
5. 比較未実施は判定3値のいずれかに擬装せず**NOT_TESTED**。分類IDがUNKNOWNなら、そのIDに依存する比較は**比較不可（理由：主体帰属未確定）**であって、IDが確定したことにしない。目的上IDが不要な記述比較でも、帰属未確定を明記し、ID別順位に転用しない。

**固定反例の期待境界**（v0.1レビュー指摘を補訂するための規則上の予測であり、旧40ケース原票の再実行結果ではない）：

| ケース | 目的・観測条件 | v0.2での期待 |
|---|---|---|
| C25 / C26 | 権限・AGENTS.md・ネットワークに差がある同一2run、目的が`descriptive`。共通課題と差の実体を立証 | `条件差あり`（差が不明/必要共通条件欠落なら`比較不可`） |
| C25 / C26 | 同一2run、目的が`controlled-ranking`で差のある項目が必須同値条件 | `比較不可` |
| C32 | 開始時の選択形態が未確認 | `comparison_id=UNKNOWN`、理由・候補・保留を記録 |
| C39 | Workまでは確認、Cloud/Localは未確認 | `comparison_id=UNKNOWN`、候補と理由を記録。勝手にWORK-CLOUD等へ固定しない |
| M10 | 比較目的が欠落した変異入力 | `protocol_validation=REJECTED`、比較判定を要求した場合は`comparison_decision=比較不可`（`MISSING_PREDECLARED_FIELD`）。既定目的の補完は禁止 |
| C31 / M09 | 開始時IDは保持し、mixedの観測値をlocalに置換したら改竄として拒否 | 開始時IDの保持自体はPASS対象。mixedからlocalへの無根拠置換は不受理 |

上記は**文書上の期待規則**。同じC25/C26でも、事前に固定した目的が `descriptive` か `controlled-ranking` かによって判定が変わる。40分類ケースと10変異の元入力一式を取得して同条件で再採点するまで、v0.2で「40/40 PASS」「10/10拒否」等と報告しない。検査器の実動作は別試験とする。

## 7. 研究の順序と既存記録

1. **Stage 0レビューゲート**: 文書案・独立レビューと反例点検を実施し、指摘・未確定事項を記録。レビュー**完了だけでは受入にならない**。
2. **Stage 0文書受入ゲート**: P2閉鎖、必要な反例再審査、独立性・証拠限界を確認した後に**別途**文書限定受入とマージ可否を決定。受入前はDraft・HOLD。
3. **Stage 1計画ゲート**: 受入済み規約に基づく共通ベンチマーク計画と検査器設計（最初は読取のみ）。計画書の作成と実測開始を混同しない。
4. **実測開始ゲート**: Stage 1のプロトコル・fixture・権限・停止条件・承認・証拠保全方法を固定し個別承認。通過した対象に限ってStage 2でChat/Work/Codex/dotの実測を開始。
5. **Stage 3ゲート**: 横断比較を経てファイル保存/再取得、接続、継続・委任を段階的に検証。第3実験は別件として**文書受入・実測開始ゲートの両方**を満たすまでは開始しない。

実験001/002は当時の対象版・主体・限定PASS/総合PARTIAL等の歴史的記録を保持し、この分類への後付けで実行したことにしない。第3実験「ファイル生成・保存・再取得」はレビューが終了しただけでは開始しない。Stage 0の文書受入を確認し、必要な実験計画・独立した実測開始承認を経てから着手する案である。Stage 0文書提出は、モデルやWork、Codex、dotの機能検証を新たに実施したことを意味しない。

## 8. 未確定事項・レビューの観点

- 実験IDの粒度（Windows/macOS、iOS/Android、CLI/IDE等の下位分類）は必要に応じて増やす。既存IDの意味は黙って変えない。
- クライアントが実際に使用したモデルの厳密な同一性、dot委任内部の全経路、Cloud/Local混在の切り分けは観測できない場合UNKNOWNを保持する。
- クライアント差と実行場所差を混同していないか、別repoの設定差を比較結果のバイアスとして記録しているかを独立レビューする。
- Stage 0は**文書範囲のみ**。実装・実測・CI・独立レビュー・証拠保存のPASSはそれぞれ別記録とする。v0.1文書について独立レビューは実施済みだが**PARTIAL・文書受入NO**。v0.2の再審査・恒久保全は未実施であり、前回の証拠ZIP照合を新しい版の保全証明へ転用しない。

## 9. 公開参考資料（2026-11-18閲覧）

- [ChatGPT Work and Codex（OpenAI Help Center）](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex): Work Cloud/Local、起動クライアント、Codex Localの区分。
- [Agent security and local work sync in ChatGPT](https://help.openai.com/ja-jp/articles/20001548-agent-security-and-local-work-sync-in-chatgpt): ローカル・クラウド作業の切替条件と同期の制約。
- [Getting started with your dot](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot): dot自身のクラウド・ローカルへのアクセス・Codexへの委任。
- [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes): Chat/Work/Codexの位置づけ。

以上の公式資料は公開仕様の根拠であり、個々の実行経路・契約・アクセス権・内部実装を実測した証拠ではない。
