// ==============================================
// RATE LIMITER MIDDLEWARE
// Demuestra: Middleware Pattern, Protection against abuse
// ==============================================

class RateLimiter {
    constructor(options = {}) {
        this.windowMs = options.windowMs || 60 * 1000; // 1 minuto por defecto
        this.maxRequests = options.maxRequests || 100;
        this.requests = new Map();
    }

    middleware() {
        return (req, res, next) => {
            // Obtener identificador del cliente (IP o Telegram ID si disponible)
            const clientId = this.getClientId(req);
            const now = Date.now();

            // Limpiar requests antiguos
            this.cleanup(now);

            // Obtener o crear registro del cliente
            if (!this.requests.has(clientId)) {
                this.requests.set(clientId, []);
            }

            const clientRequests = this.requests.get(clientId);
            
            // Filtrar requests dentro de la ventana de tiempo
            const recentRequests = clientRequests.filter(
                timestamp => now - timestamp < this.windowMs
            );

            // Verificar límite
            if (recentRequests.length >= this.maxRequests) {
                return res.status(429).json({
                    error: 'Too Many Requests',
                    message: 'Has excedido el límite de solicitudes. Intenta de nuevo en un momento.',
                    retryAfter: Math.ceil(this.windowMs / 1000)
                });
            }

            // Registrar request actual
            recentRequests.push(now);
            this.requests.set(clientId, recentRequests);

            // Agregar headers de rate limit
            res.set('X-RateLimit-Limit', this.maxRequests);
            res.set('X-RateLimit-Remaining', this.maxRequests - recentRequests.length);
            res.set('X-RateLimit-Reset', new Date(now + this.windowMs).toISOString());

            next();
        };
    }

    getClientId(req) {
        // Intentar obtener Telegram ID del body si existe
        if (req.body?.message?.from?.id) {
            return `telegram:${req.body.message.from.id}`;
        }
        
        // Fallback a IP
        return req.ip || req.connection.remoteAddress || 'unknown';
    }

    cleanup(now) {
        // Limpiar registros antiguos cada cierto tiempo
        for (const [clientId, timestamps] of this.requests.entries()) {
            const validTimestamps = timestamps.filter(
                ts => now - ts < this.windowMs
            );
            
            if (validTimestamps.length === 0) {
                this.requests.delete(clientId);
            } else {
                this.requests.set(clientId, validTimestamps);
            }
        }
    }
}

module.exports = { RateLimiter };