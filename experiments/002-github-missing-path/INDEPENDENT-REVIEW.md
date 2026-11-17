# Independent review: chatGPT-lab experiment 002

Reviewer: separate assigned subagent; same cloud environment and inherited task context. No network remeasurement, GitHub mutation, or source edit by reviewer.

## Initial finding: P2-R1 (LIMITED_CLOSED after fix/recheck)

The verifier trusts normalized route attribution without validating all corresponding original fields. With each fixture manifest renewed, the following four mutations are accepted as record integrity PASS / network experiment PASS:

1. A-N raw.tool changed from fetch_file to fetch_blob.
2. A-N raw.tool removed.
3. B-N --request GET changed to POST in raw command and normalized command.
4. B-N raw.source changed to a different provider URL while normalized source remains fixed.

See additional-results.json and retained fixtures. These are synthetic record-contract counterexamples, not evidence of wrong tools/URLs in the actual measurement. Require raw tool equality, B GET contract, and raw source equality. Add/recheck the same cases.

## Direct checks completed
- Original 002 verify and 001 verify succeed.
- Author's original 21-case suite repeated: 21/21 expected outcomes.
- 002 PLAN exact-byte equality with saved premeasurement GitHub readback, SHA-256 4b1364c119a1155616487cc840290bf93327b0a7836e56979d7869e99d1b9e16.
- target-tree.json exactly matches saved original tree response; complete 12-entry tree, truncated=false, missing target absent.
- Six raw response/metadata files exactly match initial local measurement evidence.
- Both normal payloads are 2237 bytes and recorded hashes/blob verified by the verifier. Error payloads are separated from target file bytes, and A transport status is correctly left unavailable rather than inferred from error text.
- 001 PLAN, RESULTS, observations, and historical P2-regression-results are byte-identical to the prior stage snapshot.
- 001 source changes limited to exact 002 subtree separation, associated fixture-manifest scope, and resulting manifest updates. Other hidden files/required files/hash checks remain.
- Fixed public two-path scope and absence of claims about ordinary ChatGPT, models, private rights, MCP generally are maintained.

## Limitations
Submission fixed-HEAD readback, final CI inventory and Library custody are not reviewed here yet. No independent fresh network measurement. Same environment does not prove information-route exclusivity.

## Fixed-version recheck

P2-R1 is LIMITED_CLOSED in the saved-record attribution contract. The same four retained counterexamples were rerun with the fixed verifier; all now reject with exit 1 (RED→GREEN), while the valid original remains record integrity PASS / experiment PASS. See fixed-additional-results.json. The expanded author suite was independently rerun: 25/25 expected outcomes, including valid UNKNOWN records and rejection of false PASS.

The existing 001 110-case suite was also independently rerun: old verifier 66/110 and adjusted current verifier 110/110, preserving the prior repair contract. Full records remain under review/compatibility/results.json.

Final reviewed source identities are in reviewed-files.json. Limited evidence/code review PASS; experiment conclusion PASS only for these two paths/routes/environment. Overall research remains PARTIAL. No new P0/P1/P2 found in this reviewed scope. No merge or Draft change performed. Submission and custody checks remain distinct and require their own verified records.
