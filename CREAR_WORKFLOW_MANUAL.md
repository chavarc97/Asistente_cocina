# 🔧 CREAR WORKFLOW DE N8N MANUALMENTE

Si no puedes importar el archivo JSON, sigue esta guía para crear el workflow paso a paso.

## 📋 OPCIÓN RÁPIDA: Copiar y Pegar JSON

### Método 1: Usar el portapapeles (MÁS FÁCIL)

1. **Abre el archivo JSON:**
   ```bash
   cat /Users/tagle/Documents/Asistente_cocina/n8n/workflows/telegram-chef-bot.json
   ```

2. **Copia todo el contenido** (Cmd+A, Cmd+C)

3. **En N8N:**
   - Presiona `Cmd+V` o `Ctrl+V` para pegar
   - O presiona `Cmd+I` para abrir el importador
   - Pega el JSON completo
   - Haz clic en "Import"

### Método 2: Usar curl desde terminal

```bash
# Desde la terminal, copia el JSON al portapapeles
cat /Users/tagle/Documents/Asistente_cocina/n8n/workflows/telegram-chef-bot.json | pbcopy

# Ahora en N8N presiona Cmd+V para pegar
```

---

## 🛠 OPCIÓN MANUAL: Crear paso a paso (Si copiar/pegar no funciona)

### Paso 1: Crear workflow básico

1. En N8N, haz clic en **"Start from scratch"**
2. Nombra el workflow: **"Chef Bot - Telegram Workflow Completo"**

### Paso 2: Agregar Telegram Trigger

1. Haz clic en el botón **"+"** para agregar un nodo
2. Busca: **"Telegram Trigger"**
3. Selecciona el nodo y configúralo:
   - **Updates**: Selecciona `message` y `callback_query`
   - **Credential to connect with**: Haz clic en "Create New"
     - **Name**: `Telegram Bot API`
     - **Access Token**: `8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0`
     - Haz clic en **Save**

### Paso 3: Agregar nodo de Code (Parse Message)

1. Conecta el **Telegram Trigger** con un nodo **Code**
2. Renombra el nodo a: **"Parse Message"**
3. En el campo de código, pega este código:

```javascript
// Parse incoming Telegram message
const items = $input.all();
const results = [];

for (const item of items) {
  const data = item.json;
  const message = data.message || data.callback_query?.message;
  const text = data.message?.text || data.callback_query?.data || '';
  const chatId = message?.chat?.id;
  const userId = data.message?.from?.id || data.callback_query?.from?.id;

  let command = '';
  if (text.startsWith('/')) {
    command = text.split(' ')[0].substring(1).toLowerCase();
  } else {
    command = 'natural';
  }

  results.push({
    json: {
      command,
      chatId,
      userId,
      originalText: text,
      timestamp: new Date().toISOString()
    }
  });
}

return results;
```

### Paso 4: Agregar Switch (Command Router)

1. Conecta **Parse Message** con un nodo **Switch**
2. Renombra a: **"Command Router"**
3. Configura las rutas:
   - **Ruta 1**: `{{ $json.command }}` equals `start` → Output: "start"
   - **Ruta 2**: `{{ $json.command }}` equals `buscar` → Output: "buscar"
   - **Ruta 3**: `{{ $json.command }}` equals `ayuda` → Output: "ayuda"

### Paso 5: Agregar nodo de respuesta (Send Message)

1. Para cada ruta del Switch, agrega un nodo **Telegram**
2. Configura:
   - **Resource**: `Message`
   - **Operation**: `Send Message`
   - **Chat ID**: `{{ $json.chatId }}`
   - **Text**: Escribe tu mensaje de respuesta
   - **Credential**: Selecciona `Telegram Bot API`

### Paso 6: Ejemplo de respuesta para /start

```javascript
// En un nodo Code antes del Telegram Send
const firstName = $input.first().json.firstName || 'Chef';
const chatId = $input.first().json.chatId;

const message = `🍳 ¡Hola! Bienvenido a Chef Bot

Comandos disponibles:
/buscar - Buscar recetas
/ayuda - Ver ayuda`;

return [{
  json: {
    chatId: chatId,
    message: message
  }
}];
```

---

## ✅ VERIFICAR QUE FUNCIONA

1. **Guarda el workflow**: `Cmd+S` o `Ctrl+S`
2. **Activa el workflow**: Toggle en la esquina superior derecha (debe estar verde)
3. **Prueba en Telegram**: Envía `/start` a tu bot

---

## 🚨 SI NADA FUNCIONA

### Opción más simple: Webhook básico

Si ninguna de las anteriores funciona, crea un webhook simple:

1. **Crea nuevo workflow**
2. **Agrega nodo Webhook:**
   - Path: `telegram`
   - HTTP Method: `POST`
   - Response Mode: `On Received`
3. **Agrega nodo Respond to Webhook:**
   - Status Code: `200`
   - Body: `{"ok": true}`
4. **Activa el workflow**
5. **Configura el webhook de Telegram:**

```bash
curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/setWebhook?url=https://TU-URL-NGROK.ngrok.io/webhook/telegram"
```

Esto al menos hará que el bot responda y confirme que está funcionando.

---

## 📞 SIGUIENTE PASO

Una vez que tengas el workflow básico funcionando:
1. Prueba enviando `/start` al bot en Telegram
2. Verifica que recibes una respuesta
3. Luego podemos agregar más funcionalidad paso a paso

**¿Cuál método te funcionó?** Avísame para continuar con la configuración completa.
