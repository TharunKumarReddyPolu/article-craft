---
title: Understanding Kafka's ordering guarantees
subtitle: A complete guide to partition ordering
article_type: technical-explainer
ai_assistance: generated
---

# Understanding Kafka's ordering guarantees
**A complete guide to partition ordering**

Kafka is a distributed streaming platform. Kafka guarantees ordering
within a partition. Kafka does not guarantee ordering across partitions.
This article explains Kafka ordering.

## What is Kafka

Kafka is a distributed streaming platform that is used by thousands of
companies. Kafka stores records in topics. Topics are divided into
partitions. Each partition is an ordered, immutable sequence of records.

## Ordering within a partition

Kafka guarantees ordering within a partition. Records with the same key
go to the same partition. This means ordering is preserved for records
with the same key. Producers can configure the partitioner to control
which partition receives each record.

## Ordering across partitions

Kafka does not guarantee ordering across partitions. If you need
ordering across partitions, you must design your application differently.
This is a common source of confusion for developers new to Kafka.

## Consumer ordering

Consumers read partitions in order. A consumer group assigns partitions
to consumers. Each partition is consumed by exactly one consumer in the
group. This preserves ordering within the partition during consumption.

## Conclusion

Kafka ordering is guaranteed within partitions but not across partitions.
Understanding this distinction is essential for building correct
applications with Kafka. Design your applications with this constraint
in mind.
