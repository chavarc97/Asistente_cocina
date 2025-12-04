// ==============================================
// REQUEST VALIDATOR MIDDLEWARE
// Input validation using express-validator
// ==============================================

const { body, param, validationResult } = require('express-validator');

class Validator {
    /**
     * Validate request and return errors if any
     */
    validate(req, res, next) {
        const errors = validationResult(req);
        
        if (!errors.isEmpty()) {
            return res.status(400).json({
                error: {
                    message: 'Validation failed',
                    errors: errors.array()
                }
            });
        }
        
        next();
    }

    /**
     * Validation rules for user registration
     */
    registerUser() {
        return [
            body('id').isInt().withMessage('Telegram ID must be an integer'),
            body('username').optional().isString(),
            body('first_name').optional().isString(),
            body('last_name').optional().isString()
        ];
    }

    /**
     * Validation rules for dietary filter update
     */
    updateDietaryFilter() {
        return [
            param('telegram_id').isInt().withMessage('Telegram ID must be an integer'),
            body('dietary_filter')
                .isIn(['none', 'vegetarian', 'vegan', 'gluten_free'])
                .withMessage('Invalid dietary filter')
        ];
    }

    /**
     * Validation rules for telegram_id parameter
     */
    telegramIdParam() {
        return [
            param('telegram_id').isInt().withMessage('Telegram ID must be an integer')
        ];
    }
}

module.exports = new Validator();
