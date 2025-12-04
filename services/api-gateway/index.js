// ==============================================
// API GATEWAY - CHEF BOT
// Demuestra: API Gateway Pattern, Single Responsibility Principle
// ==============================================

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Import custom modules
const { RateLimiter } = require('./middleware/rate-limiter');
const { ErrorHandler } = require('./middleware/error-handler');
const { RequestValidator } = require('./middleware/request-validator');
const ServiceRegistry = require('./services/service-registry');
const { HealthCheckService } = require('./services/health-check.service');
const { Logger } = require('./utils/logger');

class APIGateway {
    constructor() {
        this.app = express();
        this.port = process.env.PORT || 3000;
        this.logger = new Logger('API-Gateway');
        this.serviceRegistry = new ServiceRegistry();
        this.healthCheck = new HealthCheckService(this.serviceRegistry);

        this.setupMiddleware();
        this.setupRoutes();
        this.setupProxies();
        this.setupErrorHandling();
    }

    // Single Responsibility: Configuración de middleware
    setupMiddleware() {
        // Security headers
        this.app.use(helmet());

        // CORS configuration
        this.app.use(cors({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
            credentials: true
        }));

        // Request logging
        this.app.use(morgan('combined'));

        // Body parsing
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));

        // Rate limiting (10 requests per minute per user)
        const rateLimiter = new RateLimiter({
            windowMs: 60 * 1000, // 1 minuto
            maxRequests: 100     // 100 requests por minuto
        });
        this.app.use(rateLimiter.middleware());
    }

    // Single Responsibility: Configuración de rutas
    setupRoutes() {
        // Health check endpoint
        this.app.get('/health', async (req, res) => {
            const health = await this.healthCheck.checkAll();
            res.status(health.status === 'healthy' ? 200 : 503).json(health);
        });

        // API Documentation
        this.app.get('/api/docs', (req, res) => {
            res.json({
                service: 'Chef Bot API Gateway',
                version: '1.0.0',
                endpoints: this.serviceRegistry.getEndpoints(),
                description: 'Gateway for Chef Bot microservices'
            });
        });

        // Webhook endpoint para Telegram (si se usa directamente)
        this.app.post('/webhook/telegram', async (req, res) => {
            this.logger.info('Received Telegram webhook');
            // Forward to n8n or process directly
            res.status(200).json({ status: 'received' });
        });
    }

    // Dependency Inversion: Configuración de proxies a microservicios
    setupProxies() {
        // Recipe Service Proxy
        this.app.use('/api/recipes',
            createProxyMiddleware({
                target: process.env.RECIPE_SERVICE_URL || 'http://recipe-service:3001',
                changeOrigin: true,
                pathRewrite: { '^/api/recipes': '' },
                onError: this.handleProxyError.bind(this)
            })
        );

        // User Service Proxy
        this.app.use('/api/users',
            createProxyMiddleware({
                target: process.env.USER_SERVICE_URL || 'http://user-service:3002',
                changeOrigin: true,
                pathRewrite: { '^/api/users': '' },
                onError: this.handleProxyError.bind(this)
            })
        );

        // Favorites endpoint (parte del User Service)
        this.app.use('/api/favorites',
            createProxyMiddleware({
                target: process.env.USER_SERVICE_URL || 'http://user-service:3002',
                changeOrigin: true,
                pathRewrite: { '^/api/favorites': '/favorites' },
                onError: this.handleProxyError.bind(this)
            })
        );
    }

    // Manejo de errores de proxy
    handleProxyError(err, req, res) {
        this.logger.error(`Proxy error: ${err.message}`);
        res.status(503).json({
            error: 'Service temporarily unavailable',
            message: 'El servicio no está respondiendo, intenta más tarde'
        });
    }

    // Single Responsibility: Configuración de manejo de errores
    setupErrorHandling() {
        const errorHandler = new ErrorHandler();
        this.app.use(errorHandler.handle.bind(errorHandler));
    }

    // Iniciar el gateway
    start() {
        this.app.listen(this.port, () => {
            this.logger.info(`🚀 API Gateway running on port ${this.port}`);
            this.logger.info('📋 Registered services:', this.serviceRegistry.getServices());
        });
    }
}

// Inicializar y arrancar
const gateway = new APIGateway();
gateway.start();

module.exports = APIGateway;