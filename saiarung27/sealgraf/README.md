# Sealgraf for Dify

Spend approval for AI agents, as Dify tools. An agent workflow checks a
purchase **before** buying; above a limit the owner set, the owner approves
on their own Sealgraf surface; after the purchase, the completion evidence
is sealed into a receipt neither side can rewrite.

## Tools

| Tool | What it does |
|---|---|
| `check_permission` | Ask before a purchase. Returns `allow` (with a single-use decision token), `deny`, or `needs_human_approval` (with the preauth id to resume with). |
| `claim_decision_token` | After the owner approves an ask, claim the single-use decision token with the same API key that ran the check. |
| `complete_purchase` | Submit completion evidence after the purchase; returns the sealed receipt. |
| `get_receipt` | Read back state. Give exactly one id: a `preauth_id` (reads `GET /v1/preauthorize/{id}` — the check's current state and decision) or a `receipt_id` (reads `GET /v1/receipts/{id}` — the sealed receipt). |

## Setup

1. [Get your Dify key](https://sealgraf.com/app/?integration=dify&source=dify_marketplace#/connect/dify/1). Sign in or create an account, set Dify's spending limits, and copy the key.
2. In Dify, install Sealgraf and paste that key into **Sealgraf API Key**. Keep **Sealgraf Base URL** at its default, then save.
3. [Download the first-check workflow](https://sealgraf.com/app/templates/dify-first-check.yml). In Dify Studio, choose **Import DSL file**, select the downloaded file, and choose your saved Sealgraf credentials in the **Check permission** node.
4. Run with the default sample amount of 100 minor units ($1 for a USD limit), or enter another amount. Read the decision and its check ID in the output. Category and amount must match your own configured limits.

This workflow creates one real permission check. An allowed check can temporarily reserve budget, and a check above your approval threshold can create a pending approval. It stops at the decision and has no payment or completion node. A receipt is produced only after a real completed purchase is reported.

Credential validation uses the authenticated setup endpoint. Older self-hosted Sealgraf versions fall back to a receipt-list read. Validation does not create a purchase check.

## The spend loop

```
check_permission ── allow ──────────────► complete_purchase ──► get_receipt
       │
       └─ needs_human_approval ─► (owner approves in Sealgraf)
                                 claim_decision_token ─► complete_purchase
       │
       └─ deny ─► do not buy
```

Amounts are always integer minor units (cents): $42.50 is `4250`.

## Chaining the tools in a workflow

The fields a later node needs — `preauth_id` from `check_permission`,
`decision_token` from `claim_decision_token` — are declared in each
tool's output schema, so they appear in Dify's variable picker. One
platform behaviour matters when you wire them: **Dify does not resolve
a direct tool → tool reference to a tool's JSON fields at workflow
runtime.** A downstream node wired straight to `check_permission`'s
`preauth_id` receives the literal selector text instead of the value,
and the call fails. (Verified live in a real Dify workspace,
2026-11-11.)

Insert a **Code node** between the tools to extract the value from the
upstream node's `json` output — code-node outputs resolve normally:

```
check_permission ─► Code: extract preauth_id ─► claim_decision_token
claim_decision_token ─► Code: extract decision_token ─► complete_purchase
```

Extract ID (input variable: the check node's `json`):

```python
def main(check_json):
    item = check_json[0] if isinstance(check_json, list) and check_json else {}
    return {"preauth_id": item.get("preauth_id", "")}
```

Extract Token (input variable: the claim node's `json`):

```python
def main(claim_json):
    item = claim_json[0] if isinstance(claim_json, list) and claim_json else {}
    return {"decision_token": item.get("decision_token", "")}
```

Wire `complete_purchase`'s `preauth_id` to the first Code node's
output and its `decision_token` to the second's. Tokens must always
travel by reference like this — a hand-copied token fails the
completion (`decision token does not match`).

## Failure behaviour

Fail closed. A network error, timeout, non-2xx response, or a malformed
response makes the tool raise an error — never anything an agent could
read as permission.

## Source repository

https://github.com/saiarung27/dify-plugins/tree/sealgraf-source-v0.1.0/saiarung27/sealgraf
