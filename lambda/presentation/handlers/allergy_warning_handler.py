from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from lambda.application.services.recipe_service import RecipeService
from lambda.domain.services.allergy_checker import AllergyChecker


class ProceedWithAllergenRecipeHandler(AbstractRequestHandler):
    def __init__(self, recipe_service: RecipeService):
        self.recipe_service = recipe_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        return (
            session_attr.get('pending_allergen_recipes') is not None
            and handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "AMAZON.YesIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        recipes_with_allergens = session_attr.get('pending_allergen_recipes', [])

        if not recipes_with_allergens:
            speak_output = "No hay recetas pendientes. ¿Qué te gustaría cocinar?"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )

        first_recipe = recipes_with_allergens[0]
        recipe_data = first_recipe['recipe']
        allergens = first_recipe['allergens']

        allergen_list = ', '.join(allergens.keys())

        speak_output = (
            f"Entendido. Recuerda que {recipe_data['title']} contiene {allergen_list}. "
            "Esta skill no se hace responsable por cualquier reacción alérgica. "
            "Por tu seguridad, te recomendamos consultar con un profesional de la salud. "
            f"¿Quieres que comencemos con la receta de {recipe_data['title']}?"
        )

        session_attr['displayed_recipes'] = [recipe_data]
        session_attr.pop('pending_allergen_recipes', None)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿Comenzamos a cocinar?")
                .response
        )


class DeclineAllergenRecipeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        return (
            session_attr.get('pending_allergen_recipes') is not None
            and handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "AMAZON.NoIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr.pop('pending_allergen_recipes', None)

        speak_output = (
            "Perfecto, es mejor ser precavido con las alergias. "
            "¿Quieres buscar otra receta con diferentes ingredientes?"
        )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿Qué ingredientes tienes disponibles?")
                .response
        )
