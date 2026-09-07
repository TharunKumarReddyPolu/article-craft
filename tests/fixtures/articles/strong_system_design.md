---
title: Designing a rate limiter for 50,000 requests per second
subtitle: The trade-offs between token buckets, sliding windows, and distributed counters
audience: backend engineers
article_type: system-design
ai_assistance: none
---

# Designing a rate limiter for 50,000 requests per second
**The trade-offs between token buckets, sliding windows, and distributed counters**

Our API gateway needed rate limiting at 50,000 requests per second across
12 nodes. The naive answer — "use Redis" — hides three hard trade-offs
that decide whether your limiter fails open or takes your API down with
it. This is how we chose, what we rejected, and where our assumptions
would break.

## Requirements

**Functional:** limit clients to N requests per window; support per-key
and global limits; return 429 with Retry-After.

**Non-functional:** p99 limiter overhead under 5ms; survive Redis loss
without failing the API; scale to 50,000 rps (assumption: sustained, with
2x bursts — this is a labeled assumption, not a measured figure).

## The three candidates

**Fixed windows with a Redis counter** (INCR + EXPIRE): simplest, but a
client can burst 2N at the boundary. At our traffic, boundary bursts were
measured by our SRE team at 1.8x the limit during load tests — real and
unacceptable for the billing API.

**Sliding window log**: exact, but memory grows with traffic per key.
For 50k rps and 100k active keys, the math (50,000 × 60 × 8 bytes) says
~24MB per minute of history per node — workable, but the log writes
dominated latency in our staging benchmark: p99 12ms.

**Token bucket with local refill + periodic sync**: each node keeps a
local bucket, syncs consumption to Redis every 500ms. Slightly loose
under bursts (each node may admit up to its share), but p99 overhead was
1.2ms in staging, and Redis loss degrades gracefully.

## What we chose and what it cost

We picked the token bucket with a shared budget: each node leases a
quota slice from Redis. During a Redis outage, nodes drain their lease
and then fail **closed** for new leases but **open** for existing ones —
a compromise we documented explicitly. The cost: under a 2x burst, a
client can exceed the nominal rate by up to 12 × lease-size until the
next sync. We accepted this because billing correctness is enforced
downstream, not at the gateway.

## Failure handling and observability

What fails first: Redis. Alerts fire on lease-renewal failures and on
the ratio of degraded-mode admissions. Our dashboard shows per-node
lease utilization; when one node's lease share exceeds 20% for 5
minutes, load-balancing skew is the usual culprit.

## Trade-offs we rejected and why

- **Centralized counting on every request**: exact, but adds a Redis
  round-trip to p99 and couples API availability to Redis availability.
- **Local-only buckets**: fast, but 12 nodes means 12x drift on global
  limits — unacceptable for billing.
- **Envoy's native rate limit service**: strong candidate; we rejected
  it only because our custom lease model needed features it doesn't
  expose. We noted this decision with a revisit-date.

If your limits are advisory (abuse prevention), take the simple fixed
window and sleep well. If they're contractual, the lease model's
complexity buys you correctness under failure — but write the failure
matrix down before you need it.
