# Project Guidelines: kc-nova / budget_menu_planner

## Project Overview & Mission
This repository (`kc-nova/budget_menu_planner`) is a dual-purpose **public** open-source repository serving as:
1. A **HACS-compliant Home Assistant Custom Component** for automated, budget-aware meal planning and shopping list generation.
2. A **FastAPI REST API Contract & Brand Blueprint** for the `kc-nova` ecosystem.

---

## ⚠️ Security & Privacy Boundary (CRITICAL Rule)
* **PUBLIC Scope (This Repo):** Home Assistant integration code, open REST API specifications, public branding assets, installation documentation.
* **PRIVATE Scope (DO NOT INCLUDE HERE):** Commercial mobile app source code (Flutter/React Native), App Store / Google Play secrets, In-App Purchase logic, payment gateway credentials. Commercial mobile app code belongs strictly in a separate, private repository (`kc-nova/mobile_app`).

---

## Core Domain & User Profile Context
* **Brand Name:** `kc-nova`
* **Target User Context:** Single person living in Belgium. Drives for work during weekdays with **NO vehicle cooling/fridge** and **NO microwave**.
* **Financial Model:** Default monthly food budget of **€60/month** (~€15/week), fully adjustable via HA Options Flow, service calls, or API parameters.
* **Meal Requirements:**
  * 28 unique meals across 4 weeks (zero repetition).
  * **Weekdays (Mon-Fri Lunch):** Must be shelf-stable at room temperature (wraps, cold pasta/protein salads, peanut butter, hard cheeses, nuts/fruit).
  * **Weekends (Sat-Sun):** Home kitchen assumed. Sunday dinner includes batch-cooking (extra portion used for Mon/Tue lunch).
* **Belgian Store Promo Matching (Option C):** Match recipe items against Belgian supermarket promotions (Colruyt, Aldi, Lidl, Delhaize, Intermarché). Output exact purchase-ready product names (e.g., `"500g Kipfilet"`).
* **Nutrition Goals:** Toggle between `weight_loss` (~1500–1800 kcal) and `maintenance` (~2000–2200 kcal).

---

## Repository Structure Guidelines

```text
budget_menu_planner/
├── custom_components/
│   └── budget_menu_planner/
│       ├── __init__.py           # Setup & service registration
│       ├── manifest.json         # HACS metadata (domain: budget_menu_planner, codeowner: @kc-nova)
│       ├── const.py              # Constants, meal database, macro calculations
│       ├── config_flow.py        # UI Setup & Options Flow (budget, nutrition, entities)
│       ├── sensor.py             # Daily menu HA sensor
│       └── services.yaml         # HA Service definitions
├── assets/
│   ├── brand_theme.json          # kc-nova design tokens (colors, dark/light themes, typography)
│   ├── brand_guidelines.md       # Visual identity rules
│   └── kc-nova_logo.svg          # Official brand SVG logo placeholder
├── api/
│   └── main.py                   # FastAPI REST backend with branded Swagger UI docs
├── docs/
│   └── COMMERCIAL_ARCHITECTURE.md # High-level guide for private mobile app integration
├── hacs.json                      # HACS repository configuration
├── CLAUDE.md                      # Project guidelines and context (this file)
└── README.md                      # Documentation with My Home Assistant badge & manual
```

---

## Technical Standards & Conventions
* **Python Target:** Python 3.11+
* **Home Assistant Rules:**
  * Must use async handlers (`async_setup_entry`, `async_step_init`).
  * Full support for Options Flow to reconfigure budget, nutrition goals, promo sensors, and notifications dynamically without restarting HA.
  * Integrate natively with `todo.add_item` and notification services (`send_weekly_email`).
* **Branding Rules:**
  * All user-facing documents, API Swagger endpoints, and manifests must incorporate `kc-nova` visual identity tokens and naming.
* **Code Quality:**
  * Strict typing (`typing` module / Pydantic models in API).
  * Fully asynchronous API endpoints using FastAPI.
  * No placeholder code (`# TODO: implement this later`). Write full, working implementations.

---

## Quick Reference Commands

### API Server Local Run
```bash
uvicorn api.main:app --reload --port 8000
```

### Git Workflow for kc-nova
```bash
git add .
git commit -m "feat: complete initial kc-nova budget menu planner structure"
git push origin main
```