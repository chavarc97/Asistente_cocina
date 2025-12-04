// ==============================================
// REQUEST VALIDATOR MIDDLEWARE
// Demuestra: Input Validation, Security
// ==============================================

const Joi = require('joi');

class RequestValidator {
    // Esquemas de validación
    static schemas = {
        // Validación de mensaje de Telegram
        telegramMessage: Joi.object({
            update_id: Joi.number().required(),
            message: Joi.object({
                message_id: Joi.number().required(),
                from: Joi.object({
                    id: Joi.number().required(),
                    first_name: Joi.string(),
                    username: Joi.string()
                }).required(),
                chat: Joi.object({
                    id: Joi.number().required(),
                    type: Joi.string()
                }).required(),
                text: Joi.string(),
                date: Joi.number()
            })
        }),

        // Validación de búsqueda de recetas
        recipeSearch: Joi.object({
            ingredients: Joi.array()
                .items(Joi.string().min(2).max(50))
                .min(1)
                .max(3)
                .required(),
            dietaryFilter: Joi.string()
                .valid('none', 'vegetarian', 'vegan', 'gluten_free')
                .default('none')
        }),

        // Validación de favorito
        favorite: Joi.object({
            userId: Joi.string().uuid().required(),
            recipeId: Joi.string().required(),
            recipeName: Joi.string().max(255).required(),
            recipeImage: Joi.string().uri().allow(null)
        }),

        // Validación de usuario
        user: Joi.object({
            telegramId: Joi.number().required(),
            username: Joi.string().max(100),
            firstName: Joi.string().max(100),
            dietaryFilter: Joi.string()
                .valid('none', 'vegetarian', 'vegan', 'gluten_free')
        })
    };

    // Middleware de validación genérico
    static validate(schemaName) {
        return (req, res, next) => {
            const schema = RequestValidator.schemas[schemaName];
            
            if (!schema) {
                return next(new Error(`Schema '${schemaName}' not found`));
            }

            const { error, value } = schema.validate(req.body, {
                abortEarly: false,
                stripUnknown: true
            });

            if (error) {
                const errorMessage = error.details
                    .map(detail => detail.message)
                    .join(', ');

                return res.status(400).json({
                    error: 'Validation Error',
                    message: errorMessage,
                    details: error.details
                });
            }

            // Reemplazar body con valores validados/sanitizados
            req.body = value;
            next();
        };
    }

    // Validación de ingredientes (función helper)
    static validateIngredients(ingredients) {
        if (!Array.isArray(ingredients)) {
            return { valid: false, message: 'Ingredientes debe ser un array' };
        }

        if (ingredients.length === 0) {
            return { valid: false, message: 'Debes proporcionar al menos un ingrediente' };
        }

        if (ingredients.length > 3) {
            return { valid: false, message: 'Máximo 3 ingredientes permitidos' };
        }

        // Verificar que cada ingrediente sea válido
        for (const ingredient of ingredients) {
            if (typeof ingredient !== 'string' || ingredient.length < 2) {
                return { 
                    valid: false, 
                    message: `Ingrediente inválido: ${ingredient}` 
                };
            }
        }

        return { valid: true };
    }

    // Sanitizar input para prevenir inyección
    static sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        return input
            .replace(/[<>]/g, '')  // Remover tags HTML
            .replace(/['"`;]/g, '') // Remover caracteres peligrosos
            .trim()
            .substring(0, 500); // Limitar longitud
    }
}

module.exports = { RequestValidator };