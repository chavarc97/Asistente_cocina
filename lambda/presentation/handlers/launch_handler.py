from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from lambda.application.services.user_service import UserService


class LaunchRequestHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.context.system.user.user_id
        user = self.user_service.get_or_create_user(user_id)

        if not user.dietary_restrictions and not user.skill_level:
            speak_output = ("¡Hola! Bienvenido a Chef Personal, tu asistente culinario inteligente. "
                          "Antes de comenzar, me gustaría conocer tus preferencias culinarias. "
                          "¿Tienes alguna restricción alimentaria como vegetariano, vegano, sin gluten, o alguna alergia?")
        else:
            speak_output = (f"¡Hola de nuevo! ¿Qué te gustaría cocinar hoy? "
                          "Puedo ayudarte a buscar recetas por ingredientes, "
                          "mostrarte tus favoritas, o guiarte paso a paso en la cocina.")

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
