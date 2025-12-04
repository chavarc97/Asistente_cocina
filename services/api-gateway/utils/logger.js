// ==============================================
// LOGGER UTILITY
// Demuestra: Logging Abstraction, Single Responsibility
// ==============================================

class Logger {
    constructor(service) {
        this.service = service;
        this.levels = {
            ERROR: 0,
            WARN: 1,
            INFO: 2,
            DEBUG: 3
        };
        this.currentLevel = this.levels[process.env.LOG_LEVEL?.toUpperCase() || 'INFO'];
    }

    formatMessage(level, message, args) {
        const timestamp = new Date().toISOString();
        const argsStr = args.length > 0 ? ' ' + JSON.stringify(args) : '';
        return `[${timestamp}] [${level}] [${this.service}] ${message}${argsStr}`;
    }

    error(message, ...args) {
        if (this.currentLevel >= this.levels.ERROR) {
            console.error(this.formatMessage('ERROR', message, args));
        }
    }

    warn(message, ...args) {
        if (this.currentLevel >= this.levels.WARN) {
            console.warn(this.formatMessage('WARN', message, args));
        }
    }

    info(message, ...args) {
        if (this.currentLevel >= this.levels.INFO) {
            console.info(this.formatMessage('INFO', message, args));
        }
    }

    debug(message, ...args) {
        if (this.currentLevel >= this.levels.DEBUG) {
            console.debug(this.formatMessage('DEBUG', message, args));
        }
    }
}

module.exports = { Logger };