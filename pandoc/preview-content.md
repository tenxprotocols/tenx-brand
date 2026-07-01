---
title: "Access Control Policy"
author: "TenX Protocols"
date: "v1.0 — Confidential — Last updated 2026-06-30 — PREVIEW DOCUMENT, not an approved policy"
---

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

## Purpose

This policy defines how access to company systems and data is granted,
reviewed, and revoked. It exists to keep the blast radius of a compromised
account small, and to give auditors a clear, evidence-backed answer to
"who can touch what, and why."

## Scope

This policy applies to every employee, contractor, and automated service
account with access to production systems, customer data, or internal
tooling. It does not cover physical access to office space, which is
governed separately.

### Principle of least privilege

Access is granted based on role, not tenure or convenience. A new hire on
the platform team gets read access to staging logs on day one; write
access to production infrastructure requires a specific, time-bound
request approved by their manager and a member of the security team.

### Default-deny

Systems default to no access. Every grant is a deliberate, logged action —
never an inherited default from a broader group unless that group's own
access was itself deliberately scoped.

## Access review cadence

| System | Review frequency | Reviewer | Evidence |
|---|---|---|---|
| Production AWS accounts | Quarterly | Security lead | Signed access review checklist |
| Google Workspace admin | Quarterly | IT lead | Signed access review checklist |
| Source control (org owners) | Quarterly | Engineering lead | Signed access review checklist |
| Customer data warehouse | Monthly | Data lead | Signed access review checklist |

## Offboarding

When an employee or contractor's engagement ends, access is revoked the
same business day. This includes:

- SSO/identity provider account disabled
- All third-party SaaS integrations tied to their identity revoked
- Any shared credentials they had knowledge of rotated
- Physical badge and hardware returned or remotely wiped

## Exceptions

Any deviation from this policy requires written approval from the
security lead, with a documented business justification and an expiry
date. Standing exceptions are reviewed at the same cadence as regular
access reviews above.
