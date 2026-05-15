# System Design Interview Framework

Master the system design interview with structured frameworks and real examples from this repo.

## Overview

System design interviews require balancing multiple concerns: scalability, reliability, consistency, and cost. This guide provides a proven 4-phase framework to think through systems systematically.

## The 4-Phase Framework

1. **Requirements & Clarification** (5-10 min) — Scope the problem, agree on constraints
2. **High-Level Architecture** (10-15 min) — Sketch major components and data flow
3. **Deep Dive** (15-20 min) — Design 2-3 critical components in detail
4. **Trade-offs & Scaling** (10-15 min) — Discuss alternatives and handle scale increases

## Resources

- **[Full Interview Guide](system-design-interview-guide.md)** — Detailed 4-phase flow with checklist
- **[Common Follow-ups](common-follow-ups.md)** — Expected questions by system type
- **[Design Patterns Reference](design-patterns-reference.md)** — GoF patterns in system design

## Example Systems in This Repo

This repo includes 35+ system design implementations in `python/system_design/`:

- **Social:** News feed, followers system, like/comment system, photo sharing
- **Commerce:** E-commerce, auction system, payment system, wallet system
- **Real-Time:** Chat system, notifications, websocket server
- **Distributed:** Consensus algorithm, distributed transaction, saga pattern
- **Infrastructure:** Load balancer, rate limiter, circuit breaker, API gateway
- **Data:** Search engine, recommendation engine, time series DB, log aggregation
- **Advanced:** Parking lot, leaderboard, ride sharing, message queue, pub/sub

See [Common Follow-ups](common-follow-ups.md) for expected questions on each system.

## How to Use These Resources

1. **Before an interview:** Skim the 4-phase guide and checklist to refresh
2. **During practice:** Use the full guide to structure your thinking
3. **Before asking a system:** Check common follow-ups to prepare answers
4. **Between systems:** Study the implementations in this repo and understand trade-offs
