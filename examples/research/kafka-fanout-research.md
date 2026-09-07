# Research

## Article Thesis

Our Kafka consumer lag disaster was caused by unbounded fan-out, not
broker capacity — and the fix (bounding per partition key) only works
because of how Kafka's ordering guarantee is actually scoped.

## Research Questions

- What exactly does Kafka guarantee about ordering (official docs)?
- Under what conditions is per-key bounding safe for downstream consumers?
- What are published post-mortems about hot-key/consumer-lag incidents?

## Sources

### Source 1
Title: Apache Kafka Documentation — Message Ordering
URL: https://kafka.apache.org/documentation/#ordering
Authority: Tier 1 — Official documentation, standards, primary research, academic papers
Date accessed: 2026-09-05
Claims:
- Ordering is guaranteed only within a partition (VERIFIED)
- Keys map deterministically to partitions with the default partitioner (VERIFIED)
Confidence: High — all attributed claims verified this session.

### Source 2
Title: Our internal incident review doc (private)
Authority: Tier 2 — Engineering blogs, reputable technical documentation, professional editorial bodies
Date accessed: 2026-09-05
Notes: Timeline, error-rate graph, and the 2.3s→180ms staging benchmark
come from this doc. Numbers are the author's own measurements.

## Contradictions

- None found between official docs and our observed behavior; the surprise
  was our own assumption about per-key volume uniformity.

## Statistics

- 40x normal traffic (measured, from incident dashboard)
- p99 2.3s → 180ms after bounding (our staging benchmark, replayed traffic)
- Lag recovery within 40 minutes of deploy (measured)

## Claims Requiring Verification

- "4,000 events per second under normal traffic" — confirm from metrics
  dashboard before publishing.

## Potential Examples

- The bounded-fan-out code snippet (real implementation, simplified).
- The "wrong call" moment: scaling brokers while the real problem was
  application-level.
