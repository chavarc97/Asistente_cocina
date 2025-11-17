import os
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from lambda.infrastructure.database.dynamodb_client import DynamoDBClient
from lambda.infrastructure.repositories.dynamodb_user_repository import DynamoDBUserRepository
from lambda.infrastructure.repositories.dynamodb_recipe_repository import DynamoDBRecipeRepository
from lambda.infrastructure.repositories.dynamodb_session_repository import DynamoDBSessionRepository
from lambda.infrastructure.external.spoonacular_client import SpoonacularClient
from lambda.infrastructure.persistence.dynamodb_persistence_adapter import AlexaDynamoDBPersistenceAdapter

from lambda.application.services.user_service import UserService
from lambda.application.services.recipe_service import RecipeService
from lambda.application.services.session_service import SessionService

from lambda.presentation.handlers.launch_handler import LaunchRequestHandler
from lambda.presentation.handlers.search_handler import SearchByIngredientsIntentHandler
from lambda.presentation.handlers.cooking_handler import (
    StartCookingIntentHandler,
    NextStepIntentHandler,
    RepeatStepIntentHandler,
    PauseCookingIntentHandler,
    ResumeCookingIntentHandler
)
from lambda.presentation.handlers.profile_handler import (
    AddAllergyIntentHandler,
    RemoveAllergyIntentHandler,
    ListAllergiesIntentHandler,
    SetDietaryRestrictionIntentHandler,
    SetServingsIntentHandler,
    GetProfileIntentHandler
)
from lambda.presentation.handlers.onboarding_handler import (
    CaptureAllergiesIntentHandler,
    NoAllergyIntentHandler
)
from lambda.presentation.handlers.allergy_warning_handler import (
    ProceedWithAllergenRecipeHandler,
    DeclineAllergenRecipeHandler
)


region = os.getenv('AWS_REGION', 'us-east-1')

db_client = DynamoDBClient(region_name=region)

user_repository = DynamoDBUserRepository(db_client)
recipe_repository = DynamoDBRecipeRepository(db_client)
session_repository = DynamoDBSessionRepository(db_client)

user_service = UserService(user_repository)
recipe_service = RecipeService(recipe_repository)
session_service = SessionService(session_repository)

api_key = os.getenv('SPOONACULAR_API_KEY')
spoonacular_client = SpoonacularClient(api_key)

persistence_adapter = AlexaDynamoDBPersistenceAdapter(
    table_name='AlexaSessionAttributes',
    region_name=region
)


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent"

    def handle(self, handler_input):
        speak_output = ("Puedo ayudarte a buscar recetas por ingredientes, "
                       "mostrarte tus favoritas, o guiarte paso a paso mientras cocinas. "
                       "¿Qué te gustaría hacer?")
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent" or
                handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent")

    def handle(self, handler_input):
        speak_output = "¡Hasta luego! Que disfrutes tu comida."
        return handler_input.response_builder.speak(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "SessionEndedRequest"

    def handle(self, handler_input):
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        speak_output = "Lo siento, tuve problemas procesando tu solicitud. ¿Puedes intentar de nuevo?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = CustomSkillBuilder(persistence_adapter=persistence_adapter.get_adapter())

sb.add_request_handler(LaunchRequestHandler(user_service))
sb.add_request_handler(CaptureAllergiesIntentHandler(user_service))
sb.add_request_handler(NoAllergyIntentHandler(user_service))
sb.add_request_handler(ProceedWithAllergenRecipeHandler(recipe_service))
sb.add_request_handler(DeclineAllergenRecipeHandler())
sb.add_request_handler(SearchByIngredientsIntentHandler(user_service, recipe_service, spoonacular_client))
sb.add_request_handler(StartCookingIntentHandler(session_service, recipe_service))
sb.add_request_handler(NextStepIntentHandler(session_service, recipe_service))
sb.add_request_handler(RepeatStepIntentHandler(session_service, recipe_service))
sb.add_request_handler(PauseCookingIntentHandler(session_service))
sb.add_request_handler(ResumeCookingIntentHandler(session_service, recipe_service))
sb.add_request_handler(AddAllergyIntentHandler(user_service))
sb.add_request_handler(RemoveAllergyIntentHandler(user_service))
sb.add_request_handler(ListAllergiesIntentHandler(user_service))
sb.add_request_handler(SetDietaryRestrictionIntentHandler(user_service))
sb.add_request_handler(SetServingsIntentHandler(user_service))
sb.add_request_handler(GetProfileIntentHandler(user_service))
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
