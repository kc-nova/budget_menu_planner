"""Config flow for Budget Menu Planner – supports initial setup AND Options Flow."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
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
    NUTRITION_GOALS,
)

_LOGGER = logging.getLogger(__name__)


def _build_schema(
    defaults: dict[str, Any],
    show_advanced: bool = False,
) -> vol.Schema:
    """Shared schema builder for both config and options flow."""
    return vol.Schema(
        {
            vol.Required(CONF_BUDGET, default=defaults.get(CONF_BUDGET, DEFAULT_BUDGET)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=10,
                    max=500,
                    step=5,
                    unit_of_measurement="€/maand",
                    mode=selector.NumberSelectorMode.SLIDER,
                )
            ),
            vol.Required(
                CONF_NUTRITION_GOAL,
                default=defaults.get(CONF_NUTRITION_GOAL, DEFAULT_NUTRITION_GOAL),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value="weight_loss", label="Gewichtsverlies (~1500–1800 kcal, hoog eiwit)"),
                        selector.SelectOptionDict(value="maintenance", label="Onderhoud (~2000–2200 kcal, gebalanceerd)"),
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(
                CONF_TODO_ENTITY,
                default=defaults.get(CONF_TODO_ENTITY, DEFAULT_TODO),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="todo")
            ),
            vol.Required(
                CONF_NOTIFY_SERVICE,
                default=defaults.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
            vol.Optional(
                CONF_PROMO_SENSOR,
                default=defaults.get(CONF_PROMO_SENSOR, ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor",
                    multiple=False,
                )
            ),
        }
    )


class BudgetMenuPlannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle user step – initial setup form."""
        # Only one instance allowed
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        if user_input is not None:
            # Strip empty promo sensor
            if not user_input.get(CONF_PROMO_SENSOR):
                user_input.pop(CONF_PROMO_SENSOR, None)

            return self.async_create_entry(
                title="Budget Menu Planner",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema({}),
            errors=errors,
            description_placeholders={
                "brand": "kc-nova",
                "default_budget": str(DEFAULT_BUDGET),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "BudgetMenuPlannerOptionsFlow":
        """Create the options flow."""
        return BudgetMenuPlannerOptionsFlow(config_entry)


class BudgetMenuPlannerOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow – edit settings at any time from HA UI."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        current = {
            **self.config_entry.data,
            **self.config_entry.options,
        }

        if user_input is not None:
            if not user_input.get(CONF_PROMO_SENSOR):
                user_input.pop(CONF_PROMO_SENSOR, None)

            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current),
            errors=errors,
            description_placeholders={
                "brand": "kc-nova",
            },
        )
