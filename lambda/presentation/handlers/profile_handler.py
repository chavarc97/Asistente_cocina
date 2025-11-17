from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from lambda.application.services.user_service import UserService


class AddAllergyIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "AddAllergyIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        slots = handler_input.request_envelope.request.intent.slots

        allergen = slots.get("allergen")
        if not allergen or not allergen.value:
            speak_output = "No entendí a qué eres alérgico. ¿Puedes repetirlo?"
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

        allergen_value = allergen.value
        user = self.user_service.get_or_create_user(user_id)

        success = user.add_allergy(allergen_value)

        if success:
            self.user_service.update_user(user)
            speak_output = f"He registrado tu alergia a {allergen_value}. Evitaré recetas con este ingrediente."
        else:
            speak_output = f"Ya tenías registrada la alergia a {allergen_value}, o no reconozco ese alérgeno."

        return handler_input.response_builder.speak(speak_output).response


class RemoveAllergyIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "RemoveAllergyIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        slots = handler_input.request_envelope.request.intent.slots

        allergen = slots.get("allergen")
        if not allergen or not allergen.value:
            speak_output = "No entendí qué alergia quieres eliminar. ¿Puedes repetirlo?"
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

        allergen_value = allergen.value
        user = self.user_service.get_or_create_user(user_id)

        success = user.remove_allergy(allergen_value)

        if success:
            self.user_service.update_user(user)
            speak_output = f"He eliminado la alergia a {allergen_value} de tu perfil."
        else:
            speak_output = f"No encontré la alergia a {allergen_value} en tu perfil."

        return handler_input.response_builder.speak(speak_output).response


class ListAllergiesIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "ListAllergiesIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        user = self.user_service.get_or_create_user(user_id)

        if not user.allergies:
            speak_output = "No tienes alergias registradas en tu perfil."
        elif len(user.allergies) == 1:
            speak_output = f"Tienes registrada una alergia a {user.allergies[0]}."
        else:
            allergies_list = ", ".join(user.allergies[:-1])
            speak_output = f"Tienes registradas alergias a {allergies_list} y {user.allergies[-1]}."

        return handler_input.response_builder.speak(speak_output).response


class SetDietaryRestrictionIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "SetDietaryRestrictionIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        slots = handler_input.request_envelope.request.intent.slots

        diet = slots.get("diet")
        if not diet or not diet.value:
            speak_output = "No entendí qué tipo de dieta sigues. ¿Puedes repetirlo?"
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

        diet_value = diet.value
        user = self.user_service.get_or_create_user(user_id)

        success = user.set_dietary_restriction(diet_value)

        if success:
            self.user_service.update_user(user)
            if diet_value.lower() in ['ninguna', 'normal', 'sin restricciones']:
                speak_output = "He eliminado las restricciones dietéticas de tu perfil."
            else:
                speak_output = f"He configurado tu dieta como {diet_value}. Buscaré recetas compatibles."
        else:
            speak_output = f"No reconozco la dieta {diet_value}. Intenta con vegetariana, vegana, cetogénica, paleo, sin gluten o mediterránea."

        return handler_input.response_builder.speak(speak_output).response


class SetServingsIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "SetServingsIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        slots = handler_input.request_envelope.request.intent.slots

        servings = slots.get("servings")
        if not servings or not servings.value:
            speak_output = "No entendí para cuántas personas cocinas. ¿Puedes repetirlo?"
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

        try:
            servings_value = int(servings.value)
        except ValueError:
            speak_output = "No entendí el número de porciones. Por favor, di un número entre 1 y 12."
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

        user = self.user_service.get_or_create_user(user_id)
        success = user.set_servings(servings_value)

        if success:
            self.user_service.update_user(user)
            speak_output = f"He configurado las recetas para {servings_value} personas."
        else:
            speak_output = "El número de porciones debe estar entre 1 y 12."

        return handler_input.response_builder.speak(speak_output).response


class GetProfileIntentHandler(AbstractRequestHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            handler_input.request_envelope.request.type == "IntentRequest"
            and handler_input.request_envelope.request.intent.name == "GetProfileIntent"
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        user_id = handler_input.request_envelope.session.user.user_id
        user = self.user_service.get_or_create_user(user_id)

        profile_parts = []

        if user.dietary_restrictions and user.dietary_restrictions[0] != 'ninguna':
            diet = user.dietary_restrictions[0]
            profile_parts.append(f"dieta {diet}")

        if user.allergies:
            if len(user.allergies) == 1:
                profile_parts.append(f"alergia a {user.allergies[0]}")
            else:
                allergies_list = ", ".join(user.allergies[:-1])
                profile_parts.append(f"alergias a {allergies_list} y {user.allergies[-1]}")

        profile_parts.append(f"{user.servings} porciones")

        if profile_parts:
            speak_output = "Tu perfil tiene: " + ", ".join(profile_parts) + "."
        else:
            speak_output = "Aún no tienes preferencias configuradas."

        return handler_input.response_builder.speak(speak_output).response
