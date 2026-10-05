# Budget Menu Planner

<p align="center">
  <img src="assets/kc-nova_logo.svg" alt="kc-nova logo" height="60"/>
</p>

<p align="center">
  <strong>A smart, budget-conscious 4-week meal planner for Home Assistant</strong><br/>
  by <a href="https://github.com/kc-nova"><strong>kc-nova</strong></a>
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2Fkc-nova%2Fbudget_menu_planner&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in Home Assistant HACS">
  </a>
  &nbsp;
  <img src="https://img.shields.io/github/v/release/kc-nova/budget_menu_planner?style=flat-square&color=1B4F8A" alt="Release">
  &nbsp;
  <img src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square" alt="HACS Custom">
  &nbsp;
  <img src="https://img.shields.io/badge/HA-2024.1%2B-blue?style=flat-square" alt="HA 2024.1+">
  &nbsp;
  <img src="https://img.shields.io/github/license/kc-nova/budget_menu_planner?style=flat-square" alt="MIT License">
</p>

---

## ✨ Features

- 🗓️ **28 unique meals** across a rolling 4-week cycle — no repetition
- 💶 **Dynamic budget engine** — scales ingredient tiers from €10–€500/month (default: **€60/month**)
- 🥗 **Two nutrition goals** — *Weight Loss* (~1500–1800 kcal, high protein) or *Maintenance* (~2000–2200 kcal)
- 🚗 **Weekday lunches are shelf-stable** — no fridge or microwave required (designed for Belgian drivetime workers)
- 🍳 **Sunday batch-cooking** — one Sunday cook yields Mon+Tue lunch automatically
- 🏷️ **Promo sensor integration** — auto-swaps ingredients to discounted Colruyt/Aldi/Lidl/Delhaize/Intermarché products
- 🛒 **Native HA Todo push** — one service call sends the week's shopping list to any HA Todo entity
- 📧 **Weekly email dispatch** — formatted weekly menu + shopping list via any HA notify service
- ⚙️ **Full Options Flow** — edit budget, nutrition goal, and entity settings from HA UI at any time
- 🔌 **Open REST API** — standalone FastAPI backend for external integrations

---

## 🚀 Installation

### Option A — 1-Click via My Home Assistant (Recommended)

[![Open your Home Assistant instance and show the add repository dialog with a specific repository pre-filled.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2Fkc-nova%2Fbudget_menu_planner&category=integration)

1. Click the badge above
2. Click **"Add"** in the HACS dialog
3. Search for **"Budget Menu Planner"** in HACS → Integrations
4. Click **"Download"**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration** → search **Budget Menu Planner**

### Option B — Manual HACS Custom Repository

1. In HACS, click the ⋮ menu → **"Custom repositories"**
2. Add URL: `https://github.com/kc-nova/budget_menu_planner`
3. Category: **Integration**
4. Click **"Add"**
5. Find **Budget Menu Planner** in HACS and download
6. Restart Home Assistant
7. Add via **Settings → Devices & Services → Add Integration**

### Option C — Manual Install (No HACS)

```bash
# From your Home Assistant config directory:
mkdir -p custom_components/budget_menu_planner
cd custom_components/budget_menu_planner
# Download all files from:
# https://github.com/kc-nova/budget_menu_planner/tree/main/custom_components/budget_menu_planner
```

---

## ⚙️ Configuration

During setup you will be prompted for:

| Field | Description | Default |
|---|---|---|
| **Monthly budget** | Budget in € per month (slider: €10–€500) | €60 |
| **Nutrition goal** | `weight_loss` or `maintenance` | `weight_loss` |
| **Todo entity** | HA Todo entity for the shopping list | `todo.shopping_list` |
| **Notify service** | HA notify service for weekly email | `notify.notify` |
| **Promo sensor** *(optional)* | Sensor providing a `promo_items` attribute | *(none)* |

### Editing Settings Later (Options Flow)

Go to **Settings → Devices & Services → Budget Menu Planner → Configure** to update any setting at any time. Changes are applied immediately without restart.

---

## 📊 Sensors

After setup, two sensors are created:

| Entity ID | Description |
|---|---|
| `sensor.dagmenu` | Today's lunch & dinner names + full nutrition attributes |
| `sensor.wekelijkse_boodschappen` | Number of shopping items this week + full list |

### `sensor.dagmenu` attributes

```yaml
lunch: "Kipfilet wrap met pindakaas en banaan"
dinner: "Kip-curryrijst (batch-cook)"
total_kcal: 1470
protein_g: 93
fat_g: 44
carbs_g: 160
fibre_g: 13
shelf_stable: true
batch_cook: true
promo_items: []
week_number: 1
lunch_ingredients: [["Volkoren tortilla wrap (2 stuks)", "2 stuks"], ...]
dinner_ingredients: [["Kipfilet (500g Aldi)", "500g"], ...]
```

---

## 🔧 Services

### `budget_menu_planner.generate_month_menu`

Generate (or regenerate) the full 4-week menu. Optionally override budget and nutrition goal.

```yaml
service: budget_menu_planner.generate_month_menu
data:
  monthly_budget: 60
  nutrition_goal: weight_loss
```

### `budget_menu_planner.push_to_shopping_list`

Push the current week's shopping list to a HA Todo entity.

```yaml
service: budget_menu_planner.push_to_shopping_list
data:
  week_number: 1          # Optional: 1–4, defaults to current week
  todo_entity: todo.shopping_list
```

### `budget_menu_planner.send_weekly_email`

Send the weekly menu + shopping list as an email/notification.

```yaml
service: budget_menu_planner.send_weekly_email
data:
  week_number: 1          # Optional
  notify_service: notify.gmail
```

---

## 🤖 Automation Examples

### Auto-push shopping list every Sunday at 17:00

```yaml
alias: "Weekly shopping list – push to Todo"
trigger:
  - platform: time
    at: "17:00:00"
condition:
  - condition: time
    weekday: [sun]
action:
  - service: budget_menu_planner.push_to_shopping_list
    data:
      week_number: "{{ ((now().isocalendar()[1] - 1) % 4) + 1 }}"
      todo_entity: todo.shopping_list
```

### Auto-email menu every Sunday at 18:00

```yaml
alias: "Weekly menu email – Sunday dispatch"
trigger:
  - platform: time
    at: "18:00:00"
condition:
  - condition: time
    weekday: [sun]
action:
  - service: budget_menu_planner.send_weekly_email
    data:
      notify_service: notify.gmail
```

### Regenerate menu on first day of month

```yaml
alias: "Budget Menu – Monthly regeneration"
trigger:
  - platform: template
    value_template: "{{ now().day == 1 and now().hour == 6 }}"
action:
  - service: budget_menu_planner.generate_month_menu
    data:
      monthly_budget: 60
      nutrition_goal: weight_loss
```

### Display today's lunch in a Lovelace card

```yaml
type: markdown
content: |
  ## 🥗 Vandaag
  **Lunch:** {{ state_attr('sensor.dagmenu', 'lunch') }}
  **Diner:** {{ state_attr('sensor.dagmenu', 'dinner') }}
  **Totaal:** {{ state_attr('sensor.dagmenu', 'total_kcal') }} kcal
  | Eiwit | Vet | Koolhydraten | Vezels |
  |---|---|---|---|
  | {{ state_attr('sensor.dagmenu', 'protein_g') }}g | {{ state_attr('sensor.dagmenu', 'fat_g') }}g | {{ state_attr('sensor.dagmenu', 'carbs_g') }}g | {{ state_attr('sensor.dagmenu', 'fibre_g') }}g |
```

---

## 🌐 REST API (kc-nova Open Backend)

For external integrations, a standalone FastAPI service is included in `api/main.py`.

### Quick start

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000/docs for the kc-nova branded Swagger UI
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | API liveness check |
| `GET` | `/menu` | Full 4-week menu (budget + goal params) |
| `GET` | `/shopping-list` | Weekly shopping list (week 1–4) |
| `POST` | `/generate` | Custom menu with promo matching |

### Example: Generate menu with promo matching

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 55,
    "nutrition_goal": "weight_loss",
    "promo_items": ["Kipfilet", "Pindakaas", "Tonijn"]
  }'
```

---

## 🏪 Supported Stores & Promo Integration

The integration references exact, purchase-ready product names for:

- **Colruyt** — house brand references
- **Aldi** — budget-tier staples
- **Lidl** — dry goods & pantry
- **Delhaize** — quality proteins & fresh
- **Intermarché** — canned goods & sauces

Connect a custom sensor with a `promo_items` attribute to automatically highlight and swap discounted alternatives.

---

## 🗺️ Meal Plan Overview

| Week | Mon–Fri Lunches | Sat Dinner | Sun Dinner (batch-cook) |
|---|---|---|---|
| **1** | Wrap/Pasta/Noten/Kaas/PB sandwiches | Ovenpasta met gehakt | Kip-curryrijst |
| **2** | Hummus wrap/Niçoise/Notenbrood/Snackbox/Kikkererwten | Stamppot boerenkool | Linzensoep |
| **3** | Pesto pasta/Energieballen/Sardines/Hummus/Ham wrap | Wokrijst | Kippensoep |
| **4** | Makreel/Couscous/Cashew wrap/Trail mix/Antipasto | Chili con carne | Aardappelschotel |

All weekday lunches are **shelf-stable** (no cooling required). Sunday batch-cooks yield extra portions for Monday and Tuesday lunches.

---

## 🏗️ Architecture

```
budget_menu_planner (public, MIT)
├── custom_components/budget_menu_planner/   # HA integration
│   ├── __init__.py          # Setup, services, BudgetMenuEngine
│   ├── config_flow.py       # UI setup + Options Flow
│   ├── sensor.py            # Daily menu & shopping sensors
│   ├── const.py             # Constants, defaults, 28-meal DB
│   ├── manifest.json        # HACS manifest
│   └── services.yaml        # Service descriptions
├── api/
│   └── main.py              # Standalone FastAPI REST service
├── assets/                  # kc-nova brand assets
│   ├── brand_theme.json     # Design tokens
│   ├── brand_guidelines.md  # Design system guide
│   └── kc-nova_logo.svg     # Brand logo
├── docs/
│   └── COMMERCIAL_ARCHITECTURE.md  # High-level ecosystem diagram
└── hacs.json
```

See [`docs/COMMERCIAL_ARCHITECTURE.md`](docs/COMMERCIAL_ARCHITECTURE.md) for the abstract overview of how the private `kc-nova/mobile_app` ecosystem connects to this open-source integration.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/kc-nova"><strong>kc-nova</strong></a>
</p>
