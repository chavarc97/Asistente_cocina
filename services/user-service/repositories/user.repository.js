// ==============================================
// USER REPOSITORY
// Demuestra: Repository Pattern, Data Access Layer
// ==============================================

const database = require('../infrastructure/database');
const logger = require('../utils/logger');

class UserRepository {
    /**
     * Create or update user
     * Demuestra: Upsert pattern
     */
    async createOrUpdate(userData) {
        const { telegram_id, username, first_name, last_name } = userData;
        
        const query = `
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                last_active = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        `;

        try {
            const result = await database.query(query, [
                telegram_id,
                username,
                first_name,
                last_name
            ]);
            
            logger.info('User created/updated:', { telegram_id });
            return result.rows[0];
        } catch (error) {
            logger.error('Error creating/updating user:', error);
            throw error;
        }
    }

    /**
     * Find user by Telegram ID
     */
    async findByTelegramId(telegram_id) {
        const query = 'SELECT * FROM users WHERE telegram_id = $1';
        
        try {
            const result = await database.query(query, [telegram_id]);
            return result.rows[0] || null;
        } catch (error) {
            logger.error('Error finding user:', error);
            throw error;
        }
    }

    /**
     * Find user by UUID
     */
    async findById(id) {
        const query = 'SELECT * FROM users WHERE id = $1';
        
        try {
            const result = await database.query(query, [id]);
            return result.rows[0] || null;
        } catch (error) {
            logger.error('Error finding user by ID:', error);
            throw error;
        }
    }

    /**
     * Update user's dietary filter
     */
    async updateDietaryFilter(telegram_id, dietary_filter) {
        const query = `
            UPDATE users 
            SET dietary_filter = $2::dietary_filter,
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = $1
            RETURNING *
        `;

        try {
            const result = await database.query(query, [telegram_id, dietary_filter]);
            
            if (result.rows.length === 0) {
                throw new Error('User not found');
            }
            
            logger.info('Updated dietary filter:', { telegram_id, dietary_filter });
            return result.rows[0];
        } catch (error) {
            logger.error('Error updating dietary filter:', error);
            throw error;
        }
    }

    /**
     * Update user's last active timestamp
     */
    async updateLastActive(telegram_id) {
        const query = `
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP
            WHERE telegram_id = $1
        `;

        try {
            await database.query(query, [telegram_id]);
        } catch (error) {
            logger.error('Error updating last active:', error);
            // Non-critical, don't throw
        }
    }

    /**
     * Get all active users (for analytics)
     */
    async getActiveUsers(days = 7) {
        const query = `
            SELECT telegram_id, username, first_name, last_name, 
                   dietary_filter, last_active
            FROM users
            WHERE last_active > CURRENT_TIMESTAMP - INTERVAL '${days} days'
            ORDER BY last_active DESC
        `;

        try {
            const result = await database.query(query);
            return result.rows;
        } catch (error) {
            logger.error('Error getting active users:', error);
            throw error;
        }
    }

    /**
     * Get user statistics
     */
    async getUserStats(telegram_id) {
        const query = `
            SELECT 
                u.telegram_id,
                u.username,
                u.dietary_filter,
                u.created_at,
                COUNT(DISTINCT f.id) as favorite_count,
                COUNT(DISTINCT sh.id) as search_count
            FROM users u
            LEFT JOIN favorites f ON u.id = f.user_id AND f.status = 'active'
            LEFT JOIN search_history sh ON u.id = sh.user_id
            WHERE u.telegram_id = $1
            GROUP BY u.id, u.telegram_id, u.username, u.dietary_filter, u.created_at
        `;

        try {
            const result = await database.query(query, [telegram_id]);
            return result.rows[0] || null;
        } catch (error) {
            logger.error('Error getting user stats:', error);
            throw error;
        }
    }
}

module.exports = new UserRepository();
