# User Service - Chef Bot

## 📋 Overview

Node.js/Express service responsible for user management, profiles, and dietary preferences in the Chef Bot system.

## 🎯 Responsibilities

- User registration and profile management
- Dietary filter preferences
- User activity tracking
- User statistics and analytics

## 🏗️ Architecture

### Design Patterns

- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **Dependency Injection**: Loose coupling
- **Middleware Chain**: Request processing pipeline

### SOLID Principles

- **S**ingle Responsibility: Each class has one clear purpose
- **O**pen/Closed: Extensible through middleware
- **L**iskov Substitution: Consistent interfaces
- **I**nterface Segregation: Specific repository methods
- **D**ependency Inversion: Database abstraction

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns service health status and database connectivity.

### User Management

#### Register/Update User
```
POST /api/v1/users
Body: {
  "id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Get User Profile
```
GET /api/v1/users/:telegram_id
```

#### Update Dietary Filter
```
PUT /api/v1/users/:telegram_id/filter
Body: {
  "dietary_filter": "vegetarian" // none, vegetarian, vegan, gluten_free
}
```

#### Update User Activity
```
POST /api/v1/users/:telegram_id/activity
```

#### Get Active Users
```
GET /api/v1/users-active?days=7
```

#### Validate User Exists
```
GET /api/v1/users/:telegram_id/validate
```

## 🗂️ Project Structure

```
user-service/
├── index.js                    # Main application entry point
├── package.json                # Dependencies and scripts
├── Dockerfile                  # Container configuration
├── infrastructure/
│   └── database.js            # PostgreSQL connection pool
├── repositories/
│   └── user.repository.js     # Data access layer
├── services/
│   └── user.service.js        # Business logic layer
├── middleware/
│   ├── error-handler.js       # Error handling
│   └── validator.js           # Request validation
└── utils/
    └── logger.js              # Winston logger
```

## 🔧 Environment Variables

```bash
PORT=3002
DATABASE_URL=postgresql://user:pass@host:5432/db
NODE_ENV=production
LOG_LEVEL=info
ALLOWED_ORIGINS=*
```

## 🚀 Running Locally

### With Docker
```bash
docker-compose up user-service
```

### Without Docker
```bash
cd services/user-service
npm install
npm run dev
```

## 🧪 Testing

```bash
# Run tests
npm test

# Test health endpoint
curl http://localhost:3002/health

# Register user
curl -X POST http://localhost:3002/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"id": 123456789, "username": "test_user"}'

# Get user profile
curl http://localhost:3002/api/v1/users/123456789
```

## 📊 Database Schema

Uses tables from main database:
- `users` - User profiles and preferences
- `favorites` - User favorite recipes (via Recipe Service)
- `search_history` - Search activity tracking

## 🔍 Logging

Uses Winston for structured logging:
- Error logs: Critical issues
- Info logs: Important operations
- Debug logs: Detailed execution flow

## 🛡️ Error Handling

Centralized error handling middleware:
- Validation errors (400)
- Not found errors (404)
- Conflict errors (409)
- Server errors (500)

## 📈 Monitoring

Health check includes:
- Service status
- Database connectivity
- Timestamp

## 🔐 Security

- Helmet for HTTP headers
- CORS configuration
- Input validation
- Parameterized queries (SQL injection prevention)

## 🤝 Integration

### With Recipe Service
- User dietary filters used in recipe search
- User IDs for favorites and search history

### With API Gateway
- Proxied requests from gateway
- Authentication/authorization headers

### With n8n
- User data for workflow decisions
- Activity tracking from bot interactions

## 📝 Development Guidelines

1. **Repository Pattern**: All database access through repositories
2. **Service Layer**: Business logic in service classes
3. **Validation**: Use express-validator for all inputs
4. **Error Handling**: Throw errors, let middleware catch
5. **Logging**: Log all important operations
6. **Testing**: Write tests for all endpoints

## 🎯 Future Enhancements

- [ ] User preferences beyond dietary filters
- [ ] User groups/family profiles
- [ ] User badges/achievements
- [ ] Email notifications
- [ ] Export user data (GDPR)
- [ ] User analytics dashboard
