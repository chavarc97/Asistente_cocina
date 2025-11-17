# Bienvenido a Chef Personal 👋

Este documento te ayudará a entender rápidamente cómo funciona el proyecto y cómo empezar a trabajar en él.

## ¿Qué es Chef Personal?

Es una **Alexa Skill** que ayuda a las personas a cocinar. El usuario habla con Alexa y:
- Busca recetas basadas en ingredientes que tiene en casa
- Recibe guías paso a paso mientras cocina
- El sistema recuerda sus alergias y preferencias dietéticas

**Ejemplo de uso:**
```
Usuario: "Alexa, abre chef personal"
Alexa: "Bienvenido, ¿tienes alguna alergia?"
Usuario: "Soy alérgico a los cacahuetes"
Alexa: "Entendido, lo guardaré"
Usuario: "Tengo pollo y arroz"
Alexa: "Encontré 3 recetas: 1. Arroz con Pollo..."
Usuario: "La primera"
Alexa: "Paso 1: Calienta el aceite en una sartén..."
```

## Tecnologías Principales

| Tecnología | Para qué sirve |
|------------|----------------|
| **Python 3.11** | Lenguaje de programación |
| **AWS Lambda** | Ejecuta el código cuando Alexa lo necesita |
| **DynamoDB** | Base de datos para guardar usuarios, recetas y sesiones |
| **Alexa Skills Kit** | Framework para crear skills de Alexa |
| **Spoonacular API** | De donde obtenemos las recetas |

## Arquitectura Simplificada

```
Usuario habla → Alexa → AWS Lambda → Spoonacular API
                           ↓
                      DynamoDB (guarda datos)
```

### Flujo de una búsqueda de receta:

1. **Usuario dice:** "Tengo pollo y arroz"
2. **Alexa recibe** el audio y lo convierte a texto
3. **Lambda se activa** y procesa la solicitud
4. **Lambda pregunta a DynamoDB:** "¿Tiene alergias este usuario?"
5. **Lambda pregunta a Spoonacular:** "Dame recetas con pollo y arroz"
6. **Lambda filtra** las recetas que contengan alergias
7. **Lambda responde a Alexa** con 3 opciones seguras
8. **Alexa le dice al usuario** las recetas

## Estructura del Código

El código sigue una **arquitectura en capas** (como un pastel de capas):

```
📁 lambda/
├── 📁 presentation/      ← Capa 1: Handlers (reciben comandos de Alexa)
├── 📁 application/       ← Capa 2: Services (lógica de negocio)
├── 📁 domain/           ← Capa 3: Models (definición de datos)
└── 📁 infrastructure/   ← Capa 4: Repositories y APIs (hablan con BD y APIs)
```

### ¿Por qué estas capas?

**Cada capa tiene una responsabilidad:**

1. **Presentation (Handlers)**: Escuchan a Alexa
   - `launch_handler.py`: Cuando abres la skill
   - `search_handler.py`: Cuando buscas recetas
   - `cooking_handler.py`: Cuando estás cocinando

2. **Application (Services)**: Contienen la lógica
   - `recipe_service.py`: Buscar y guardar recetas
   - `user_service.py`: Gestionar usuarios y alergias
   - `session_service.py`: Controlar sesiones de cocina

3. **Domain (Models)**: Definen qué es cada cosa
   - `user.py`: Qué información tiene un usuario
   - `recipe.py`: Qué información tiene una receta

4. **Infrastructure**: Conexiones externas
   - `spoonacular_client.py`: Habla con la API de recetas
   - `dynamodb_*_repository.py`: Habla con la base de datos

## Ejemplo Práctico: ¿Qué pasa cuando buscas recetas?

```python
# 1. HANDLER (escucha a Alexa)
# lambda/presentation/handlers/search_handler.py
class SearchByIngredientsIntentHandler:
    def handle(self, handler_input):
        # Usuario dijo: "Tengo pollo y arroz"
        ingredients = ["pollo", "arroz"]

        # 2. Llama al SERVICE
        recipes = self.recipe_service.search_by_ingredients(
            ingredients,
            user_id
        )

        # 5. Responde a Alexa
        return "Encontré 3 recetas: ..."
```

```python
# 2. SERVICE (lógica de negocio)
# lambda/application/services/recipe_service.py
class RecipeService:
    def search_by_ingredients(self, ingredients, user_id):
        # Obtener alergias del usuario
        user = self.user_service.get_user(user_id)

        # 3. Llamar a la API externa
        recipes = self.spoonacular_client.search(ingredients)

        # Filtrar recetas con alergias
        safe_recipes = [r for r in recipes
                       if not has_allergens(r, user.allergies)]

        # 4. Guardar en base de datos
        self.recipe_repository.save_all(safe_recipes)

        return safe_recipes
```

```python
# 3. INFRASTRUCTURE (habla con APIs)
# lambda/infrastructure/external/spoonacular_client.py
class SpoonacularClient:
    def search(self, ingredients):
        # Llamada HTTP a Spoonacular
        response = requests.get(
            f"{API_URL}/recipes/findByIngredients",
            params={"ingredients": ",".join(ingredients)}
        )
        return response.json()
```

## Conceptos Clave

### 1. Intents (Intenciones)
Son los comandos que Alexa reconoce. Ejemplos:
- `SearchByIngredientsIntent`: Usuario busca recetas
- `StartCookingIntent`: Usuario quiere empezar a cocinar
- `NextStepIntent`: Usuario pide el siguiente paso

### 2. Handlers (Manejadores)
Cada handler responde a un intent específico:
```python
class SearchByIngredientsIntentHandler:
    def can_handle(self, handler_input):
        # ¿Es el intent correcto?
        return intent_name == "SearchByIngredientsIntent"

    def handle(self, handler_input):
        # Procesar la búsqueda
        return response
```

### 3. Repositories (Repositorios)
Son las clases que hablan con la base de datos:
```python
class DynamoDBUserRepository:
    def get_user(self, user_id):
        # Obtener usuario de DynamoDB
        return User(...)

    def save_user(self, user):
        # Guardar usuario en DynamoDB
        db.put_item(...)
```

### 4. Services (Servicios)
Coordinan la lógica de negocio:
```python
class RecipeService:
    def __init__(self, repository, api_client):
        self.repository = repository
        self.api_client = api_client

    def search_recipes(self, ingredients):
        # Buscar en API
        # Guardar en BD
        # Filtrar por alergias
        return recipes
```

## Base de Datos (DynamoDB)

Tenemos 3 tablas principales:

### Users (Usuarios)
```
user_id (clave)    | allergies           | diet         | servings
-------------------|---------------------|--------------|----------
alexa-user-123     | ["peanuts", "eggs"] | "vegetarian" | 2
```

### Recipes (Recetas)
```
recipe_id (clave) | title              | ingredients | steps
------------------|--------------------|--------------|---------
716429            | "Arroz con Pollo"  | [...]       | [...]
```

### Sessions (Sesiones de cocina)
```
session_id (clave) | user_id        | recipe_id | current_step | status
-------------------|----------------|-----------|--------------|--------
session-abc        | alexa-user-123 | 716429    | 3            | active
```

## API Externa: Spoonacular

Es de donde obtenemos las recetas.

**Lo que nos da:**
- 380,000+ recetas
- Búsqueda por ingredientes
- Pasos de cocina
- Información nutricional
- Imágenes

**Límites:**
- Plan gratuito: 150 requests/día
- Tenemos caché para no gastar requests innecesarios

## Configuración de Desarrollo

### 1. Pre-requisitos
```bash
# Python 3.11
python --version

# AWS CLI configurado
aws configure
```

### 2. Clonar y Setup
```bash
# Clonar repo
git clone <tu-repo>
cd Asistente_cocina

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Variables de Entorno
Crea un archivo `.env`:
```
SPOONACULAR_API_KEY=tu_api_key_aqui
AWS_REGION=us-east-1
```

### 4. Ejecutar Tests Locales
```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/test_recipe_service.py

# Ver cobertura
pytest --cov=lambda
```

## Cómo Hacer Cambios

### Agregar un nuevo Intent (comando de voz)

**Ejemplo: Quieres agregar "guardar receta como favorita"**

1. **Definir el intent en Alexa Console**
   - Ir a `alexa-skill/interactionModels/custom/es-ES.json`
   - Agregar:
   ```json
   {
     "name": "SaveFavoriteIntent",
     "samples": [
       "guarda esta receta",
       "agrégala a favoritos",
       "quiero guardarla"
     ]
   }
   ```

2. **Crear el Handler**
   - Crear `lambda/presentation/handlers/favorite_handler.py`:
   ```python
   class SaveFavoriteIntentHandler(AbstractRequestHandler):
       def can_handle(self, handler_input):
           return intent_name == "SaveFavoriteIntent"

       def handle(self, handler_input):
           # Obtener recipe_id actual
           # Llamar a user_service.add_favorite(user_id, recipe_id)
           return response
   ```

3. **Actualizar el Service**
   - Agregar método en `user_service.py`:
   ```python
   def add_favorite(self, user_id, recipe_id):
       user = self.user_repository.get_user(user_id)
       user.favorites.append(recipe_id)
       self.user_repository.save_user(user)
   ```

4. **Registrar el Handler**
   - En `lambda_function.py`:
   ```python
   sb.add_request_handler(SaveFavoriteIntentHandler(user_service))
   ```

5. **Hacer Deploy**
   ```bash
   ./deploy.sh
   ```

## Estructura de Archivos Importantes

```
Asistente_cocina/
├── lambda/
│   ├── lambda_function.py          ← INICIO: Registra todos los handlers
│   ├── presentation/handlers/      ← Handlers de cada intent
│   │   ├── launch_handler.py
│   │   ├── search_handler.py
│   │   └── cooking_handler.py
│   ├── application/services/       ← Lógica de negocio
│   │   ├── recipe_service.py
│   │   ├── user_service.py
│   │   └── session_service.py
│   ├── domain/models/              ← Definición de datos
│   │   ├── user.py
│   │   ├── recipe.py
│   │   └── session.py
│   └── infrastructure/             ← Conexiones externas
│       ├── external/
│       │   └── spoonacular_client.py
│       └── repositories/
│           ├── dynamodb_user_repository.py
│           ├── dynamodb_recipe_repository.py
│           └── dynamodb_session_repository.py
├── alexa-skill/
│   └── interactionModels/
│       └── custom/
│           └── es-ES.json          ← Definición de intents y utterances
├── infrastructure/                  ← Scripts de Terraform (deploy AWS)
├── requirements.txt                ← Dependencias Python
├── ARQUITECTURA.md                 ← Diagramas técnicos detallados
├── API_INFO.md                     ← Info sobre Spoonacular API
└── ALEXA_SETUP.md                  ← Guía de configuración en Alexa Console
```

## Flujo de Trabajo Git

```bash
# 1. Crear rama para tu feature
git checkout -b feature/mi-nueva-funcionalidad

# 2. Hacer cambios y commits
git add .
git commit -m "Add: nueva funcionalidad X"

# 3. Push a remoto
git push origin feature/mi-nueva-funcionalidad

# 4. Crear Pull Request en GitHub
# Esperar review del equipo

# 5. Merge a main
```

## Deployment

### Deploy Manual
```bash
# 1. Empaquetar
cd lambda
zip -r ../chef-personal-lambda.zip .

# 2. Actualizar Lambda
aws lambda update-function-code \
  --function-name chef-personal \
  --zip-file fileb://../chef-personal-lambda.zip
```

### Deploy con Script
```bash
# Ejecutar script de deploy
./setup.sh
```

## Testing

### Probar Localmente
```bash
# Simular un evento de Alexa
python -m pytest tests/integration/test_search_flow.py
```

### Probar en Alexa Console
1. Ir a https://developer.amazon.com/alexa/console/ask
2. Seleccionar "Chef Personal"
3. Tab "Test"
4. Escribir: "abre chef personal"

### Probar en Dispositivo Real
1. Usar la misma cuenta de Amazon
2. Decir: "Alexa, abre chef personal"

## Debugging

### Ver Logs de Lambda
```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/chef-personal --follow

# Ver logs específicos
aws logs filter-pattern /aws/lambda/chef-personal "ERROR"
```

### Debugging Local
```python
# Agregar prints en el código
def search_recipes(self, ingredients):
    print(f"DEBUG: Buscando recetas con {ingredients}")
    recipes = self.api_client.search(ingredients)
    print(f"DEBUG: Encontradas {len(recipes)} recetas")
    return recipes
```

## Problemas Comunes

### "There was a problem with the requested skill's response"
**Causa:** Error en Lambda
**Solución:**
```bash
aws logs tail /aws/lambda/chef-personal --follow
```
Ver el error específico en los logs

### "The skill took too long to respond"
**Causa:** Lambda timeout
**Solución:**
```bash
aws lambda update-function-configuration \
  --function-name chef-personal \
  --timeout 15
```

### API de Spoonacular retorna 402 (Payment Required)
**Causa:** Se acabaron los requests del día
**Solución:**
- Esperar al día siguiente
- O upgrade al plan de pago
- Verificar caché está funcionando

## Recursos Útiles

### Documentación
- [Alexa Skills Kit](https://developer.amazon.com/docs/ask-overviews/build-skills-with-the-alexa-skills-kit.html)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Spoonacular API](https://spoonacular.com/food-api/docs)
- [DynamoDB](https://docs.aws.amazon.com/dynamodb/)

### Documentos del Proyecto
- `ARQUITECTURA.md`: Diagramas técnicos detallados
- `API_INFO.md`: Info completa de Spoonacular
- `ALEXA_SETUP.md`: Configuración de Alexa Console
- `TESTING_GUIA.md`: Guía de testing completa

## Glosario Rápido

| Término | Significado |
|---------|-------------|
| **Intent** | Un comando que el usuario puede decir a Alexa |
| **Handler** | Código que responde a un intent específico |
| **Utterance** | Frase que activa un intent ("tengo pollo") |
| **Slot** | Variable en un utterance (ingredient_name) |
| **Lambda** | Función que corre en la nube cuando se necesita |
| **DynamoDB** | Base de datos NoSQL de AWS |
| **Repository** | Clase que habla con la base de datos |
| **Service** | Clase con lógica de negocio |
| **Model** | Definición de una entidad (User, Recipe) |

## Siguiente Paso

1. **Lee el código de un handler simple:** `launch_handler.py`
2. **Sigue el flujo de un intent completo:** Ver ejemplo de búsqueda arriba
3. **Haz tu primer cambio:** Modifica el mensaje de bienvenida
4. **Pruébalo en Alexa Console**

¡Bienvenido al equipo! Si tienes dudas, pregunta sin problema 🚀
