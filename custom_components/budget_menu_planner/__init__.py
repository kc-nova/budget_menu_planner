"""Budget Menu Planner – Home Assistant integration entry point."""

from __future__ import annotations

import logging
from datetime import date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    ATTR_SHOPPING_LIST,
    ATTR_WEEK_NUMBER,
    CONF_BUDGET,
    CONF_NOTIFY_SERVICE,
    CONF_NUTRITION_GOAL,
    CONF_PROMO_SENSOR,
    CONF_TODO_ENTITY,
    DEFAULT_BUDGET,
    DEFAULT_NOTIFY,
    DEFAULT_NUTRITION_GOAL,
    DEFAULT_TODO,
    DOMAIN,
    MEAL_DB,
    NUTRITION_GOAL_WEIGHT_LOSS,
    SERVICE_GENERATE_MONTH_MENU,
    SERVICE_PUSH_TO_SHOPPING_LIST,
    SERVICE_SEND_WEEKLY_EMAIL,
    SUPPORTED_STORES,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Budget Menu Planner from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    engine = BudgetMenuEngine(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = engine

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_services(hass, engine, entry)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info(
        "Budget Menu Planner v%s loaded – budget=€%.0f/month, goal=%s",
        VERSION,
        entry.options.get(CONF_BUDGET, entry.data.get(CONF_BUDGET, DEFAULT_BUDGET)),
        entry.options.get(CONF_NUTRITION_GOAL, entry.data.get(CONF_NUTRITION_GOAL, DEFAULT_NUTRITION_GOAL)),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        # Unregister services when last entry removed
        if not hass.data[DOMAIN]:
            for service in (
                SERVICE_GENERATE_MONTH_MENU,
                SERVICE_PUSH_TO_SHOPPING_LIST,
                SERVICE_SEND_WEEKLY_EMAIL,
            ):
                hass.services.async_remove(DOMAIN, service)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update – reload entry to pick up new settings."""
    await hass.config_entries.async_reload(entry.entry_id)


@callback
def _register_services(
    hass: HomeAssistant,
    engine: "BudgetMenuEngine",
    entry: ConfigEntry,
) -> None:
    """Register integration services."""

    # ── generate_month_menu ───────────────────────────────────────────────────
    async def handle_generate_month_menu(call: ServiceCall) -> None:
        budget = call.data.get(CONF_BUDGET, engine.budget)
        goal = call.data.get(CONF_NUTRITION_GOAL, engine.nutrition_goal)
        promo_state = _get_promo_state(hass, engine.promo_sensor)

        menu = engine.generate_month_menu(budget=budget, goal=goal, promo_items=promo_state)
        hass.data[DOMAIN][entry.entry_id].current_menu = menu

        # Fire event so automations / sensors can react
        hass.bus.async_fire(
            f"{DOMAIN}_menu_generated",
            {
                "weeks": [
                    {
                        "week": w,
                        "meals": [m["name"] for m in meals],
                    }
                    for w, meals in menu.items()
                ]
            },
        )
        _LOGGER.info("Month menu generated (budget=€%.0f, goal=%s)", budget, goal)

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_MONTH_MENU,
        handle_generate_month_menu,
        schema=vol.Schema(
            {
                vol.Optional(CONF_BUDGET): vol.Coerce(float),
                vol.Optional(CONF_NUTRITION_GOAL): vol.In(["weight_loss", "maintenance"]),
            }
        ),
    )

    # ── push_to_shopping_list ─────────────────────────────────────────────────
    async def handle_push_to_shopping_list(call: ServiceCall) -> None:
        week_num = call.data.get(ATTR_WEEK_NUMBER, _current_week_in_cycle())
        todo_entity = call.data.get(CONF_TODO_ENTITY, engine.todo_entity)

        shopping_list = engine.build_shopping_list(week_num=week_num)

        for item in shopping_list:
            await hass.services.async_call(
                "todo",
                "add_item",
                {"entity_id": todo_entity, "item": item},
                blocking=True,
            )

        _LOGGER.info(
            "Pushed %d items to %s for week %d",
            len(shopping_list),
            todo_entity,
            week_num,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_PUSH_TO_SHOPPING_LIST,
        handle_push_to_shopping_list,
        schema=vol.Schema(
            {
                vol.Optional(ATTR_WEEK_NUMBER): vol.All(int, vol.Range(min=1, max=4)),
                vol.Optional(CONF_TODO_ENTITY): cv.entity_id,
            }
        ),
    )

    # ── send_weekly_email ─────────────────────────────────────────────────────
    async def handle_send_weekly_email(call: ServiceCall) -> None:
        week_num = call.data.get(ATTR_WEEK_NUMBER, _current_week_in_cycle())
        notify_service = call.data.get(CONF_NOTIFY_SERVICE, engine.notify_service)

        week_meals = engine.get_week_meals(week_num)
        shopping_list = engine.build_shopping_list(week_num=week_num)

        meal_lines = "\n".join(
            f"  • {m['day'].capitalize()}: {m['name']}"
            for m in sorted(week_meals, key=lambda x: _day_order(x["day"]))
        )
        shop_lines = "\n".join(f"  ✓ {item}" for item in shopping_list)

        message = (
            f"🥗 Budget Menu Planner – Week {week_num}\n\n"
            f"Budget: €{engine.budget:.0f}/maand  |  Doel: {engine.nutrition_goal}\n\n"
            f"📅 Maaltijdplan:\n{meal_lines}\n\n"
            f"🛒 Boodschappenlijst:\n{shop_lines}\n\n"
            f"— kc-nova Budget Menu Planner v{VERSION}"
        )

        service_parts = notify_service.split(".")
        domain_part = service_parts[0] if len(service_parts) > 1 else "notify"
        service_part = service_parts[1] if len(service_parts) > 1 else notify_service

        await hass.services.async_call(
            domain_part,
            service_part,
            {
                "title": f"🥗 Weekmenu Week {week_num}",
                "message": message,
            },
            blocking=True,
        )
        _LOGGER.info("Weekly email sent for week %d via %s", week_num, notify_service)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_WEEKLY_EMAIL,
        handle_send_weekly_email,
        schema=vol.Schema(
            {
                vol.Optional(ATTR_WEEK_NUMBER): vol.All(int, vol.Range(min=1, max=4)),
                vol.Optional(CONF_NOTIFY_SERVICE): str,
            }
        ),
    )


def _get_promo_state(hass: HomeAssistant, promo_sensor: str | None) -> list[str]:
    """Retrieve promo item names from optional sensor attribute."""
    if not promo_sensor:
        return []
    state = hass.states.get(promo_sensor)
    if state is None:
        return []
    return state.attributes.get("promo_items", [])


def _current_week_in_cycle() -> int:
    """Return week-in-4-week-cycle (1–4) based on ISO week number."""
    iso_week = date.today().isocalendar()[1]
    return ((iso_week - 1) % 4) + 1


def _day_order(day: str) -> int:
    order = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    }
    return order.get(day.lower(), 99)


class BudgetMenuEngine:
    """Core business logic – budget scaling, menu generation, shopping lists."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self.current_menu: dict = {}

    # ── Config accessors ──────────────────────────────────────────────────────
    @property
    def budget(self) -> float:
        return float(
            self._entry.options.get(
                CONF_BUDGET, self._entry.data.get(CONF_BUDGET, DEFAULT_BUDGET)
            )
        )

    @property
    def nutrition_goal(self) -> str:
        return self._entry.options.get(
            CONF_NUTRITION_GOAL,
            self._entry.data.get(CONF_NUTRITION_GOAL, DEFAULT_NUTRITION_GOAL),
        )

    @property
    def promo_sensor(self) -> str | None:
        return self._entry.options.get(
            CONF_PROMO_SENSOR, self._entry.data.get(CONF_PROMO_SENSOR)
        )

    @property
    def todo_entity(self) -> str:
        return self._entry.options.get(
            CONF_TODO_ENTITY, self._entry.data.get(CONF_TODO_ENTITY, DEFAULT_TODO)
        )

    @property
    def notify_service(self) -> str:
        return self._entry.options.get(
            CONF_NOTIFY_SERVICE,
            self._entry.data.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY),
        )

    # ── Core methods ──────────────────────────────────────────────────────────
    def generate_month_menu(
        self,
        budget: float | None = None,
        goal: str | None = None,
        promo_items: list[str] | None = None,
    ) -> dict[int, list[dict]]:
        """Generate 4-week menu grouped by week number."""
        _budget = budget or self.budget
        _goal = goal or self.nutrition_goal
        _promos = promo_items or []

        menu: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: []}

        for meal in MEAL_DB:
            scaled = dict(meal)
            scaled["budget_tier"] = self._budget_tier(_budget)
            scaled["promo_matches"] = self._find_promo_matches(meal, _promos)
            scaled["goal_match"] = self._check_goal_match(meal, _goal)
            menu[meal["week"]].append(scaled)

        return menu

    def get_week_meals(self, week_num: int) -> list[dict]:
        """Return meals for a given week (1–4)."""
        if self.current_menu:
            return self.current_menu.get(week_num, [])
        # Fallback: generate fresh
        full_menu = self.generate_month_menu()
        return full_menu.get(week_num, [])

    def get_today_meals(self) -> dict:
        """Return today's lunch and dinner."""
        today = date.today()
        week_num = _current_week_in_cycle()
        day_name = today.strftime("%A").lower()

        week_meals = self.get_week_meals(week_num)
        lunch = next((m for m in week_meals if m["type"] == "lunch" and m["day"] == day_name), None)
        dinner = next((m for m in week_meals if m["type"] == "dinner" and m["day"] == day_name), None)
        return {"lunch": lunch, "dinner": dinner}

    def build_shopping_list(self, week_num: int | None = None) -> list[str]:
        """Build a deduplicated, purchase-ready shopping list for one week."""
        _week = week_num or _current_week_in_cycle()
        week_meals = self.get_week_meals(_week)

        seen: dict[str, str] = {}
        for meal in week_meals:
            for product, qty in meal.get("ingredients", []):
                key = product.split("(")[0].strip().lower()
                if key not in seen:
                    seen[key] = f"{product} – {qty}"

        return sorted(seen.values())

    # ── Internal helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _budget_tier(budget: float) -> str:
        if budget < 40:
            return "budget"
        if budget < 70:
            return "standard"
        return "premium"

    @staticmethod
    def _find_promo_matches(meal: dict, promo_items: list[str]) -> list[str]:
        """Return ingredient names that appear in current promos."""
        matches = []
        for product, _qty in meal.get("ingredients", []):
            for promo in promo_items:
                if promo.lower() in product.lower():
                    matches.append(product)
                    break
        return matches

    @staticmethod
    def _check_goal_match(meal: dict, goal: str) -> bool:
        """Check if meal fits the nutrition goal target ranges."""
        if goal == NUTRITION_GOAL_WEIGHT_LOSS:
            return meal.get("kcal", 0) <= 650 and meal.get("protein_g", 0) >= 20
        # maintenance
        return 600 <= meal.get("kcal", 0) <= 900
