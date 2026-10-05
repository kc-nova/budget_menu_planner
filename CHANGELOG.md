# Budget Menu Planner – Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [1.0.0] – 2026-10-05

### Added
- Initial release of the Budget Menu Planner HACS integration
- 28 unique meals across 4-week rotation (no repetition)
- Dynamic budget engine (€10–€500/month, default €60)
- Nutrition goals: `weight_loss` and `maintenance`
- Weekday lunches: fully shelf-stable (no fridge/microwave required)
- Sunday batch-cooking: extra portions for Mon/Tue lunches
- `generate_month_menu` service with budget + goal overrides
- `push_to_shopping_list` service → native HA Todo integration
- `send_weekly_email` service via any HA notify service
- Config Flow + Options Flow (edit all settings from HA UI)
- `sensor.dagmenu` – daily lunch/dinner + full nutrition attributes
- `sensor.wekelijkse_boodschappen` – weekly shopping list sensor
- Promo sensor integration (optional, store brand matching)
- Store references: Colruyt, Aldi, Lidl, Delhaize, Intermarché
- Standalone FastAPI REST backend (`api/main.py`)
- kc-nova brand assets: SVG logo, `brand_theme.json`, brand guidelines
- Dutch (`nl`) and English (`en`) UI translations
- `docs/COMMERCIAL_ARCHITECTURE.md` – abstract ecosystem blueprint
- HACS compliance: `hacs.json`, MIT license, HACS badge in README
