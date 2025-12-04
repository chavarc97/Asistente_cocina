// ==============================================
// SERVICE REGISTRY
// Demuestra: Service Discovery Pattern
// ==============================================

class ServiceRegistry {
    constructor() {
        this.services = {
            'recipe-service': process.env.RECIPE_SERVICE_URL || 'http://recipe-service:3001',
            'user-service': process.env.USER_SERVICE_URL || 'http://user-service:3002'
        };
    }

    getServices() {
        return this.services;
    }

    getServiceUrl(serviceName) {
        return this.services[serviceName] || null;
    }

    getEndpoints() {
        return [
            {
                name: 'recipes',
                path: '/api/recipes',
                target: this.services['recipe-service'],
                methods: ['GET', 'POST'],
                description: 'Búsqueda y gestión de recetas'
            },
            {
                name: 'users',
                path: '/api/users',
                target: this.services['user-service'],
                methods: ['GET', 'POST', 'PUT'],
                description: 'Gestión de usuarios'
            },
            {
                name: 'favorites',
                path: '/api/favorites',
                target: this.services['user-service'],
                methods: ['GET', 'POST', 'DELETE'],
                description: 'Gestión de recetas favoritas'
            },
            {
                name: 'health',
                path: '/health',
                target: 'internal',
                methods: ['GET'],
                description: 'Estado del servicio'
            }
        ];
    }

    registerService(name, url) {
        this.services[name] = url;
        console.log(`Service registered: ${name} -> ${url}`);
    }

    unregisterService(name) {
        delete this.services[name];
        console.log(`Service unregistered: ${name}`);
    }
}

module.exports = ServiceRegistry;