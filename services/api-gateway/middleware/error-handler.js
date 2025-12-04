// ==============================================
// ERROR HANDLER MIDDLEWARE
// Demuestra: Centralized Error Handling, Single Responsibility
// ==============================================

class ErrorHandler {
    handle(err, req, res, next) {
        // Log del error
        console.error('[ERROR]', {
            timestamp: new Date().toISOString(),
            error: err.message,
            stack: err.stack,
            url: req.url,
            method: req.method,
            body: req.body
        });

        // Determinar código de estado
        const statusCode = err.statusCode || err.status || 500;
        
        // Mensajes amigables según tipo de error
        let message = 'Ha ocurrido un error. Por favor intenta de nuevo.';
        
        if (statusCode === 400) {
            message = err.message || 'Solicitud inválida. Verifica los datos enviados.';
        } else if (statusCode === 404) {
            message = err.message || 'Recurso no encontrado.';
        } else if (statusCode === 429) {
            message = 'Demasiadas solicitudes. Espera un momento.';
        } else if (statusCode === 503) {
            message = 'Servicio no disponible temporalmente.';
        }

        // Respuesta de error
        res.status(statusCode).json({
            error: err.name || 'Error',
            message: message,
            ...(process.env.NODE_ENV === 'development' && {
                details: err.message,
                stack: err.stack
            })
        });
    }
}

module.exports = { ErrorHandler };