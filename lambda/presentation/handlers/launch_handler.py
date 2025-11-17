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

        session_attr = handler_input.attributes_manager.session_attributes

        if not user.allergies and session_attr.get('allergies_asked') != 'true':
            session_attr['awaiting_allergies'] = 'true'
            session_attr['allergies_asked'] = 'true'
            speak_output = (
                "¡Bienvenido a Chef Personal! Soy tu asistente culinario inteligente. "
                "Para brindarte la mejor experiencia, ¿tienes alguna alergia alimentaria que deba tener en cuenta? "
                "Por ejemplo: cacahuetes, nueces, leche, huevos, mariscos. "
                "Si no tienes alergias, solo di 'ninguna'."
            )
        else:
            speak_output = (
                "¡Hola! ¿Qué te gustaría cocinar hoy? "
                "Puedo ayudarte a buscar recetas por ingredientes, "
                "mostrarte tus favoritas, o guiarte paso a paso en la cocina."
            )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
