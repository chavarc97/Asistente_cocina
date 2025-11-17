from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from lambda.application.services.user_service import UserService
from lambda.application.services.recipe_service import RecipeService
from lambda.infrastructure.external.spoonacular_client import SpoonacularClient
from lambda.domain.services.allergy_checker import AllergyChecker


class SearchByIngredientsIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService, recipe_service: RecipeService,
                 api_client: SpoonacularClient):
        self.user_service = user_service
        self.recipe_service = recipe_service
        self.api_client = api_client

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("SearchByIngredientsIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.context.system.user.user_id
        user = self.user_service.get_or_create_user(user_id)

        slots = handler_input.request_envelope.request.intent.slots
        ingredients = []

        for i in range(1, 6):
            slot_name = f"ingredient{i}"
            if slot_name in slots and slots[slot_name].value:
                ingredients.append(slots[slot_name].value)

        if not ingredients:
            speak_output = "No escuché ningún ingrediente. ¿Qué ingredientes tienes disponibles?"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )

        try:
            diet = user.dietary_restrictions[0] if user.dietary_restrictions else None
            results = self.api_client.search_by_ingredients(ingredients, number=5, diet=diet)

            if not results:
                speak_output = f"No encontré recetas con {', '.join(ingredients)}. ¿Quieres probar con otros ingredientes?"
                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .ask(speak_output)
                        .response
                )

            session_attributes = handler_input.attributes_manager.session_attributes
            session_attributes['search_results'] = results
            session_attributes['user_allergies'] = user.allergies

            safe_recipes = []
            recipes_with_allergens = []

            for result in results:
                recipe_ingredients = [ing.get('name', '') for ing in result.get('usedIngredients', [])]
                recipe_ingredients.extend([ing.get('name', '') for ing in result.get('missedIngredients', [])])

                if user.allergies:
                    allergens_found = AllergyChecker.check_recipe_for_allergens(recipe_ingredients, user.allergies)
                    if allergens_found:
                        recipes_with_allergens.append({
                            'recipe': result,
                            'allergens': allergens_found
                        })
                    else:
                        safe_recipes.append(result)
                else:
                    safe_recipes.append(result)

            if safe_recipes:
                recipes_text = []
                for idx, result in enumerate(safe_recipes[:3], 1):
                    recipe_desc = self._format_recipe_description(result)
                    recipes_text.append(f"{idx}. {recipe_desc}")

                speak_output = (
                    f"Encontré {len(safe_recipes)} recetas seguras con {', '.join(ingredients)}. "
                    f"Las mejores opciones son: {'. '.join(recipes_text)}. "
                    "¿Cuál te interesa?"
                )
                session_attributes['displayed_recipes'] = safe_recipes[:3]
            elif recipes_with_allergens:
                session_attributes['pending_allergen_recipes'] = recipes_with_allergens[:3]
                first_recipe = recipes_with_allergens[0]
                allergen_warning = AllergyChecker.format_allergen_warning(first_recipe['allergens'])

                speak_output = (
                    f"Encontré recetas con {', '.join(ingredients)}, pero contienen ingredientes a los que eres alérgico. "
                    f"Por ejemplo, {first_recipe['recipe']['title']}. {allergen_warning}. "
                    "¿Quieres ver esta receta de todos modos? Ten en cuenta que esta skill no se hace responsable por reacciones alérgicas."
                )
            else:
                speak_output = f"No encontré recetas compatibles con {', '.join(ingredients)}. ¿Quieres probar con otros ingredientes?"

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("¿Qué te gustaría hacer?")
                    .response
            )

        except Exception as e:
            speak_output = "Lo siento, tuve problemas para buscar recetas. ¿Quieres intentar de nuevo?"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )

    def _format_recipe_description(self, recipe: dict) -> str:
        title = recipe.get('title', 'Receta')
        ready_time = recipe.get('readyInMinutes', 0)
        dish_types = recipe.get('dishTypes', [])
        cuisines = recipe.get('cuisines', [])

        parts = [title]

        if dish_types and len(dish_types) > 0:
            dish_type = dish_types[0].replace('-', ' ')
            parts.append(f"un {dish_type}")

        if cuisines and len(cuisines) > 0:
            cuisine = cuisines[0]
            parts.append(f"de cocina {cuisine}")

        if ready_time > 0:
            if ready_time < 30:
                parts.append("listo en menos de 30 minutos")
            elif ready_time < 60:
                parts.append(f"listo en {ready_time} minutos")
            else:
                hours = ready_time // 60
                minutes = ready_time % 60
                if minutes == 0:
                    parts.append(f"listo en {hours} {'hora' if hours == 1 else 'horas'}")
                else:
                    parts.append(f"listo en {hours}h {minutes}min")

        if len(parts) == 1:
            return title

        return f"{parts[0]}, {', '.join(parts[1:])}"
