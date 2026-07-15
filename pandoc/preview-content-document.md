---
title: "Incident Response Runbook"
author: "TenX Protocols · Platform Engineering"
date: "v1.0 — Confidential — Last updated 2026-06-30"
doctype: document
---

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

## Purpose

This runbook covers first response for a production incident: how to
declare severity, who to page, and the immediate stabilization steps
before a full postmortem is written.

## Escalation path

1. On-call engineer acknowledges the page within 5 minutes.
2. SEV-1/SEV-2 incidents page the on-call lead automatically.
3. The lead decides whether to open an incident channel and pull in
   additional responders.

## Immediate steps

- Confirm the blast radius: which systems, which customers.
- Mitigate first, root-cause later — roll back or fail over before
  investigating why.
- Post a status update in the incident channel every 15 minutes while
  the incident is open.

## Recovery verification

- Error rates and latency back to baseline for at least 15 minutes.
- No open pages or active alerts tied to this incident.
- Customer-facing status page updated to resolved.

## After the incident

Open a postmortem using the Postmortem template within one business day.
This runbook only covers the response itself, not the retrospective.
