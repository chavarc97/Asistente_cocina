// ==============================================
// USER SERVICE - MAIN APPLICATION
// Express API for user management
// Demuestra: RESTful API, Service Layer Pattern
// ==============================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const database = require('./infrastructure/database');
const userService = require('./services/user.service');
const validator = require('./middleware/validator');
const errorHandler = require('./middleware/error-handler');
const logger = require('./utils/logger');

// ==============================================
// APPLICATION SETUP
// ==============================================

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(helmet());
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true
}));
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ==============================================
// ROUTES
// ==============================================

/**
 * Health check endpoint
 */
app.get('/health', async (req, res) => {
    try {
        const dbHealthy = await database.healthCheck();
        
        res.json({
            status: dbHealthy ? 'healthy' : 'degraded',
            service: 'user-service',
            database: dbHealthy ? 'connected' : 'disconnected',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            service: 'user-service',
            error: error.message
        });
    }
});

/**
 * Root endpoint
 */
app.get('/', (req, res) => {
    res.json({
        service: 'Chef Bot - User Service',
        version: '1.0.0',
        status: 'running'
    });
});

/**
 * Register or update user
 * POST /api/v1/users
 */
app.post('/api/v1/users',
    validator.registerUser(),
    validator.validate,
    async (req, res, next) => {
        try {
            const user = await userService.registerUser(req.body);
            res.status(201).json(user);
        } catch (error) {
            next(error);
        }
    }
);

/**
 * Get user profile by Telegram ID
 * GET /api/v1/users/:telegram_id
 */
app.get('/api/v1/users/:telegram_id',
    validator.telegramIdParam(),
    validator.validate,
    async (req, res, next) => {
        try {
            const { telegram_id } = req.params;
            const user = await userService.getUserProfile(parseInt(telegram_id));
            
            if (!user) {
                return res.status(404).json({
                    error: 'User not found'
                });
            }
            
            res.json(user);
        } catch (error) {
            next(error);
        }
    }
);

/**
 * Update user's dietary filter
 * PUT /api/v1/users/:telegram_id/filter
 */
app.put('/api/v1/users/:telegram_id/filter',
    validator.updateDietaryFilter(),
    validator.validate,
    async (req, res, next) => {
        try {
            const { telegram_id } = req.params;
            const { dietary_filter } = req.body;
            
            const result = await userService.updateDietaryFilter(
                parseInt(telegram_id),
                dietary_filter
            );
            
            res.json(result);
        } catch (error) {
            next(error);
        }
    }
);

/**
 * Update user activity (last active timestamp)
 * POST /api/v1/users/:telegram_id/activity
 */
app.post('/api/v1/users/:telegram_id/activity',
    validator.telegramIdParam(),
    validator.validate,
    async (req, res, next) => {
        try {
            const { telegram_id } = req.params;
            await userService.updateActivity(parseInt(telegram_id));
            res.json({ message: 'Activity updated' });
        } catch (error) {
            next(error);
        }
    }
);

/**
 * Get active users (for analytics)
 * GET /api/v1/users/active?days=7
 */
app.get('/api/v1/users-active',
    async (req, res, next) => {
        try {
            const days = parseInt(req.query.days) || 7;
            const users = await userService.getActiveUsers(days);
            
            res.json({
                count: users.length,
                users
            });
        } catch (error) {
            next(error);
        }
    }
);

/**
 * Validate user exists
 * GET /api/v1/users/:telegram_id/validate
 */
app.get('/api/v1/users/:telegram_id/validate',
    validator.telegramIdParam(),
    validator.validate,
    async (req, res, next) => {
        try {
            const { telegram_id } = req.params;
            const exists = await userService.validateUser(parseInt(telegram_id));
            
            res.json({
                telegram_id: parseInt(telegram_id),
                exists
            });
        } catch (error) {
            next(error);
        }
    }
);

// ==============================================
// ERROR HANDLERS
// ==============================================

app.use(errorHandler.notFound);
app.use(errorHandler.handle);

// ==============================================
// SERVER STARTUP
// ==============================================

async function startServer() {
    try {
        // Initialize database connection
        await database.connect();
        
        // Start server
        app.listen(PORT, () => {
            logger.info(`User Service running on port ${PORT}`);
            logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        });
    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
    logger.info('SIGTERM signal received: closing HTTP server');
    await database.close();
    process.exit(0);
});

process.on('SIGINT', async () => {
    logger.info('SIGINT signal received: closing HTTP server');
    await database.close();
    process.exit(0);
});

// Start the server
startServer();

module.exports = app;
