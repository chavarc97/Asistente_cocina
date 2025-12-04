// ==============================================
// DATABASE CONNECTION - USER SERVICE
// Demuestra: Connection Pooling, Repository Pattern
// ==============================================

const { Pool } = require('pg');
const logger = require('../utils/logger');

class Database {
    constructor() {
        this.pool = null;
    }

    /**
     * Initialize database connection pool
     */
    async connect() {
        try {
            this.pool = new Pool({
                connectionString: process.env.DATABASE_URL,
                max: 20,
                idleTimeoutMillis: 30000,
                connectionTimeoutMillis: 2000,
            });

            // Test connection
            const client = await this.pool.connect();
            await client.query('SELECT NOW()');
            client.release();

            logger.info('Database connection pool initialized successfully');
        } catch (error) {
            logger.error('Failed to initialize database pool:', error);
            throw error;
        }
    }

    /**
     * Execute a query
     */
    async query(text, params) {
        const start = Date.now();
        try {
            const result = await this.pool.query(text, params);
            const duration = Date.now() - start;
            logger.debug('Executed query', { text, duration, rows: result.rowCount });
            return result;
        } catch (error) {
            logger.error('Query error:', { text, error: error.message });
            throw error;
        }
    }

    /**
     * Get a client from the pool for transactions
     */
    async getClient() {
        return await this.pool.connect();
    }

    /**
     * Close all connections
     */
    async close() {
        if (this.pool) {
            await this.pool.end();
            logger.info('Database connection pool closed');
        }
    }

    /**
     * Check database connection health
     */
    async healthCheck() {
        try {
            await this.pool.query('SELECT 1');
            return true;
        } catch (error) {
            logger.error('Database health check failed:', error);
            return false;
        }
    }
}

// Singleton instance
const database = new Database();

module.exports = database;
