# Standalone reproduction check

- Tested UTC: 2026-09-25
- Tested archive SHA-256: `194c3608c4659c370af5330d281fd94ba162d85f70714f961a899d7e50dc1f58`
- Test: extracted `reproducibility_bundle.zip` into a clean directory with no project virtual environment and ran `make all`.
- Result: PASS.
- The clean build installed the pinned environment, ran sample-size analysis, generated and analysed synthetic validation data, verified 22 references and 30 persisted source records, regenerated the manuscripts/figures, passed 23 QC checks, and rebuilt both archives.
- Exact comparison result: calculated numeric CSV/JSON outputs and the blinded-manuscript text were identical to the canonical project outputs.

This check validates software reproducibility only. Synthetic outputs are not clinical observations, and private retrospective source files are intentionally excluded.
