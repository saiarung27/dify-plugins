# Plugin Submission

## Plugin information

- **Author**: saiarung27
- **Plugin name**: sealgraf
- **Version**: 0.1.1
- **Source repository**: https://github.com/saiarung27/dify-plugins/tree/update-sealgraf-0.1.1/saiarung27/sealgraf
- **Contact**: support@sealgraf.com

## Submission type

- [ ] New plugin
- [x] Version update

## What changed

The `check_permission` category list now matches the production canonical set: 17 categories. Added **services**, **shipping** and **repairs** — production added these for business purchases, while the plugin's closed list still carried the original 14 and rejected those categories locally, before any API call. The version is bumped to 0.1.1 in the manifest, and the client's User-Agent string follows. Nothing else changes: endpoints, parameters, payment vocabularies, auth (X-API-Key) and response handling are identical to 0.1.0.

## Risk level

- [ ] Low risk
- [ ] Medium risk
- [x] High risk

Selected per the risk classification in docs/plugin-submission-requirements.md: the plugin handles financial data (purchase amounts, categories, counterparties) and the API base URL is a user-configured credential field. Details in the security notes below. Unchanged from the 0.1.0 submission.

## Required checks

- [x] I have read and followed the [Marketplace submission requirements](https://github.com/langgenius/dify-plugins/blob/main/docs/plugin-submission-requirements.md).
- [x] I have read and comply with the [Plugin Development Guidelines](https://docs.dify.ai/en/develop-plugin/publishing/standards/contributor-covenant-code-of-conduct).
- [x] I tested this plugin on Dify Community Edition and Dify Cloud, or documented any limitation below. Limitation: the 0.1.1 change is a closed-list data fix verified by the mocked contract suite (77 tests) run on the exact submitted package; the four tool flows are unchanged from 0.1.0, which was validated end-to-end on Dify Cloud (cloud.dify.ai). Version 0.1.1 itself has not yet been run on Dify Cloud or a self-hosted Community Edition instance.
- [x] The package contains runtime files, manifest, README, privacy policy, license, and icon; no development state.
- [x] The package does not contain secrets, local credentials, `.env` files, `.git` directories, virtual environments, caches, logs, or IDE files.
- [x] The package does not contain executables or bundled binaries. (None included.)
- [x] The plugin README includes setup steps, usage instructions, required APIs or credentials, connection requirements, and the source repository link.
- [x] The plugin includes `PRIVACY.md` or a hosted privacy policy, and `manifest.yaml` references it.
- [x] All user-facing text is primarily in English, with any localized README files following the [i18n guidance](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/multilingual-readme).

## Security and privacy notes

- Financial data: when a workflow runs a check, the purchase amount, category, counterparty name, and an optional description are sent to the Sealgraf API. Completed-purchase records and sealed receipts are stored by Sealgraf; PRIVACY.md describes what is collected and why.
- Credential handling: the Sealgraf agent API key is a Dify secret-input credential, sent only as an `X-API-Key` header to the configured Sealgraf base URL. It is never logged and never appears in tool outputs or error messages.
- User-controlled network destination: the base URL is a provider credential field (default `https://sealgraf.com`) so self-hosters can point the plugin at their own Sealgraf instance. Requests go only to four fixed API paths under that base URL, with enforced timeouts, and every failure is fail-closed: no approval is ever inferred from an error.
- Decision tokens are single-use, bound to the check that minted them and to the API key that created it, and are passed between tools by reference only (never printed or logged).
- No command execution, code execution, SQL, SSH/SFTP, filesystem operations, or browser automation.

## Local validation

- Mocked contract test suite: 77 passed, 0 failed (pytest), run on the exact submitted source; the structural test now pins the canonical 17 categories so the list cannot drift silently again.
- Packaged with the official Dify plugin CLI (dify-plugin v0.6.15); package contents verified after packaging (manifest at 0.1.1, all 17 categories present in the client and the tool YAML).
- Package sha256: 47dc391d78c4c026422e156855c5bfca6dc6d080146d0415608f72164723521c

## Reviewer notes

- To review against the live service: create a free Sealgraf account at https://sealgraf.com, set spending limits for an agent, create an agent API key, and enter it as the plugin credential (base URL default). A check inside the limits returns an instant allow; a check above the ask-limit stays pending until the owner approves it inside Sealgraf, and only then does the claim step succeed. That pause is the product working as intended.
- The only behavioral delta in 0.1.1: a `check_permission` call with category `services`, `shipping` or `repairs` is now accepted by the plugin and sent to the API (0.1.0 refused it locally as an invalid category).
