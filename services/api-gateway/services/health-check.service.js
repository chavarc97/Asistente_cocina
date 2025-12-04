// ==============================================
// HEALTH CHECK SERVICE
// Demuestra: Health Monitoring Pattern
// ==============================================

const axios = require('axios');

class HealthCheckService {
    constructor(serviceRegistry) {
        this.serviceRegistry = serviceRegistry;
        this.timeout = 5000; // 5 segundos timeout
    }

    async checkAll() {
        const services = this.serviceRegistry.getServices();
        const checks = {};
        let overallStatus = 'healthy';

        // Verificar cada servicio
        for (const [name, url] of Object.entries(services)) {
            try {
                const response = await axios.get(`${url}/health`, {
                    timeout: this.timeout
                });
                
                checks[name] = {
                    status: 'healthy',
                    responseTime: response.headers['x-response-time'] || 'N/A',
                    url: url
                };
            } catch (error) {
                checks[name] = {
                    status: 'unhealthy',
                    error: error.message,
                    url: url
                };
                overallStatus = 'degraded';
            }
        }

        return {
            status: overallStatus,
            timestamp: new Date().toISOString(),
            service: 'api-gateway',
            version: '1.0.0',
            dependencies: checks
        };
    }

    async checkService(serviceName) {
        const url = this.serviceRegistry.getServiceUrl(serviceName);
        
        if (!url) {
            return {
                status: 'unknown',
                error: 'Service not registered'
            };
        }

        try {
            const start = Date.now();
            const response = await axios.get(`${url}/health`, {
                timeout: this.timeout
            });
            const responseTime = Date.now() - start;

            return {
                status: 'healthy',
                responseTime: `${responseTime}ms`,
                data: response.data
            };
        } catch (error) {
            return {
                status: 'unhealthy',
                error: error.message
            };
        }
    }
}

module.exports = { HealthCheckService };