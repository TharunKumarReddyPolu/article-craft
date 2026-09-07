---
title: Why our Kafka consumer fell seven hours behind
subtitle: What we learned bounding fan-out during a Black Friday incident
audience: backend engineers
article_type: case-study
ai_assistance: none
---

# Why our Kafka consumer fell seven hours behind
**What we learned bounding fan-out during a Black Friday incident**

Last Black Friday, our notification service fell seven hours behind. The
on-call dashboard showed consumer lag climbing from minutes to hours while
CPU sat at 20%. This is what actually happened, and the fix that surprised
us — because it wasn't the brokers.

## The situation

We run a Kafka consumer that fans out to per-user notification channels:
email, push, and in-app. Under normal traffic it processes about 4,000
events per second with lag under 30 seconds. At 40x normal traffic that
Black Friday, lag climbed for six hours straight. I watched the error rate
tick up at minute three and made the wrong call: I assumed the brokers were
the problem and we spent two hours scaling the cluster for nothing.

## What actually broke

The consumer was fine. Our fan-out wasn't bounded: one power user with
50,000 followers generated 50,000 notifications from a single event, and
our per-poll batch assumed roughly uniform per-key volumes. When one key
dominated a poll cycle, everything behind it waited. I benchmarked the fix
on staging with a replay of the incident traffic: bounding fan-out per key
brought p99 from 2.3s to 180ms on identical hardware, and end-to-end lag
recovered within 40 minutes of deploying.

## What we changed

We bounded fan-out per partition key: at most 500 notifications per user
per poll cycle, spilling the rest to the next cycle. Bounding is safe here
because Kafka's ordering guarantee only exists within a partition — see
[Kafka's ordering documentation](https://kafka.apache.org/documentation/#ordering)
— and our notifications don't need cross-key ordering. The core of the
change is deliberately boring:

```python
# Bound notifications per user per poll cycle.
for user, events in partition_batch:
    emit(events[:MAX_PER_USER])
    if len(events) > MAX_PER_USER:
        deferred.extend(events[MAX_PER_USER:])
```

The subtle part was choosing where to bound. Bounding at the producer would
have dropped events during the spike; bounding at the consumer with a
deferred queue kept them.

## What I'd do differently

I should have added the lag alert at the design stage, not the incident
stage. The design doc even mentioned "hot key risk" in a bullet we never
turned into a requirement. If I built it again, I'd bound fan-out at the
producer with an explicit overflow channel, and I'd write the load test
before the feature, not after the outage. The lesson I keep from this one:
capacity assumptions you don't turn into tests are just hopes.

## Lessons for your team

- Fan-out without bounds is a latency bomb waiting for your busiest user.
- Your consumer isn't always the bottleneck — measure before scaling.
- Ordering guarantees are per-partition; exploit that for safe batching.
- Turn every "we should handle hot keys" bullet into a test or delete it.
