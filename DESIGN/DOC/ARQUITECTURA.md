# Arquitectura del Sistema - Chef Personal

## Diagrama C4 - Nivel 1: Contexto del Sistema

```mermaid
graph TB
    Usuario[Usuario con Alexa]
    ChefPersonal[Skill Chef Personal]
    Spoonacular[Spoonacular API]
    MealDB[TheMealDB API]

    Usuario -->|Comandos de voz| ChefPersonal
    ChefPersonal -->|Respuestas de voz| Usuario
    ChefPersonal -->|Búsqueda de recetas| Spoonacular
    ChefPersonal -->|Backup de recetas| MealDB
```

## Diagrama C4 - Nivel 2: Contenedores

```mermaid
graph TB
    subgraph "Amazon Alexa"
        AVS[Alexa Voice Service]
    end

    subgraph "AWS Cloud"
        Lambda[AWS Lambda<br/>Python 3.11]
        DynamoDB[(DynamoDB)]
        CloudWatch[CloudWatch Logs]
        SecretsManager[Secrets Manager]
    end

    subgraph "APIs Externas"
        Spoonacular[Spoonacular API]
        MealDB[TheMealDB API]
    end

    AVS <-->|JSON/HTTPS| Lambda
    Lambda -->|Read/Write| DynamoDB
    Lambda -->|Logs| CloudWatch
    Lambda -->|API Keys| SecretsManager
    Lambda -->|HTTP| Spoonacular
    Lambda -->|HTTP| MealDB
```

## Diagrama C4 - Nivel 3: Componentes

```mermaid
graph TB
    subgraph "Lambda Function"
        subgraph "Handlers Layer"
            LaunchHandler[Launch Handler]
            SearchHandler[Search Handler]
            CookingHandler[Cooking Handler]
            FavoritesHandler[Favorites Handler]
            ProfileHandler[Profile Handler]
        end

        subgraph "Services Layer"
            RecipeService[Recipe Service]
            UserService[User Service]
            RecommendationService[Recommendation Service]
            SessionService[Session Service]
        end

        subgraph "Infrastructure Layer"
            DynamoDBRepo[DynamoDB Repository]
            APIClient[API Client]
            CacheManager[Cache Manager]
            SSMLBuilder[SSML Builder]
        end

        subgraph "Domain Layer"
            UserModel[User Model]
            RecipeModel[Recipe Model]
            SessionModel[Session Model]
        end
    end

    LaunchHandler --> UserService
    SearchHandler --> RecipeService
    CookingHandler --> SessionService
    FavoritesHandler --> UserService
    ProfileHandler --> UserService

    RecipeService --> APIClient
    RecipeService --> CacheManager
    UserService --> DynamoDBRepo
    SessionService --> DynamoDBRepo
    RecommendationService --> DynamoDBRepo

    DynamoDBRepo --> UserModel
    DynamoDBRepo --> RecipeModel
    DynamoDBRepo --> SessionModel
```

## Diagrama de Secuencia - Búsqueda de Receta

```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as Alexa
    participant L as Lambda
    participant RS as RecipeService
    participant API as Spoonacular API
    participant DB as DynamoDB

    U->>A: "Tengo pollo y arroz"
    A->>L: SearchByIngredientsIntent
    L->>DB: Obtener perfil de usuario
    DB-->>L: UserProfile
    L->>RS: search_recipes(ingredients, profile)
    RS->>API: GET /recipes/complexSearch
    API-->>RS: Recipe List
    RS->>DB: Cache recipes
    RS-->>L: Filtered recipes
    L->>A: Response con 3 opciones
    A->>U: "Encontré 3 recetas..."
```

## Diagrama de Secuencia - Modo Cocina

```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as Alexa
    participant L as Lambda
    participant SS as SessionService
    participant DB as DynamoDB

    U->>A: "Comienza a cocinar"
    A->>L: StartCookingIntent
    L->>SS: create_session(recipe_id, user_id)
    SS->>DB: Save session state
    L->>A: Response con primer paso
    A->>U: "Paso 1: ..."

    loop Cada paso
        U->>A: "Siguiente"
        A->>L: NextStepIntent
        L->>SS: advance_step()
        SS->>DB: Update session
        L->>A: Response con siguiente paso
        A->>U: "Paso N: ..."
    end
```

## Diagrama de Estados - Sesión de Cocina

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Searching: SearchIntent
    Searching --> RecipeSelected: Selecciona receta
    RecipeSelected --> Cooking: StartCookingIntent

    Cooking --> Paused: PauseIntent
    Paused --> Cooking: ResumeIntent

    Cooking --> Cooking: NextStep/RepeatStep
    Cooking --> Completed: Último paso

    Completed --> Idle: RateRecipe

    Searching --> Idle: CancelIntent
    RecipeSelected --> Idle: CancelIntent
    Paused --> Idle: CancelIntent
```

## Arquitectura de Capas

```mermaid
graph TB
    subgraph "Presentation Layer"
        Handlers[Intent Handlers]
    end

    subgraph "Application Layer"
        Services[Business Services]
    end

    subgraph "Domain Layer"
        Models[Domain Models]
        Interfaces[Repository Interfaces]
    end

    subgraph "Infrastructure Layer"
        Repositories[Repository Implementations]
        External[External API Clients]
        Utils[Utilities]
    end

    Handlers --> Services
    Services --> Models
    Services --> Interfaces
    Interfaces --> Repositories
    Services --> External
    Repositories --> Utils
```

## Flujo de Datos

```mermaid
flowchart LR
    A[Alexa Request] --> B[Router]
    B --> C{Intent Type}

    C -->|Launch| D[LaunchHandler]
    C -->|Search| E[SearchHandler]
    C -->|Cooking| F[CookingHandler]
    C -->|Favorites| G[FavoritesHandler]

    D --> H[UserService]
    E --> I[RecipeService]
    F --> J[SessionService]
    G --> H

    I --> K[APIClient]
    H --> L[DynamoDB]
    J --> L

    K --> M[Cache]
    M --> N[Response Builder]
    L --> N

    N --> O[Alexa Response]
```
