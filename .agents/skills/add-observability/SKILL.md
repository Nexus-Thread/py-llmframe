---
name: add-observability
description: Add profiling, metrics, tracing, and operational notes for an important Python workflow without making unsupported performance claims.
---

# Add Observability

Use this skill when a workflow needs better runtime visibility, measurable
performance evidence, or operator-facing troubleshooting support.

## When to use this skill

Use this skill when you need to:

- profile a hot path before or after a change
- add metrics or tracing around meaningful workflow boundaries
- improve logging context for operator-visible paths
- document dashboards, alerts, or troubleshooting notes

This skill complements policy in the rules. It should not be used to justify
toy benchmarks or speculative performance claims.

## Steps

### 1. Define the workflow and signal you care about

Identify the specific path, such as:

- an external API call chain
- persistence or parsing work
- a high-volume adapter
- a latency-sensitive use case

State what you want to observe, for example latency, throughput, failure rate,
retry behavior, queue backlog, or memory growth.

### 2. Measure before changing behavior claims

Before claiming an optimization or observability improvement, capture a baseline
using representative inputs and environment notes.

Record:

- dataset or workload shape
- environment assumptions
- before numbers
- what changed
- after numbers when applicable

### 3. Instrument the right boundary

Prefer instrumentation at meaningful workflow boundaries such as:

- start and completion of a use case
- external I/O calls
- long-running parsing or persistence steps
- retry loops or failure boundaries

Keep field names stable and low-cardinality.

### 4. Add logs, metrics, or traces deliberately

- add logs for state transitions or operator-visible failures
- add metrics for duration, success or failure, and volume where supported
- add tracing spans around external I/O and other meaningful boundaries
- propagate request, correlation, or job IDs when available

Do not log or emit secrets, personal data, or highly variable labels.

### 5. Add operational notes

When the change matters operationally, update project-facing docs with:

- troubleshooting notes
- dashboard or alert references
- new failure modes
- rollout or on-call implications

Use `update-project-docs` for the durable documentation update.

### 6. Keep claims honest

Do not describe a change as a performance improvement unless representative
measurement supports that claim.

If the outcome is better visibility rather than lower latency, say that plainly.

## Output checklist

- workflow and observed signal are explicit
- baseline and environment are captured when claims depend on numbers
- instrumentation is placed at meaningful boundaries
- logs, metrics, and traces use safe, low-cardinality context
- operational documentation is updated when needed
