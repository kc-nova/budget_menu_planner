"""Sensor platform – Daily Menu Sensor for Budget Menu Planner."""

from __future__ import annotations

import logging
from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_BATCH_COOK,
    ATTR_CARBS_G,
    ATTR_DINNER,
    ATTR_FAT_G,
    ATTR_FIBRE_G,
    ATTR_LUNCH,
    ATTR_PROMO_ITEMS,
    ATTR_PROTEIN_G,
    ATTR_SHELF_STABLE,
    ATTR_SHOPPING_LIST,
    ATTR_TOTAL_KCAL,
    ATTR_WEEK_NUMBER,
    DOMAIN,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Budget Menu Planner sensors."""
    engine = hass.data[DOMAIN][entry.entry_id]

    coordinator = BudgetMenuCoordinator(hass, engine)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            DailyMenuSensor(coordinator, entry),
            WeeklyShoppingSensor(coordinator, entry),
        ]
    )


class BudgetMenuCoordinator(DataUpdateCoordinator):
    """Coordinator that refreshes menu data hourly."""

    def __init__(self, hass: HomeAssistant, engine) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.engine = engine

    async def _async_update_data(self) -> dict:
        """Fetch latest data from engine."""
        today_meals = self.engine.get_today_meals()
        week_num = _current_week_in_cycle()
        shopping = self.engine.build_shopping_list(week_num)

        lunch = today_meals.get("lunch") or {}
        dinner = today_meals.get("dinner") or {}

        return {
            "lunch": lunch,
            "dinner": dinner,
            "week_number": week_num,
            "shopping_list": shopping,
            "total_kcal": (lunch.get("kcal") or 0) + (dinner.get("kcal") or 0),
            "protein_g": (lunch.get("protein_g") or 0) + (dinner.get("protein_g") or 0),
            "fat_g": (lunch.get("fat_g") or 0) + (dinner.get("fat_g") or 0),
            "carbs_g": (lunch.get("carbs_g") or 0) + (dinner.get("carbs_g") or 0),
            "fibre_g": (lunch.get("fibre_g") or 0) + (dinner.get("fibre_g") or 0),
            "shelf_stable": lunch.get("shelf_stable", False),
            "batch_cook": dinner.get("batch_cook", False),
            "promo_items": lunch.get("promo_matches", []) + dinner.get("promo_matches", []),
        }


def _current_week_in_cycle() -> int:
    iso_week = date.today().isocalendar()[1]
    return ((iso_week - 1) % 4) + 1


class DailyMenuSensor(CoordinatorEntity, SensorEntity):
    """Sensor: today's meal names and full nutrition attributes."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:silverware-fork-knife"

    def __init__(self, coordinator: BudgetMenuCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_daily_menu"
        self._attr_name = "Dagmenu"

    @property
    def native_value(self) -> str | None:
        """Return today's lunch name as primary state."""
        lunch = self.coordinator.data.get("lunch") or {}
        return lunch.get("name", "Geen menu beschikbaar")

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        lunch = data.get("lunch") or {}
        dinner = data.get("dinner") or {}
        return {
            ATTR_LUNCH: lunch.get("name"),
            ATTR_DINNER: dinner.get("name"),
            ATTR_TOTAL_KCAL: data.get("total_kcal"),
            ATTR_PROTEIN_G: data.get("protein_g"),
            ATTR_FAT_G: data.get("fat_g"),
            ATTR_CARBS_G: data.get("carbs_g"),
            ATTR_FIBRE_G: data.get("fibre_g"),
            ATTR_SHELF_STABLE: data.get("shelf_stable"),
            ATTR_BATCH_COOK: data.get("batch_cook"),
            ATTR_PROMO_ITEMS: data.get("promo_items"),
            ATTR_WEEK_NUMBER: data.get("week_number"),
            "lunch_ingredients": lunch.get("ingredients", []),
            "dinner_ingredients": dinner.get("ingredients", []),
            "lunch_kcal": lunch.get("kcal"),
            "dinner_kcal": dinner.get("kcal"),
            "integration_version": VERSION,
        }

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Budget Menu Planner",
            "manufacturer": "kc-nova",
            "model": "Budget Menu Planner",
            "sw_version": VERSION,
        }


class WeeklyShoppingSensor(CoordinatorEntity, SensorEntity):
    """Sensor: current week's shopping list item count + list as attribute."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:cart-outline"
    _attr_native_unit_of_measurement = "items"

    def __init__(self, coordinator: BudgetMenuCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_weekly_shopping"
        self._attr_name = "Wekelijkse boodschappen"

    @property
    def native_value(self) -> int:
        shopping = self.coordinator.data.get("shopping_list", [])
        return len(shopping)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            ATTR_SHOPPING_LIST: self.coordinator.data.get("shopping_list", []),
            ATTR_WEEK_NUMBER: self.coordinator.data.get("week_number"),
        }

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Budget Menu Planner",
            "manufacturer": "kc-nova",
            "model": "Budget Menu Planner",
            "sw_version": VERSION,
        }
