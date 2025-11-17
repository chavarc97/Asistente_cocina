# Guía de Testing - Chef Personal

## Problema: "Alexa me da comandos en lugar de abrir mi skill"

Esto sucede cuando:
1. El modelo no está compilado (Build)
2. Testing no está habilitado
3. Lambda no está conectado correctamente

## Solución Paso a Paso

### 1. Verificar que el Modelo esté Compilado

**En Alexa Developer Console:**
1. Ve a **Build** → **Interaction Model**
2. Verifica que diga **"Build Successful"** con fecha reciente
3. Si dice **"Build Failed"** o no hay fecha:
   - Ve a **JSON Editor**
   - Verifica que el JSON esté pegado
   - Clic en **"Save Model"**
   - Clic en **"Build Model"**
   - Espera 1-2 minutos

### 2. Habilitar Testing

**En Alexa Developer Console:**
1. Ve a la pestaña **"Test"** (arriba)
2. En **"Skill testing is enabled in:"**
   - Selecciona **"Development"**
   - Debería cambiar de "Off" a "Development"

### 3. Verificar Endpoint de Lambda

**En Alexa Developer Console:**
1. Ve a **Build** → **Endpoint**
2. Verifica que esté configurado:
   ```
   AWS Lambda ARN: arn:aws:lambda:us-east-1:TU_ACCOUNT:function:chef-personal
   ```
3. Si está vacío, agrégalo y clic en **"Save Endpoints"**

### 4. Dar Permisos a Lambda

**En tu terminal (si no lo has hecho):**
```bash
# Primero, obtén tu Skill ID de Alexa Console
# Está en Build > Endpoint > "Your Skill ID"

aws lambda add-permission \
  --function-name chef-personal \
  --statement-id alexa-skill-permission \
  --action lambda:InvokeFunction \
  --principal alexa-appkit.amazon.com \
  --event-source-token amzn1.ask.skill.TU-SKILL-ID-AQUI
```

## Cómo Probar la Skill

### Opción 1: Simulador de Alexa (Recomendado para primera vez)

**En Alexa Developer Console - Tab "Test":**

1. **Texto:**
   - Escribe: `abre chef personal`
   - Enter

2. **Voz:**
   - Clic en el micrófono
   - Di: "Alexa, abre chef personal"

**Respuesta esperada:**
```
Alexa: ¡Bienvenido a Chef Personal! Soy tu asistente culinario inteligente.
       Para brindarte la mejor experiencia, ¿tienes alguna alergia alimentaria
       que deba tener en cuenta? Por ejemplo: cacahuetes, nueces, leche, huevos,
       mariscos. Si no tienes alergias, solo di 'ninguna'.
```

### Opción 2: Dispositivo Alexa Real

**Requisitos:**
- Misma cuenta de Amazon en Developer Console y dispositivo
- Skill en modo "Development"
- Dispositivo conectado a internet

**Comandos:**
```
Tú: "Alexa, abre chef personal"

Alexa: [Respuesta de bienvenida]
```

## Problemas Comunes y Soluciones

### ❌ "No encuentro esa skill"

**Causa:** Skill no está en modo Development o cuenta diferente

**Solución:**
1. Verifica que Testing esté en "Development"
2. Usa la misma cuenta de Amazon
3. Di exactamente: "Alexa, abre chef personal"

### ❌ "Alexa me da opciones de comandos de Alexa"

**Causa:** La skill no se está abriendo, Alexa piensa que quieres comandos generales

**Solución:**
1. Di la frase completa: **"Alexa, abre chef personal"**
2. NO digas solo "abre chef" o "chef personal"
3. Verifica que el invocation name sea exactamente "chef personal"

### ❌ "There was a problem with the requested skill's response"

**Causa:** Lambda no responde o tiene errores

**Solución:**
1. Verifica que Lambda esté creado:
   ```bash
   aws lambda get-function --function-name chef-personal
   ```

2. Verifica logs de Lambda:
   ```bash
   aws logs tail /aws/lambda/chef-personal --follow
   ```

3. Verifica que el ARN en Alexa Console sea correcto

4. Verifica permisos:
   ```bash
   aws lambda get-policy --function-name chef-personal
   ```

### ❌ "The skill took too long to respond"

**Causa:** Lambda timeout o código bloqueado

**Solución:**
1. Aumenta timeout de Lambda:
   ```bash
   aws lambda update-function-configuration \
     --function-name chef-personal \
     --timeout 15
   ```

2. Verifica que las dependencias estén instaladas en Lambda

### ❌ "Intent not found" o "No handler for intent"

**Causa:** Lambda no tiene el handler configurado

**Solución:**
1. Verifica que lambda_function.py tenga todos los handlers registrados
2. Verifica que el código esté actualizado en Lambda:
   ```bash
   aws lambda update-function-code \
     --function-name chef-personal \
     --zip-file fileb://chef-personal-lambda.zip
   ```

## Secuencia de Testing Completa

### Test 1: Onboarding (Primera vez)

```
Tú: "Alexa, abre chef personal"
Alexa: "¿Tienes alguna alergia alimentaria?"

Tú: "Soy alérgico a los cacahuetes"
Alexa: "He registrado tu alergia a cacahuetes. Evitaré recetas con este ingrediente."

Tú: "Tengo pollo y arroz"
Alexa: "Encontré 3 recetas seguras: 1. Arroz con Pollo... 2. Paella... 3. Risotto..."

Tú: "La primera"
Alexa: "Perfecto, comenzamos con Arroz con Pollo. Paso 1: ..."

Tú: "Siguiente"
Alexa: "Paso 2: ..."

Tú: "Pausa"
Alexa: "He pausado la receta. Tu progreso está guardado."

Tú: "Alexa, cierra"
```

### Test 2: Usuario Recurrente

```
Tú: "Alexa, abre chef personal"
Alexa: "¡Hola! ¿Qué te gustaría cocinar hoy?"

Tú: "Continúa"
Alexa: "Continuamos con Arroz con Pollo. Estabas en el paso 2: ..."
```

### Test 3: Gestión de Alergias

```
Tú: "Alexa, abre chef personal"
Alexa: "¡Hola! ¿Qué te gustaría cocinar hoy?"

Tú: "Cuáles son mis alergias"
Alexa: "Tienes registrada una alergia a cacahuetes"

Tú: "Agrega alergia a la leche"
Alexa: "He registrado tu alergia a leche"

Tú: "Mis alergias"
Alexa: "Tienes alergias a cacahuetes y leche"
```

## Debug en Tiempo Real

### Ver Logs de Lambda

```bash
# Ver últimas líneas
aws logs tail /aws/lambda/chef-personal

# Seguir en tiempo real
aws logs tail /aws/lambda/chef-personal --follow

# Ver errores
aws logs tail /aws/lambda/chef-personal --follow --filter-pattern "ERROR"
```

### Ver Request/Response en Alexa Console

1. Ve a **Test** tab
2. Después de cada interacción, ve a la parte inferior
3. Clic en **"JSON Input"** - Ver lo que Alexa envió
4. Clic en **"JSON Output"** - Ver lo que Lambda respondió

### Verificar DynamoDB

```bash
# Ver perfiles de usuario
aws dynamodb scan --table-name UserProfiles --limit 5

# Ver sesiones activas
aws dynamodb scan --table-name CookingSessions --limit 5
```

## Checklist de Verificación

Antes de probar, verifica:

- [ ] Modelo compilado (Build Successful)
- [ ] Testing habilitado (Development)
- [ ] Endpoint configurado (ARN de Lambda)
- [ ] Lambda creado y con código
- [ ] Permisos de Alexa en Lambda
- [ ] Variables de entorno en Lambda (SPOONACULAR_API_KEY)
- [ ] Tablas de DynamoDB creadas
- [ ] Misma cuenta de Amazon en todos lados

## Frases de Invocación Válidas

✅ **Correcto:**
- "Alexa, abre chef personal"
- "Alexa, lanza chef personal"
- "Alexa, inicia chef personal"
- "Alexa, abre la skill chef personal"

❌ **Incorrecto:**
- "Alexa, chef personal" (falta "abre")
- "Alexa, abre chef" (falta "personal")
- "Alexa, cocina" (no es el invocation name)

## Notas Importantes

1. **Primera vez:** Siempre usa el simulador de Alexa Console primero
2. **Cuenta:** Usa la misma cuenta de Amazon en todos lados
3. **Paciencia:** El primer build puede tardar 2-3 minutos
4. **Logs:** Siempre verifica logs si algo falla
5. **Cache:** Si cambias código, espera 30 segundos antes de probar
