// ==============================================
// ERROR HANDLER MIDDLEWARE
// Centralized error handling
// ==============================================

const logger = require('../utils/logger');

class ErrorHandler {
    /**
     * Handle API errors
     */
    handle(err, req, res, next) {
        logger.error('API Error:', {
            error: err.message,
            stack: err.stack,
            path: req.path,
            method: req.method
        });

        // Default error
        let statusCode = err.statusCode || 500;
        let message = err.message || 'Internal Server Error';

        // Handle specific error types
        if (err.name === 'ValidationError') {
            statusCode = 400;
            message = 'Validation Error';
        }

        if (err.code === '23505') { // PostgreSQL unique violation
            statusCode = 409;
            message = 'Resource already exists';
        }

        if (err.code === '23503') { // PostgreSQL foreign key violation
            statusCode = 404;
            message = 'Related resource not found';
        }

        res.status(statusCode).json({
            error: {
                message,
                status: statusCode,
                ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
            }
        });
    }

    /**
     * Handle 404 errors
     */
    notFound(req, res, next) {
        res.status(404).json({
            error: {
                message: 'Resource not found',
                status: 404,
                path: req.path
            }
        });
    }
}

module.exports = new ErrorHandler();
