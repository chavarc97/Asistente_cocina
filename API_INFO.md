# APIs Utilizadas - Chef Personal

## Spoonacular Food API

**URL:** https://spoonacular.com/food-api

### ¿Qué es?
Spoonacular es una API de comida y nutrición que proporciona:
- Más de 380,000 recetas
- Información nutricional
- Búsqueda por ingredientes
- Instrucciones paso a paso
- Imágenes de recetas

### Endpoints que Usamos

#### 1. **Buscar por Ingredientes**
```
GET https://api.spoonacular.com/recipes/findByIngredients
```

**Parámetros:**
- `ingredients`: "chicken,rice,tomato"
- `number`: Cantidad de resultados (default: 5)
- `ranking`: 2 (maximiza ingredientes usados)
- `diet`: vegetarian, vegan, ketogenic, etc.
- `addRecipeInformation`: true

**Respuesta:**
```json
[
  {
    "id": 716429,
    "title": "Pasta with Garlic, Scallions, Cauliflower & Breadcrumbs",
    "image": "https://spoonacular.com/recipeImages/716429-312x231.jpg",
    "usedIngredients": [...],
    "missedIngredients": [...],
    "readyInMinutes": 45,
    "servings": 2,
    "dishTypes": ["lunch", "main course"],
    "cuisines": ["Italian"]
  }
]
```

#### 2. **Información Detallada de Receta**
```
GET https://api.spoonacular.com/recipes/{id}/information
```

**Respuesta:**
```json
{
  "id": 716429,
  "title": "Pasta with Garlic...",
  "readyInMinutes": 45,
  "servings": 2,
  "extendedIngredients": [
    {
      "name": "pasta",
      "amount": 200,
      "unit": "g",
      "original": "200g pasta"
    }
  ],
  "analyzedInstructions": [
    {
      "steps": [
        {
          "number": 1,
          "step": "Heat oil in a large pan..."
        }
      ]
    }
  ],
  "vegetarian": false,
  "vegan": false,
  "glutenFree": false
}
```

### Costo y Límites

**Plan Gratuito:**
- 150 requests/día
- Suficiente para desarrollo y pruebas

**Plan Básico ($49/mes):**
- 5,000 requests/día
- ~150,000/mes
- Recomendado para producción

**Plan Mega ($149/mes):**
- 50,000 requests/día
- ~1.5M/mes
- Para apps con muchos usuarios

### Cómo Obtener API Key

1. Ve a https://spoonacular.com/food-api
2. Crea una cuenta
3. Obtén tu API key del dashboard
4. Agrégala a tu `.env`:
   ```
   SPOONACULAR_API_KEY=tu_clave_aqui
   ```

### Optimizaciones Implementadas

✅ **Caché en DynamoDB** - Guardamos recetas para evitar llamadas repetidas
✅ **TTL en RecipeCache** - Auto-limpieza de recetas antiguas
✅ **Batch requests** - `addRecipeInformation: true` reduce llamadas
✅ **Error handling** - Fallback si API falla

### Uso Actual en el Proyecto

```python
# lambda/infrastructure/external/spoonacular_client.py

class SpoonacularClient:
    BASE_URL = "https://api.spoonacular.com"

    def search_by_ingredients(self, ingredients, number=5, diet=None):
        # Busca recetas por ingredientes

    def get_recipe_information(self, recipe_id):
        # Obtiene detalles completos de una receta

    def get_recipe_summary(self, recipe_id):
        # Obtiene resumen (tiempo, tipo, cocina)
```

### Alternativas Consideradas

**TheMealDB** (Mencionado en arquitectura)
- URL: https://www.themealdb.com/api.php
- Gratis
- ~300 recetas
- Menos completo que Spoonacular
- Podría usarse como backup

**Edamam Recipe API**
- URL: https://www.edamam.com/
- Similar a Spoonacular
- Más caro
- Mejor para nutrición

**USDA FoodData Central**
- URL: https://fdc.nal.usda.gov/
- Gratis
- Solo nutrición, no recetas

### Monitoreo de Uso

Puedes ver tu uso en:
https://spoonacular.com/food-api/console

**Métricas importantes:**
- Requests hoy
- Requests este mes
- Costos estimados

### Ejemplo de Flujo Completo

```
Usuario: "Tengo pollo y arroz"
    ↓
SearchByIngredientsIntentHandler
    ↓
SpoonacularClient.search_by_ingredients(["chicken", "rice"])
    ↓
API: GET /recipes/findByIngredients?ingredients=chicken,rice
    ↓
Respuesta: 5 recetas con detalles
    ↓
Sistema: Filtra por alergias del usuario
    ↓
Alexa: "Encontré 3 recetas seguras:
        1. Arroz con Pollo, listo en 45 minutos
        2. Paella, listo en 1 hora
        3. Risotto, listo en 30 minutos"
```

### Estimación de Costos

**Escenario: 100 usuarios activos/día**

- Búsqueda por ingredientes: 100 requests/día
- Detalles de receta: 50 requests/día (50% seleccionan)
- Total: ~150 requests/día

**Con caché:**
- Reducción: 70% (muchas recetas repetidas)
- Total real: ~45 requests/día
- **Plan gratuito es suficiente** ✅

**Escenario: 1000 usuarios activos/día**

- Sin caché: 1,500 requests/día
- Con caché: ~450 requests/día
- **Plan Básico ($49/mes)** suficiente

### Documentación Completa

https://spoonacular.com/food-api/docs
