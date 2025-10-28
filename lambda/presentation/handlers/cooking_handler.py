from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from lambda.application.services.session_service import SessionService
from lambda.application.services.recipe_service import RecipeService


class StartCookingIntentHandler(AbstractRequestHandler):
    def __init__(self, session_service: SessionService, recipe_service: RecipeService):
        self.session_service = session_service
        self.recipe_service = recipe_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("StartCookingIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.context.system.user.user_id
        session_attrs = handler_input.attributes_manager.session_attributes

        recipe_id = session_attrs.get('selected_recipe_id')
        if not recipe_id:
            speak_output = "Primero debes seleccionar una receta. ¿Qué te gustaría cocinar?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        recipe = self.recipe_service.get_recipe(recipe_id)
        if not recipe:
            speak_output = "No pude cargar la receta. ¿Quieres buscar otra?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        cooking_session = self.session_service.create_session(user_id, recipe_id)
        self.session_service.start_cooking(cooking_session.session_id)

        session_attrs['cooking_session_id'] = cooking_session.session_id

        first_step = recipe.steps[0] if recipe.steps else None
        if first_step:
            speak_output = (f"Perfecto, comenzamos con {recipe.title}. "
                          f"Paso 1: {first_step.instruction}. "
                          "Dime 'siguiente' cuando estés listo para continuar.")
        else:
            speak_output = "Esta receta no tiene pasos definidos."

        return handler_input.response_builder.speak(speak_output).ask("¿Listo para continuar?").response


class NextStepIntentHandler(AbstractRequestHandler):
    def __init__(self, session_service: SessionService, recipe_service: RecipeService):
        self.session_service = session_service
        self.recipe_service = recipe_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("NextStepIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attrs = handler_input.attributes_manager.session_attributes
        session_id = session_attrs.get('cooking_session_id')

        if not session_id:
            speak_output = "No hay una sesión de cocina activa. ¿Quieres empezar a cocinar algo?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        cooking_session = self.session_service.session_repository.get_by_id(session_id)
        recipe = self.recipe_service.get_recipe(cooking_session.recipe_id)

        current_step = self.session_service.next_step(session_id)

        if current_step >= len(recipe.steps):
            self.session_service.complete_session(session_id)
            speak_output = (f"¡Felicidades! Has completado {recipe.title}. "
                          "¿Cómo quedó? Puedes calificar esta receta del 1 al 5.")
        else:
            step = recipe.steps[current_step]
            speak_output = f"Paso {current_step + 1}: {step.instruction}. Dime 'siguiente' para continuar."

        return handler_input.response_builder.speak(speak_output).ask("¿Necesitas algo más?").response


class RepeatStepIntentHandler(AbstractRequestHandler):
    def __init__(self, session_service: SessionService, recipe_service: RecipeService):
        self.session_service = session_service
        self.recipe_service = recipe_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attrs = handler_input.attributes_manager.session_attributes
        session_id = session_attrs.get('cooking_session_id')

        if not session_id:
            speak_output = "No hay una sesión de cocina activa."
            return handler_input.response_builder.speak(speak_output).response

        cooking_session = self.session_service.session_repository.get_by_id(session_id)
        recipe = self.recipe_service.get_recipe(cooking_session.recipe_id)

        current_step_num = cooking_session.current_step
        if current_step_num < len(recipe.steps):
            step = recipe.steps[current_step_num]
            speak_output = f"Paso {current_step_num + 1}: {step.instruction}"
        else:
            speak_output = "Ya completaste todos los pasos."

        return handler_input.response_builder.speak(speak_output).ask("¿Listo para continuar?").response
