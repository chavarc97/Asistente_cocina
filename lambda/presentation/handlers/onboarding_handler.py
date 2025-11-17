from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from lambda.application.services.user_service import UserService
from lambda.domain.validators.allergy_validator import AllergyValidator


class CaptureAllergiesIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        return (
            session_attr.get('awaiting_allergies') == 'true'
            and handler_input.request_envelope.request.type == "IntentRequest"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes

        allergen = slots.get("allergen") if slots else None

        if allergen and allergen.value and allergen.value.lower() not in ['ninguna', 'no', 'no tengo']:
            user = self.user_service.get_or_create_user(user_id)
            allergen_value = allergen.value

            success = user.add_allergy(allergen_value)

            if success:
                self.user_service.update_user(user)
                session_attr['awaiting_allergies'] = 'false'
                speak_output = (
                    f"Perfecto, he registrado tu alergia a {allergen_value}. "
                    "Evitaré recetas con este ingrediente. "
                    "Si tienes más alergias, puedes agregarlas diciendo 'soy alérgico a' seguido del ingrediente. "
                    "Ahora, ¿qué te gustaría cocinar?"
                )
            else:
                speak_output = (
                    f"No reconozco el alérgeno {allergen_value}. "
                    "¿Puedes intentar con otro término? "
                    "Por ejemplo: cacahuetes, nueces, leche, huevos, pescado, mariscos."
                )
        else:
            session_attr['awaiting_allergies'] = 'false'
            speak_output = (
                "Perfecto, no tienes alergias registradas. "
                "Puedes agregar alergias en cualquier momento diciendo 'soy alérgico a' seguido del ingrediente. "
                "Ahora, ¿qué te gustaría cocinar?"
            )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿En qué puedo ayudarte?")
                .response
        )


class NoAllergyIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        return (
            session_attr.get('awaiting_allergies') == 'true'
            and handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name in ["AMAZON.NoIntent", "NoAllergyIntent"]
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['awaiting_allergies'] = 'false'

        speak_output = (
            "Perfecto, no registraré alergias. "
            "Puedes agregar alergias en cualquier momento. "
            "¿Qué te gustaría cocinar hoy?"
        )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿En qué puedo ayudarte?")
                .response
        )
