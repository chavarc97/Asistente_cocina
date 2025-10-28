from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from lambda.application.services.user_service import UserService
from lambda.application.services.recipe_service import RecipeService
from lambda.infrastructure.external.spoonacular_client import SpoonacularClient


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
            results = self.api_client.search_by_ingredients(ingredients, number=3, diet=diet)

            if not results:
                speak_output = f"No encontré recetas con {', '.join(ingredients)}. ¿Quieres probar con otros ingredientes?"
            else:
                recipes_text = []
                for idx, result in enumerate(results[:3], 1):
                    recipes_text.append(f"{idx}. {result['title']}")

                speak_output = (f"Encontré {len(results)} recetas con {', '.join(ingredients)}. "
                              f"Las más populares son: {', '.join(recipes_text)}. "
                              "¿Cuál te interesa?")

                session_attributes = handler_input.attributes_manager.session_attributes
                session_attributes['search_results'] = results

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("¿Cuál receta te gustaría preparar?")
                    .response
            )

        except Exception as e:
            speak_output = "Lo siento, tuve problemas para buscar recetas. ¿Quieres ver tus favoritas?"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
