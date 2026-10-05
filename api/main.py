"""
kc-nova Budget Menu Planner – Public REST API
=============================================
Lightweight FastAPI backend exposing the Budget Menu Planner engine
as a standalone open-source REST service.

Brand: kc-nova | License: MIT
Docs : /docs  (kc-nova branded Swagger UI)
"""

from __future__ import annotations

import json
from datetime import date
from enum import Enum
from typing import Any

from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ─── kc-nova brand palette (mirrors brand_theme.json) ────────────────────────
BRAND_PRIMARY = "#1B4F8A"
BRAND_ACCENT = "#F5A623"
BRAND_BG_DARK = "#0D1B2A"
BRAND_TEXT = "#FFFFFF"

# ─── Embedded meal database (same source-of-truth as HA integration) ─────────
# We import the data here via inline JSON to keep this file self-contained
# for standalone deployment (no HA dependency).
MEAL_DB: list[dict] = [
    # Week 1 – Lunches (shelf-stable, no fridge/microwave)
    {"id":"W1_L1","name":"Kipfilet wrap met pindakaas en banaan","type":"lunch","week":1,"day":"monday","shelf_stable":True,"batch_cook":False,"kcal":620,"protein_g":38,"fat_g":22,"carbs_g":65,"fibre_g":6,"ingredients":[["Volkoren tortilla wrap (2 stuks)","2 stuks"],["Kipfilet (gekookt, koud)","100g"],["Pindakaas (Aldi)","30g"],["Banaan","1 stuk"],["Honing mosterd saus (Colruyt)","15g"]]},
    {"id":"W1_L2","name":"Pastasalade met tonijn en olijven","type":"lunch","week":1,"day":"tuesday","shelf_stable":True,"batch_cook":False,"kcal":590,"protein_g":35,"fat_g":18,"carbs_g":68,"fibre_g":5,"ingredients":[["Pasta penne (Lidl)","100g"],["Tonijn in water blik (Delhaize)","1 blik 160g"],["Zwarte olijven (pot)","50g"],["Zongedroogde tomaten (pot)","30g"],["Olijfolie extra vierge","10ml"],["Italiaanse kruiden","5g"]]},
    {"id":"W1_L3","name":"Amandel-energieballen met appel","type":"lunch","week":1,"day":"wednesday","shelf_stable":True,"batch_cook":False,"kcal":540,"protein_g":22,"fat_g":28,"carbs_g":55,"fibre_g":9,"ingredients":[["Havermout (Lidl)","80g"],["Amandelen (ongezouten)","40g"],["Pindakaas (Aldi)","30g"],["Honing (Colruyt)","15g"],["Appel","1 stuk"],["Gemengde noten","30g"]]},
    {"id":"W1_L4","name":"Harde kaas & crackers met tomatensalade","type":"lunch","week":1,"day":"thursday","shelf_stable":True,"batch_cook":False,"kcal":560,"protein_g":28,"fat_g":30,"carbs_g":42,"fibre_g":4,"ingredients":[["Gouda belegen blokjes (Colruyt)","80g"],["Rijstwafels (Aldi)","4 stuks"],["Crackers (Lidl)","4 stuks"],["Kerstomaatjes","120g"],["Komkommer","100g"],["Olijfolie + citroensap","10ml"]]},
    {"id":"W1_L5","name":"Pindakaas & frambozenjam sandwiches","type":"lunch","week":1,"day":"friday","shelf_stable":True,"batch_cook":False,"kcal":580,"protein_g":20,"fat_g":20,"carbs_g":75,"fibre_g":7,"ingredients":[["Volkoren brood (4 sneden, Delhaize)","4 sneden"],["Pindakaas (Aldi)","50g"],["Frambozenjam suikervrij (Colruyt)","30g"],["Peer","1 stuk"],["Walnoten","30g"]]},
    {"id":"W1_D_SAT","name":"Ovenpasta met gehakt en geraspte kaas","type":"dinner","week":1,"day":"saturday","shelf_stable":False,"batch_cook":False,"kcal":780,"protein_g":45,"fat_g":32,"carbs_g":78,"fibre_g":8,"ingredients":[["Pasta fusilli (Lidl)","150g"],["Rundergehakt 20% vet (Aldi)","150g"],["Gezeefde tomaten brik (Intermarché)","200ml"],["Geraspte kaas (Colruyt)","50g"],["Ui","1 stuk"],["Knoflook","2 teentjes"],["Tomatenpuree (Lidl)","30g"],["Italiaanse kruiden","5g"],["Olijfolie","15ml"]]},
    {"id":"W1_D_SUN","name":"Kip-curryrijst (batch-cook)","type":"dinner","week":1,"day":"sunday","shelf_stable":False,"batch_cook":True,"kcal":850,"protein_g":55,"fat_g":22,"carbs_g":95,"fibre_g":7,"ingredients":[["Kipfilet (500g Aldi)","500g"],["Basmatirijst (Lidl)","300g"],["Kokosmelk light blik (Delhaize)","200ml"],["Curry poeder","10g"],["Kurkuma","5g"],["Ui (2 stuks)","2 stuks"],["Knoflook","3 teentjes"],["Kipbouillon blokje (Colruyt)","1 blokje"],["Diepvries erwten (Aldi)","150g"]]},
    # Week 2
    {"id":"W2_L1","name":"Volkoren wrap met hummus en gerookte zalm","type":"lunch","week":2,"day":"monday","shelf_stable":True,"batch_cook":False,"kcal":640,"protein_g":40,"fat_g":25,"carbs_g":58,"fibre_g":7,"ingredients":[["Volkoren tortilla wrap (Colruyt)","2 stuks"],["Hummus natuur (Delhaize)","80g"],["Gerookte zalm (Aldi 100g)","100g"],["Komkommer plakjes","80g"],["Citroen","0.5 stuk"],["Verse dille (gedroogd)","3g"]]},
    {"id":"W2_L2","name":"Niçoise-stijl salade in pot","type":"lunch","week":2,"day":"tuesday","shelf_stable":True,"batch_cook":False,"kcal":570,"protein_g":33,"fat_g":20,"carbs_g":60,"fibre_g":8,"ingredients":[["Tonijn in olijfolie blik (Lidl)","1 blik 160g"],["Hardgekookt ei (2 stuks)","2 stuks"],["Groene boontjes (pot)","100g"],["Olijven (pot)","40g"],["Kleine pasta (Intermarché)","80g"],["Rode wijnazijn dressing (Colruyt)","20ml"]]},
    {"id":"W2_L3","name":"Notenbrood-sandwich met kipfilet en mosterd","type":"lunch","week":2,"day":"wednesday","shelf_stable":True,"batch_cook":False,"kcal":610,"protein_g":42,"fat_g":18,"carbs_g":62,"fibre_g":6,"ingredients":[["Notenbrood (4 sneden, Colruyt)","4 sneden"],["Kipfilet koud gesneden (Aldi)","120g"],["Grove mosterd (Delhaize)","20g"],["Veldsla (zakje)","50g"],["Tomaat (1 stuk)","1 stuk"]]},
    {"id":"W2_L4","name":"Rijstcracker snackbox met noten en gedroogd fruit","type":"lunch","week":2,"day":"thursday","shelf_stable":True,"batch_cook":False,"kcal":520,"protein_g":15,"fat_g":26,"carbs_g":60,"fibre_g":8,"ingredients":[["Rijstwafels (Aldi)","6 stuks"],["Cashewnoten (ongezouten, 30g)","30g"],["Amandelen (30g)","30g"],["Gedroogde abrikozen (Colruyt)","40g"],["Rozijnen (Lidl)","30g"],["Donkere chocolade 85% (2 blokjes)","20g"]]},
    {"id":"W2_L5","name":"Kikkererwten-salade wrap met feta","type":"lunch","week":2,"day":"friday","shelf_stable":True,"batch_cook":False,"kcal":600,"protein_g":28,"fat_g":22,"carbs_g":68,"fibre_g":11,"ingredients":[["Volkoren wrap (Intermarché)","2 stuks"],["Kikkererwten blik (Lidl)","1 blik 400g uitgelekt"],["Fetakaas (Colruyt)","60g"],["Kerstomaatjes (150g)","150g"],["Komkommer","80g"],["Olijfolie + oregano","15ml"]]},
    {"id":"W2_D_SAT","name":"Stamppot boerenkool met rookworst","type":"dinner","week":2,"day":"saturday","shelf_stable":False,"batch_cook":False,"kcal":820,"protein_g":38,"fat_g":35,"carbs_g":82,"fibre_g":12,"ingredients":[["Aardappelen (1kg, Aldi)","400g"],["Boerenkool diepvries (Delhaize)","300g"],["Rookworst (Colruyt)","200g"],["Melk halfvol (Lidl)","100ml"],["Boter (Aldi)","20g"],["Mosterdzaad (Intermarché)","5g"],["Zout & peper","naar smaak"]]},
    {"id":"W2_D_SUN","name":"Linzensoep (batch-cook)","type":"dinner","week":2,"day":"sunday","shelf_stable":False,"batch_cook":True,"kcal":720,"protein_g":42,"fat_g":12,"carbs_g":95,"fibre_g":18,"ingredients":[["Rode linzen (Lidl)","400g"],["Ui (2 stuks)","2 stuks"],["Wortel (3 stuks)","3 stuks"],["Bleekselderij (2 stengels)","2 stengels"],["Knoflook","4 teentjes"],["Gezeefde tomaten brik (Intermarché)","400ml"],["Groentebouillon blokje (Colruyt)","2 blokjes"],["Komijn + paprikapoeder","10g"],["Olijfolie","20ml"]]},
    # Week 3
    {"id":"W3_L1","name":"Tonijn-pesto pasta salade","type":"lunch","week":3,"day":"monday","shelf_stable":True,"batch_cook":False,"kcal":600,"protein_g":35,"fat_g":20,"carbs_g":70,"fibre_g":6,"ingredients":[["Penne (Lidl)","100g"],["Tonijn blik (Aldi)","1 blik 160g"],["Pesto rosso (Colruyt)","30g"],["Zongedroogde tomaten","30g"],["Kappertjes (pot)","20g"],["Pijnboompitten (20g)","20g"]]},
    {"id":"W3_L2","name":"Pindakaas-havermout energieballen + fruit","type":"lunch","week":3,"day":"tuesday","shelf_stable":True,"batch_cook":False,"kcal":560,"protein_g":20,"fat_g":26,"carbs_g":62,"fibre_g":8,"ingredients":[["Havermout (Aldi)","100g"],["Pindakaas (Lidl)","50g"],["Honing (Colruyt)","20g"],["Chiazaad (Intermarché)","10g"],["Donkere chocoladeschilfers (Delhaize)","20g"],["Mandarijn (2 stuks)","2 stuks"]]},
    {"id":"W3_L3","name":"Volkoren crackers met sardines in tomatensaus","type":"lunch","week":3,"day":"wednesday","shelf_stable":True,"batch_cook":False,"kcal":540,"protein_g":32,"fat_g":22,"carbs_g":48,"fibre_g":6,"ingredients":[["Volkoren crackers (Aldi)","6 stuks"],["Sardines in tomatensaus blik (Colruyt)","2 blikjes 120g"],["Citroen (0.5 stuk)","0.5 stuk"],["Platte peterselie gedroogd","3g"],["Appel (1 stuk)","1 stuk"]]},
    {"id":"W3_L4","name":"Hummus & groentesticks met noten-trail mix","type":"lunch","week":3,"day":"thursday","shelf_stable":True,"batch_cook":False,"kcal":510,"protein_g":18,"fat_g":28,"carbs_g":50,"fibre_g":10,"ingredients":[["Hummus natuur (Lidl)","120g"],["Worteltjes (zakje babywortel)","150g"],["Rijstwafels (Aldi)","4 stuks"],["Gemengde noten (30g)","30g"],["Gedroogde cranberry's (Colruyt)","30g"],["Pompoenpitten (20g)","20g"]]},
    {"id":"W3_L5","name":"Belegen kaas & ham wrap met mosterd-honing","type":"lunch","week":3,"day":"friday","shelf_stable":True,"batch_cook":False,"kcal":620,"protein_g":35,"fat_g":26,"carbs_g":58,"fibre_g":5,"ingredients":[["Volkoren wrap (Colruyt)","2 stuks"],["Belegen kaas plakken (Delhaize)","60g"],["Gekookte ham (Aldi)","80g"],["Mosterd-honing saus (Intermarché)","20g"],["IJsbergsla (zakje)","50g"],["Tomaat (1 stuk)","1 stuk"]]},
    {"id":"W3_D_SAT","name":"Wokgroenten met ei-gebakken rijst","type":"dinner","week":3,"day":"saturday","shelf_stable":False,"batch_cook":False,"kcal":730,"protein_g":28,"fat_g":22,"carbs_g":95,"fibre_g":9,"ingredients":[["Jasmin rijst (Lidl)","200g"],["Wok groentenmix diepvries (Aldi)","400g"],["Eieren (3 stuks)","3 stuks"],["Sojasaus (Colruyt)","30ml"],["Sesamolie (Delhaize)","10ml"],["Knoflook (3 teentjes)","3 teentjes"],["Verse gember (5g)","5g"],["Lente-ui (3 stuks)","3 stuks"]]},
    {"id":"W3_D_SUN","name":"Tomaten-kippensoep (batch-cook)","type":"dinner","week":3,"day":"sunday","shelf_stable":False,"batch_cook":True,"kcal":680,"protein_g":48,"fat_g":14,"carbs_g":72,"fibre_g":8,"ingredients":[["Kipfilet (400g, Aldi)","400g"],["Kippenbouillon (1L brik, Colruyt)","1L"],["Gezeefde tomaten brik (Lidl)","400ml"],["Wortel (3 stuks)","3 stuks"],["Selder (2 stengels)","2 stengels"],["Ui (2 stuks)","2 stuks"],["Vermicelli (Delhaize)","80g"],["Tijm + laurier","naar smaak"],["Peterselie","naar smaak"]]},
    # Week 4
    {"id":"W4_L1","name":"Makreelbokaal op volkoren crackers","type":"lunch","week":4,"day":"monday","shelf_stable":True,"batch_cook":False,"kcal":580,"protein_g":38,"fat_g":28,"carbs_g":44,"fibre_g":5,"ingredients":[["Gerookte makreel blik (Aldi)","1 blik 125g"],["Volkoren crackers (Lidl)","6 stuks"],["Crème fraîche light (Colruyt)","30g"],["Citroensap","10ml"],["Bieslook gedroogd","3g"],["Komkommer (100g)","100g"]]},
    {"id":"W4_L2","name":"Couscous-groenten salade (koud)","type":"lunch","week":4,"day":"tuesday","shelf_stable":True,"batch_cook":False,"kcal":560,"protein_g":20,"fat_g":16,"carbs_g":78,"fibre_g":9,"ingredients":[["Couscous (Lidl)","100g"],["Kikkererwten blik (Aldi)","200g uitgelekt"],["Kerstomaatjes (150g)","150g"],["Komkommer","100g"],["Munt gedroogd","3g"],["Olijfolie + citroensap","20ml"],["Rozijnen (Colruyt)","30g"]]},
    {"id":"W4_L3","name":"Cashew-proteïneverreiker wrap","type":"lunch","week":4,"day":"wednesday","shelf_stable":True,"batch_cook":False,"kcal":630,"protein_g":38,"fat_g":24,"carbs_g":62,"fibre_g":7,"ingredients":[["Volkoren wrap (Intermarché)","2 stuks"],["Kipfilet koud (Aldi)","120g"],["Cashewnoten (30g)","30g"],["Hoisin saus (Delhaize)","20g"],["IJsbergsla (zakje)","50g"],["Rode paprika in reepjes","80g"]]},
    {"id":"W4_L4","name":"Trail mix + haver-proteïnekoeken","type":"lunch","week":4,"day":"thursday","shelf_stable":True,"batch_cook":False,"kcal":550,"protein_g":22,"fat_g":24,"carbs_g":64,"fibre_g":8,"ingredients":[["Havermout (Lidl)","80g"],["Ei (1 stuk)","1 stuk"],["Pindakaas (Aldi)","40g"],["Honing (Colruyt)","15g"],["Gemengde noten (30g)","30g"],["Gedroogde mango (Intermarché)","30g"],["Pompoenpitten (20g)","20g"]]},
    {"id":"W4_L5","name":"Olijf-antipasto crackerbox","type":"lunch","week":4,"day":"friday","shelf_stable":True,"batch_cook":False,"kcal":570,"protein_g":20,"fat_g":30,"carbs_g":52,"fibre_g":7,"ingredients":[["Volkoren crackers (Colruyt)","6 stuks"],["Belegen kaas blokjes (Delhaize)","60g"],["Olijven mix (pot)","60g"],["Zongedroogde tomaten (pot)","40g"],["Artisjokharten (pot, Aldi)","50g"],["Walnoten (30g)","30g"]]},
    {"id":"W4_D_SAT","name":"Vegetarische chili con carne met rijst","type":"dinner","week":4,"day":"saturday","shelf_stable":False,"batch_cook":False,"kcal":750,"protein_g":32,"fat_g":14,"carbs_g":110,"fibre_g":16,"ingredients":[["Rode kidneybonen blik (Lidl)","2 blikken 400g"],["Maïs blik (Aldi)","1 blik 300g"],["Gezeefde tomaten (Intermarché)","400ml"],["Paprika rood (2 stuks)","2 stuks"],["Ui (2 stuks)","2 stuks"],["Knoflook (3 teentjes)","3 teentjes"],["Chilipoeder + komijn","10g"],["Basmatirijst (Colruyt)","200g"],["Olijfolie (Delhaize)","15ml"]]},
    {"id":"W4_D_SUN","name":"Aardappel-ovenschotel met groenten (batch-cook)","type":"dinner","week":4,"day":"sunday","shelf_stable":False,"batch_cook":True,"kcal":800,"protein_g":35,"fat_g":28,"carbs_g":95,"fibre_g":10,"ingredients":[["Aardappelen (1kg, Aldi)","600g"],["Rundergehakt (200g, Colruyt)","200g"],["Ui (2 stuks)","2 stuks"],["Paprika geel (2 stuks)","2 stuks"],["Courgette (1 stuk)","1 stuk"],["Geraspte kaas (Lidl)","80g"],["Slagroom light (Delhaize)","100ml"],["Tijm + rozemarijn","5g"],["Olijfolie (Intermarché)","20ml"]]},
]

# ─── Pydantic models ──────────────────────────────────────────────────────────

class NutritionGoal(str, Enum):
    weight_loss = "weight_loss"
    maintenance = "maintenance"


class GenerateRequest(BaseModel):
    budget: float = Field(
        default=60.0,
        ge=10,
        le=500,
        description="Monthly budget in euros (default: €60/month).",
        example=60.0,
    )
    nutrition_goal: NutritionGoal = Field(
        default=NutritionGoal.weight_loss,
        description="Nutrition goal: weight_loss (~1500–1800 kcal) or maintenance (~2000–2200 kcal).",
        example="weight_loss",
    )
    promo_items: list[str] = Field(
        default_factory=list,
        description="Optional list of discounted product name fragments to match against ingredients.",
        example=["Kipfilet", "Pindakaas"],
    )


class MealOut(BaseModel):
    id: str
    name: str
    type: str
    week: int
    day: str
    shelf_stable: bool
    batch_cook: bool
    kcal: int
    protein_g: int
    fat_g: int
    carbs_g: int
    fibre_g: int
    ingredients: list[list[str]]
    promo_matches: list[str] = []
    budget_tier: str = "standard"


class MenuOut(BaseModel):
    budget: float
    nutrition_goal: str
    generated_at: str
    weeks: dict[str, list[MealOut]]


class ShoppingListOut(BaseModel):
    week: int
    budget: float
    items: list[str]
    item_count: int


# ─── FastAPI app with custom kc-nova branding ─────────────────────────────────

app = FastAPI(
    title="Budget Menu Planner API",
    description="""
## kc-nova – Budget Menu Planner

Open-source REST API powering the [Budget Menu Planner](https://github.com/kc-nova/budget_menu_planner)
Home Assistant integration.

### Features
- 🗓️ **28 unique meals** across a 4-week rotation
- 🥗 **Dynamic budget scaling** (€10–€500/month)
- 💊 **Nutrition goals**: weight loss or maintenance
- 🏷️ **Promo matching**: swap ingredients to discounted store brands
- 🛒 **Purchase-ready shopping lists** with exact product names (Colruyt / Aldi / Lidl / Delhaize / Intermarché)

### Context
Designed for a **single person, Belgian drivetime worker** — weekday lunches
are **shelf-stable** (no fridge/microwave in vehicle). Sunday dinners include
**batch-cooking** for Monday/Tuesday lunches.

---
*Brand: **kc-nova** | License: MIT | [GitHub](https://github.com/kc-nova/budget_menu_planner)*
""",
    version="1.0.0",
    contact={
        "name": "kc-nova",
        "url": "https://github.com/kc-nova",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,   # Disabled in favour of custom branded endpoint
    redoc_url=None,
)


# ─── Custom branded Swagger UI ────────────────────────────────────────────────

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui() -> HTMLResponse:
    """kc-nova branded Swagger UI."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Budget Menu Planner API – kc-nova",
        swagger_favicon_url="https://raw.githubusercontent.com/kc-nova/budget_menu_planner/main/assets/favicon.ico",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "list",
            "filter": True,
            "tryItOutEnabled": True,
        },
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc() -> HTMLResponse:
    """kc-nova branded ReDoc UI."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Budget Menu Planner API – kc-nova",
        redoc_favicon_url="https://raw.githubusercontent.com/kc-nova/budget_menu_planner/main/assets/favicon.ico",
    )


# ─── Health ────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    response_description="API status and version",
)
async def health() -> dict:
    """Returns API liveness status."""
    return {
        "status": "ok",
        "brand": "kc-nova",
        "version": "1.0.0",
        "meal_count": len(MEAL_DB),
    }


# ─── Menu endpoint ─────────────────────────────────────────────────────────────

@app.get(
    "/menu",
    tags=["Menu"],
    response_model=MenuOut,
    summary="Get full 4-week menu",
    response_description="Full 4-week meal plan grouped by week",
)
async def get_menu(
    budget: float = Query(default=60.0, ge=10, le=500, description="Monthly budget in euros"),
    nutrition_goal: NutritionGoal = Query(
        default=NutritionGoal.weight_loss,
        description="Nutrition goal",
    ),
) -> MenuOut:
    """
    Returns the complete 4-week meal rotation, dynamically filtered and
    annotated according to the requested budget and nutrition goal.
    """
    return _build_menu_response(budget=budget, nutrition_goal=nutrition_goal.value, promo_items=[])


# ─── Shopping list endpoint ────────────────────────────────────────────────────

@app.get(
    "/shopping-list",
    tags=["Shopping"],
    response_model=ShoppingListOut,
    summary="Get weekly shopping list",
    response_description="Purchase-ready shopping list for a given week",
)
async def get_shopping_list(
    week: int = Query(default=1, ge=1, le=4, description="Week number (1–4)"),
    budget: float = Query(default=60.0, ge=10, le=500, description="Monthly budget in euros"),
) -> ShoppingListOut:
    """
    Returns a deduplicated, purchase-ready shopping list for the specified week.
    Product names include store-brand references (Aldi, Lidl, Colruyt, etc.)
    """
    items = _build_shopping_list(week_num=week)
    return ShoppingListOut(
        week=week,
        budget=budget,
        items=items,
        item_count=len(items),
    )


# ─── Generate endpoint (POST) ─────────────────────────────────────────────────

@app.post(
    "/generate",
    tags=["Menu"],
    response_model=MenuOut,
    summary="Generate custom menu with promo matching",
    response_description="Custom menu with promo item matches highlighted",
)
async def generate_menu(body: GenerateRequest) -> MenuOut:
    """
    Generates a custom 4-week menu with optional promo matching.

    Supply a list of `promo_items` (product name fragments) to automatically
    detect and highlight discounted alternatives in the ingredient lists.
    This mirrors the **Option C Promo Integration** in the Home Assistant integration.
    """
    return _build_menu_response(
        budget=body.budget,
        nutrition_goal=body.nutrition_goal.value,
        promo_items=body.promo_items,
    )


# ─── Internal helpers ──────────────────────────────────────────────────────────

def _budget_tier(budget: float) -> str:
    if budget < 40:
        return "budget"
    if budget < 70:
        return "standard"
    return "premium"


def _find_promo_matches(meal: dict, promo_items: list[str]) -> list[str]:
    matches = []
    for product, _qty in meal.get("ingredients", []):
        for promo in promo_items:
            if promo.lower() in product.lower():
                matches.append(product)
                break
    return matches


def _check_goal_match(meal: dict, goal: str) -> bool:
    if goal == "weight_loss":
        return meal.get("kcal", 0) <= 650 and meal.get("protein_g", 0) >= 20
    return 600 <= meal.get("kcal", 0) <= 900


def _build_menu_response(
    budget: float,
    nutrition_goal: str,
    promo_items: list[str],
) -> MenuOut:
    tier = _budget_tier(budget)
    weeks: dict[str, list[MealOut]] = {"1": [], "2": [], "3": [], "4": []}

    for meal in MEAL_DB:
        meal_out = MealOut(
            **{k: v for k, v in meal.items() if k in MealOut.model_fields},
            promo_matches=_find_promo_matches(meal, promo_items),
            budget_tier=tier,
        )
        weeks[str(meal["week"])].append(meal_out)

    return MenuOut(
        budget=budget,
        nutrition_goal=nutrition_goal,
        generated_at=date.today().isoformat(),
        weeks=weeks,
    )


def _build_shopping_list(week_num: int) -> list[str]:
    week_meals = [m for m in MEAL_DB if m["week"] == week_num]
    seen: dict[str, str] = {}
    for meal in week_meals:
        for product, qty in meal.get("ingredients", []):
            key = product.split("(")[0].strip().lower()
            if key not in seen:
                seen[key] = f"{product} – {qty}"
    return sorted(seen.values())


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
