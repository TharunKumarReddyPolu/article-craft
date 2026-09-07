---
title: ""
subtitle: ""
audience: ""
article_type: system-design
platform: medium
ai_assistance: assistive
---

# [The system + the hard constraint that shaped it]
**[Subtitle: the trade-off at the heart of the design]**

<!-- Intro: the problem in one paragraph. Why it's interesting. Who this is
for. -->

## Requirements

**Functional:** what the system must do (bulleted, concrete).
**Non-functional:** scale, latency, availability, consistency targets —
**as explicit numbers or labeled assumptions.**

## Constraints and assumptions

<!-- Traffic, data size, team size, budget. Label every assumption as an
assumption. "Assume 10k writes/s (typical for this class of system)" — the
label is what keeps this honest. -->

## High-level architecture

<!-- Diagram (image or ASCII). Components + responsibilities only; no
deep-dive yet. -->

## Deep dive: data model & storage

<!-- Schema choices, why this store, what the alternatives cost. -->

## Deep dive: messaging & caching

<!-- Queues, delivery guarantees, cache invalidation strategy. -->

## Failure handling

<!-- What fails first. What happens on partition, on dependency loss, on
thundering herd. Recovery + observability: how would you KNOW it's failing? -->

## Trade-offs and rejected alternatives

<!-- For each major decision: what you chose, what you rejected, why. This
section is where credibility lives. -->

## Security and scaling notes

<!-- AuthN/Z boundaries, multi-tenancy, what breaks at 10x/100x. -->

---

Checklist before publishing:
- [ ] Assumptions labeled as assumptions
- [ ] No fabricated benchmark numbers
- [ ] Failure handling and observability covered
- [ ] Rejected alternatives documented
