# Commercial Architecture – Abstract Guide

> **Visibility: PUBLIC** · This document intentionally contains **no proprietary source code**.
> It describes the high-level architecture only. All implementation details live in the
> **private** repository `kc-nova/mobile_app` (not publicly accessible).

---

## Overview

The kc-nova ecosystem follows a **layered, loosely-coupled architecture** that separates concerns cleanly between:

1. **This public repository** (`kc-nova/budget_menu_planner`) — open-source Home Assistant integration + REST API contract
2. **Private mobile application** (`kc-nova/mobile_app`) — commercial native app (source not public)
3. **Private infrastructure** — cloud backend, databases, payment gateway (not public)

```
┌─────────────────────────────────────────────────────────────────┐
│                       END USER DEVICES                          │
│                                                                 │
│  ┌──────────────────┐        ┌──────────────────────────────┐  │
│  │  Home Assistant  │        │  kc-nova Mobile App          │  │
│  │  (open-source)   │        │  (private, commercial)       │  │
│  │                  │        │                              │  │
│  │  budget_menu_    │        │  • iOS / Android             │  │
│  │  planner HACS    │        │  • In-App Purchases          │  │
│  │  integration     │        │  • Push notifications        │  │
│  └────────┬─────────┘        └──────────────┬───────────────┘  │
└───────────┼──────────────────────────────────┼─────────────────┘
            │ REST API (open contract)           │ Private API
            │ GET /menu, GET /shopping-list      │ (authenticated)
            │ POST /generate                     │
            ▼                                   ▼
┌───────────────────────────┐     ┌─────────────────────────────┐
│  Budget Menu Planner API  │     │  Private kc-nova Backend    │
│  (this repo: api/main.py) │     │  • User accounts            │
│                           │     │  • Subscription management  │
│  • Open REST contract     │     │  • Payment processing       │
│  • No auth required       │     │  • Push notification infra  │
│  • MIT licensed           │     │  • Analytics                │
└───────────────────────────┘     └─────────────────────────────┘
```

---

## How the Mobile App Connects

> **Note:** No mobile app source code is included or implied here.

The private mobile application integrates with this ecosystem through **three integration points**:

### 1. Public REST API (Open Contract)
The mobile app MAY consume the same public REST API defined in `api/main.py`:
- `GET /menu` — fetch the 4-week meal plan
- `GET /shopping-list?week=N` — fetch the shopping list for a given week
- `POST /generate` — generate a custom menu with budget and promo parameters

This API is **rate-limit free for self-hosted deployments** and requires no API key.

### 2. Home Assistant Companion Integration (Optional)
Users who also run Home Assistant may connect the mobile app to their HA instance via the **HA Companion App WebSocket API**, allowing:
- Triggering `budget_menu_planner.generate_month_menu` directly from the mobile UI
- Subscribing to `budget_menu_planner_menu_generated` HA events in real time
- Reading sensor states (`sensor.dagmenu`, `sensor.wekelijkse_boodschappen`)

### 3. Private Cloud Backend (Subscription Features)
Premium features offered through the commercial mobile app (e.g., AI-powered recipe suggestions, multi-person household support, store-specific promo integration) are powered by a **separate, private backend** not included in this repository.

---

## Data Flow – Menu Generation

```
User sets budget & goal
        │
        ▼
[Open API POST /generate]   OR   [HA Service Call]
        │                               │
        └──────────┬────────────────────┘
                   ▼
         BudgetMenuEngine
         (same logic, open-source)
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
   Menu JSON             Shopping List
   (28 meals,            (deduplicated,
    4-week rotation)      store-branded)
         │                    │
         ▼                    ▼
   Mobile App UI        HA Todo Entity
   (private)            (open-source)
```

---

## Security Boundary

| Layer | Authentication | Source |
|---|---|---|
| Public REST API | None (open) | This repo |
| HA Integration | HA long-lived token | This repo |
| Private Mobile API | JWT + subscription check | Private repo |
| Payment Gateway | PCI-DSS compliant provider | Private infra |

**No credentials, API keys, or private endpoints appear in this public repository.**

---

## HACS Compliance Statement

This repository (`kc-nova/budget_menu_planner`) is a **pure open-source HACS custom component**.
It contains:
- ✅ Full HA integration source code
- ✅ Open REST API contract
- ✅ Public brand assets
- ❌ No commercial mobile app code
- ❌ No In-App Purchase logic
- ❌ No payment gateway credentials
- ❌ No private backend endpoints

The commercial mobile application is developed and maintained separately in a private repository
and is subject to its own commercial license.

---

*kc-nova · [github.com/kc-nova](https://github.com/kc-nova)*
