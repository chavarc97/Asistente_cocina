// ==============================================
// USER SERVICE
// Demuestra: Service Layer, Business Logic
// ==============================================

const userRepository = require('../repositories/user.repository');
const logger = require('../utils/logger');

class UserService {
    /**
     * Register or update user from Telegram
     */
    async registerUser(telegramUser) {
        try {
            const userData = {
                telegram_id: telegramUser.id,
                username: telegramUser.username || null,
                first_name: telegramUser.first_name || null,
                last_name: telegramUser.last_name || null
            };

            const user = await userRepository.createOrUpdate(userData);
            
            logger.info('User registered/updated:', { 
                telegram_id: user.telegram_id,
                username: user.username 
            });

            return {
                id: user.id,
                telegram_id: user.telegram_id,
                username: user.username,
                first_name: user.first_name,
                last_name: user.last_name,
                dietary_filter: user.dietary_filter,
                created_at: user.created_at
            };
        } catch (error) {
            logger.error('Error registering user:', error);
            throw error;
        }
    }

    /**
     * Get user profile
     */
    async getUserProfile(telegram_id) {
        try {
            const user = await userRepository.findByTelegramId(telegram_id);
            
            if (!user) {
                return null;
            }

            // Get user statistics
            const stats = await userRepository.getUserStats(telegram_id);

            return {
                id: user.id,
                telegram_id: user.telegram_id,
                username: user.username,
                first_name: user.first_name,
                last_name: user.last_name,
                dietary_filter: user.dietary_filter,
                created_at: user.created_at,
                last_active: user.last_active,
                stats: {
                    favorites_count: parseInt(stats?.favorite_count || 0),
                    searches_count: parseInt(stats?.search_count || 0)
                }
            };
        } catch (error) {
            logger.error('Error getting user profile:', error);
            throw error;
        }
    }

    /**
     * Update dietary filter
     */
    async updateDietaryFilter(telegram_id, dietaryFilter) {
        const validFilters = ['none', 'vegetarian', 'vegan', 'gluten_free'];
        
        if (!validFilters.includes(dietaryFilter)) {
            throw new Error(`Invalid dietary filter: ${dietaryFilter}`);
        }

        try {
            const user = await userRepository.updateDietaryFilter(telegram_id, dietaryFilter);
            
            return {
                telegram_id: user.telegram_id,
                dietary_filter: user.dietary_filter,
                updated_at: user.updated_at
            };
        } catch (error) {
            logger.error('Error updating dietary filter:', error);
            throw error;
        }
    }

    /**
     * Update user's last active timestamp
     */
    async updateActivity(telegram_id) {
        try {
            await userRepository.updateLastActive(telegram_id);
        } catch (error) {
            // Non-critical error, just log it
            logger.warn('Failed to update user activity:', error);
        }
    }

    /**
     * Get active users for analytics
     */
    async getActiveUsers(days = 7) {
        try {
            const users = await userRepository.getActiveUsers(days);
            return users.map(user => ({
                telegram_id: user.telegram_id,
                username: user.username,
                dietary_filter: user.dietary_filter,
                last_active: user.last_active
            }));
        } catch (error) {
            logger.error('Error getting active users:', error);
            throw error;
        }
    }

    /**
     * Validate user exists
     */
    async validateUser(telegram_id) {
        try {
            const user = await userRepository.findByTelegramId(telegram_id);
            return !!user;
        } catch (error) {
            logger.error('Error validating user:', error);
            return false;
        }
    }
}

module.exports = new UserService();
