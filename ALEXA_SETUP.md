# Configuración en Alexa Developer Console

## Paso 1: Crear la Skill

### 1.1 Acceder a la Consola
1. Ve a https://developer.amazon.com/alexa/console/ask
2. Inicia sesión con tu cuenta de Amazon
3. Clic en **"Create Skill"**

### 1.2 Configuración Básica
- **Skill name:** Chef Personal
- **Primary locale:** Spanish (ES)
- **Model:** Custom
- **Hosting:** Provision your own
- **Backend resources:** No
- Clic en **"Create skill"**

### 1.3 Template
- Selecciona **"Start from Scratch"**
- Clic en **"Continue with template"**

## Paso 2: Configurar Interaction Model

### 2.1 Método 1: JSON Editor (Recomendado)

1. En el menú izquierdo, ve a **"Build"** > **"Interaction Model"** > **"JSON Editor"**

2. Copia todo el contenido del archivo:
   ```
   alexa-skill/interactionModels/custom/es-ES.json
   ```

3. Pégalo en el editor, reemplazando todo el contenido

4. Clic en **"Save Model"**

5. Clic en **"Build Model"** (tarda 1-2 minutos)

### 2.2 Método 2: Configuración Manual (Alternativa)

Si prefieres configurar manualmente:

**Invocation Name:**
- Ve a **"Invocations"** > **"Skill Invocation Name"**
- Escribe: `chef personal`
- Save

**Intents:**
- Ve a **"Interaction Model"** > **"Intents"**
- Agrega cada intent del archivo JSON manualmente
- Agrega los slots y sample utterances

**Slot Types:**
- Ve a **"Slot Types"**
- Crea `AllergenType` con todos los valores
- Crea `DietType` con todos los valores

## Paso 3: Configurar Endpoint (Lambda)

### 3.1 Primero: Deploy Lambda en AWS

Antes de configurar el endpoint, necesitas tener tu función Lambda creada:

```bash
# 1. Empaquetar el código
cd lambda
pip install -r ../requirements.txt -t .
zip -r ../chef-personal-lambda.zip .

# 2. Crear función Lambda
aws lambda create-function \
  --function-name chef-personal \
  --runtime python3.11 \
  --role arn:aws:iam::TU_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://../chef-personal-lambda.zip \
  --timeout 10 \
  --memory-size 256 \
  --environment Variables="{SPOONACULAR_API_KEY=54b49c32fc2b4750834c8ee4a40bd127,AWS_REGION=us-east-1}"
```

### 3.2 Obtener el ARN de Lambda

```bash
aws lambda get-function --function-name chef-personal
```

El ARN se verá así:
```
arn:aws:lambda:us-east-1:123456789012:function:chef-personal
```

### 3.3 Configurar en Alexa Console

1. En Alexa Developer Console, ve a **"Build"** > **"Endpoint"**

2. Selecciona **"AWS Lambda ARN"**

3. En **"Default Region"**, pega tu ARN:
   ```
   arn:aws:lambda:us-east-1:TU_ACCOUNT_ID:function:chef-personal
   ```

4. Copia el **"Your Skill ID"** que aparece arriba (lo necesitarás)
   ```
   amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

5. Clic en **"Save Endpoints"**

### 3.4 Dar Permisos a Alexa en Lambda

```bash
aws lambda add-permission \
  --function-name chef-personal \
  --statement-id alexa-skill-permission \
  --action lambda:InvokeFunction \
  --principal alexa-appkit.amazon.com \
  --event-source-token amzn1.ask.skill.TU_SKILL_ID
```

## Paso 4: Testing

### 4.1 Habilitar Testing

1. Ve a la pestaña **"Test"** en el menú superior
2. En **"Skill testing is enabled in:"** selecciona **"Development"**

### 4.2 Probar la Skill

**Opción A: Simulador de Texto**

Escribe en el simulador:
```
abre chef personal
```

Deberías ver:
```
Alexa: ¡Bienvenido a Chef Personal! Soy tu asistente culinario inteligente.
       Para brindarte la mejor experiencia, ¿tienes alguna alergia alimentaria
       que deba tener en cuenta?
```

**Opción B: Simulador de Voz**

Clic en el micrófono y habla:
```
"Alexa, abre chef personal"
```

**Opción C: Dispositivo Real**

En tu dispositivo Alexa (Echo, etc.):
```
"Alexa, abre chef personal"
```

### 4.3 Pruebas Completas

```
1. "Alexa, abre chef personal"
   → Pregunta sobre alergias

2. "Soy alérgico a los cacahuetes"
   → Confirma registro de alergia

3. "Tengo pollo y arroz"
   → Muestra 3 recetas con descripción

4. "La primera"
   → Comienza modo cocina

5. "Siguiente"
   → Avanza pasos

6. "Pausa"
   → Pausa la receta

7. "Alexa, cierra"
   → Cierra skill

8. "Alexa, abre chef personal"
   → Abre de nuevo

9. "Continúa"
   → Retoma donde quedó
```

## Paso 5: Configuración Adicional (Opcional)

### 5.1 Iconos de la Skill

1. Ve a **"Distribution"** > **"Skill Preview"**
2. Sube iconos:
   - **Small Icon:** 108x108 px
   - **Large Icon:** 512x512 px

### 5.2 Información de Publicación

1. **Public Name:** Chef Personal
2. **One Sentence Description:**
   ```
   Tu asistente de cocina que encuentra recetas y te guía paso a paso
   ```
3. **Detailed Description:**
   ```
   Chef Personal es tu asistente de cocina inteligente que:
   - Encuentra recetas basadas en ingredientes que tengas
   - Respeta tus alergias y restricciones dietéticas
   - Te guía paso a paso mientras cocinas
   - Guarda tu progreso para continuar después
   ```

### 5.3 Privacy & Compliance

1. **Does this skill allow users to make purchases?** No
2. **Does this Alexa skill collect users' personal information?** Yes
   - Explicación: "Guardamos alergias y preferencias dietéticas"
3. **Is this skill directed to children under 13?** No
4. **Export Compliance:** Yes
5. **Does this skill contain advertising?** No

## Paso 6: Monitoreo y Logs

### 6.1 Ver Logs de Lambda

```bash
aws logs tail /aws/lambda/chef-personal --follow
```

### 6.2 Analytics en Alexa Console

1. Ve a **"Analytics"**
2. Verás:
   - Usuarios activos
   - Sessions
   - Utterances más usados
   - Errores

### 6.3 CloudWatch Metrics

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chef-personal \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Troubleshooting

### Error: "There was a problem with the requested skill's response"

**Causa:** Lambda no responde o tiene errores

**Solución:**
1. Verifica logs de Lambda:
   ```bash
   aws logs tail /aws/lambda/chef-personal --follow
   ```
2. Verifica que el ARN esté correcto
3. Verifica permisos de Alexa en Lambda

### Error: "The requested skill took too long to respond"

**Causa:** Lambda timeout

**Solución:**
```bash
aws lambda update-function-configuration \
  --function-name chef-personal \
  --timeout 15
```

### Error: Intent no reconocido

**Causa:** Modelo no construido o utterances incorrectos

**Solución:**
1. Ve a Build > JSON Editor
2. Verifica que el JSON esté correcto
3. Clic en "Build Model"
4. Espera a que termine

### No responde en dispositivo real

**Causa:** Testing no habilitado o cuenta diferente

**Solución:**
1. Verifica que Testing esté en "Development"
2. Usa la misma cuenta de Amazon en Alexa Developer Console y en tu dispositivo
3. Di "Alexa, descubre dispositivos" (aunque no aplica a skills, reinicia)

## Actualizar la Skill

### Actualizar Lambda:

```bash
cd lambda
zip -r ../chef-personal-lambda.zip .

aws lambda update-function-code \
  --function-name chef-personal \
  --zip-file fileb://../chef-personal-lambda.zip
```

### Actualizar Interaction Model:

1. Ve a Build > JSON Editor
2. Pega el nuevo JSON
3. Save Model
4. Build Model

### Actualizar Variables de Entorno:

```bash
aws lambda update-function-configuration \
  --function-name chef-personal \
  --environment Variables="{SPOONACULAR_API_KEY=tu_key,AWS_REGION=us-east-1}"
```

## Certificación para Producción

Cuando estés listo para publicar:

1. Completa toda la información en **"Distribution"**
2. Pasa las pruebas de **"Validation"**
3. Completa **"Privacy & Compliance"**
4. Envía para certificación en **"Certification"**
5. Amazon revisará (5-7 días)
6. Una vez aprobado, estará en la Alexa Skills Store

## Recursos Útiles

- **Alexa Developer Docs:** https://developer.amazon.com/docs/ask-overviews/build-skills-with-the-alexa-skills-kit.html
- **Testing Guide:** https://developer.amazon.com/docs/devconsole/test-your-skill.html
- **Lambda Best Practices:** https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- **Spoonacular API:** https://spoonacular.com/food-api/console
