# SupaHealth Backend API Specification

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except auth and health endpoints) require JWT Bearer token authentication.

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## System Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Authentication Endpoints

### Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### Sign In
```http
POST /api/auth/signin
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
```

**Response:**
```json
{
  "id": "user..abc123def456",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-15T10:00:00+00:00",
  "updated_at": null
}
```

### Refresh Token
```http
POST /api/auth/refresh
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Heart Rate Tracking Endpoints

### Ingest Heart Rate Data
```http
POST /api/ingest-heart-rate
```

**Request Body:**
```json
{
  "record": {
    "data": {
      "metrics": [
        {
          "name": "heart_rate",
          "data": [
            {
              "Min": 65.5,
              "Max": 120.0,
              "date": "2025-01-15T10:00:00Z",
              "source": "Oura"
            }
          ],
          "units": "bpm"
        }
      ]
    }
  },
  "metadata": {
    "id": "hr_session_123",
    "private": false,
    "createdAt": "2025-01-15T12:00:00Z",
    "name": "Morning Heart Rate"
  }
}
```

### Get Heart Rate Data
```http
GET /api/heart-rate
```

**Query Parameters:**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

## Diet Tracking Endpoints

### Ingest Diet Data
```http
POST /api/ingest-diet
```

**Request Body:**
```json
{
  "record": {
    "data": {
      "metrics": [
        {
          "name": "diet",
          "data": [
            {
              "protein": 25.5,
              "carbs": 45.0,
              "fat": 15.2,
              "calories": 350.0,
              "meal_name": "Breakfast",
              "notes": "Oatmeal with berries",
              "date": "2025-01-15T08:00:00Z",
              "source": "Manual Entry"
            }
          ],
          "units": "grams"
        }
      ]
    }
  },
  "metadata": {
    "id": "diet_session_123",
    "private": false,
    "createdAt": "2025-01-15T12:00:00Z",
    "name": "Daily Meals"
  }
}
```

### Add Single Diet Record
```http
POST /api/diet/record
```

**Request Body:**
```json
{
  "protein": 25.5,
  "carbs": 45.0,
  "fat": 15.2,
  "calories": 350.0,
  "meal_name": "Breakfast",
  "notes": "Oatmeal with berries",
  "datetime": "2025-01-15T08:00:00Z",
  "source": "Manual Entry"
}
```

### Delete Diet Record
```http
DELETE /api/diet/record/{record_id}
```

### Get Diet Data
```http
GET /api/diet
```

**Query Parameters:**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string
- `meal_name` (optional): Filter by meal name

### Get Daily Diet Aggregation
```http
GET /api/diet/daily/{date}
```

**Example:**
```http
GET /api/diet/daily/2025-01-15
```

### Get Diet Aggregation
```http
GET /api/diet/aggregate
```

**Query Parameters:**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

## Weight Tracking Endpoints

### Create Weight Record
```http
POST /api/weight
```

**Request Body:**
```json
{
  "weight": 70.5,
  "body_fat_percentage": 15.2,
  "muscle_mass_percentage": 45.0,
  "notes": "Morning weight after workout"
}
```

### Get All Weight Records
```http
GET /api/weight
```

### Get Specific Weight Record
```http
GET /api/weight/{weight_id}
```

### Update Weight Record
```http
PUT /api/weight/{weight_id}
```

**Request Body:**
```json
{
  "weight": 70.2,
  "body_fat_percentage": 15.0,
  "muscle_mass_percentage": 45.2,
  "notes": "Updated morning weight"
}
```

### Delete Weight Record
```http
DELETE /api/weight/{weight_id}
```

## Goals Endpoints

### Create Weight Goal
```http
POST /api/goals/weight
```

**Request Body:**
```json
{
  "target_weight": 68.0,
  "target_body_fat_percentage": 12.0,
  "target_muscle_mass_percentage": 48.0
}
```

### Get Weight Goal
```http
GET /api/goals/weight
```

### Update Weight Goal
```http
PUT /api/goals/weight
```

**Request Body:**
```json
{
  "target_weight": 67.0,
  "target_body_fat_percentage": 11.5,
  "target_muscle_mass_percentage": 49.0
}
```

### Delete Weight Goal
```http
DELETE /api/goals/weight
```

## Chat/AI Endpoints

### Chat with AI
```http
POST /api/chat
```

**Request Body:**
```json
{
  "message": "How can I improve my fitness routine?"
}
```

**Response:**
```json
{
  "response": "Based on your current data, I recommend...",
  "timestamp": "2025-01-15T12:00:00+00:00"
}
```

## Workout Tracking Endpoints

### 1. Ingest Active Calories Data

**Endpoint:** `POST /api/ingest-active-calories`

**Request Body:**
```json
{
  "record": {
    "data": {
      "metrics": [
        {
          "name": "active_calories",
          "data": [
            {
              "calories_burned": 150.5,
              "date": "2025-01-15T10:00:00Z",
              "source": "Apple Watch"
            },
            {
              "calories_burned": 200.0,
              "date": "2025-01-15T11:00:00Z",
              "source": "Apple Watch"
            }
          ],
          "units": "calories"
        }
      ]
    }
  },
  "metadata": {
    "id": "workout_session_123",
    "private": false,
    "createdAt": "2025-01-15T12:00:00Z",
    "name": "Morning Workout"
  }
}
```

**Response:**
```json
{
  "message": "Active calories data ingested successfully",
  "records_processed": 2,
  "metrics_processed": ["active_calories"],
  "user_id": "user..abc123def456",
  "source": "POST request"
}
```

### 2. Get Active Calories Data

**Endpoint:** `GET /api/active-calories`

**Query Parameters:**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

**Example:**
```http
GET /api/active-calories?start_date=2025-01-15T00:00:00Z&end_date=2025-01-15T23:59:59Z
```

**Response:**
```json
{
  "records": [
    {
      "user_id": "user..abc123def456",
      "date": "2025-01-15T10:00:00+00:00",
      "calories_burned": 150.5,
      "source": "Apple Watch",
      "created_at": "2025-01-15T12:00:00+00:00",
      "updated_at": null
    },
    {
      "user_id": "user..abc123def456",
      "date": "2025-01-15T11:00:00+00:00",
      "calories_burned": 200.0,
      "source": "Apple Watch",
      "created_at": "2025-01-15T12:00:00+00:00",
      "updated_at": null
    }
  ],
  "total_count": 2,
  "user_id": "user..abc123def456"
}
```

### 3. Ingest Hourly Steps Data

**Endpoint:** `POST /api/ingest-hourly-steps`

**Request Body:**
```json
{
  "record": {
    "data": {
      "metrics": [
        {
          "name": "hourly_steps",
          "data": [
            {
              "steps": 1250,
              "date": "2025-01-15T10:00:00Z",
              "source": "Apple Watch"
            },
            {
              "steps": 980,
              "date": "2025-01-15T11:00:00Z",
              "source": "Apple Watch"
            }
          ],
          "units": "steps"
        }
      ]
    }
  },
  "metadata": {
    "id": "steps_session_123",
    "private": false,
    "createdAt": "2025-01-15T12:00:00Z",
    "name": "Daily Steps"
  }
}
```

**Response:**
```json
{
  "message": "Hourly steps data ingested successfully",
  "records_processed": 2,
  "metrics_processed": ["hourly_steps"],
  "user_id": "user..abc123def456",
  "source": "POST request"
}
```

### 4. Get Hourly Steps Data

**Endpoint:** `GET /api/hourly-steps`

**Query Parameters:**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

**Example:**
```http
GET /api/hourly-steps?start_date=2025-01-15T00:00:00Z&end_date=2025-01-15T23:59:59Z
```

**Response:**
```json
{
  "records": [
    {
      "user_id": "user..abc123def456",
      "date": "2025-01-15T10:00:00+00:00",
      "steps": 1250,
      "source": "Apple Watch",
      "created_at": "2025-01-15T12:00:00+00:00",
      "updated_at": null
    },
    {
      "user_id": "user..abc123def456",
      "date": "2025-01-15T11:00:00+00:00",
      "steps": 980,
      "source": "Apple Watch",
      "created_at": "2025-01-15T12:00:00+00:00",
      "updated_at": null
    }
  ],
  "total_count": 2,
  "user_id": "user..abc123def456"
}
```

## Data Types and Validation

### Active Calories Data Point
```typescript
interface ActiveCaloriesDataPoint {
  calories_burned: number | null; // 0-2000, will be rounded down if float
  date: string; // ISO datetime string
  source: string; // Required, e.g., "Apple Watch", "Fitbit"
}
```

### Hourly Steps Data Point
```typescript
interface HourlyStepsDataPoint {
  steps: number | null; // 0-10000, will be rounded down if float
  date: string; // ISO datetime string
  source: string; // Required, e.g., "Apple Watch", "Fitbit"
}
```

### User ID Format
All user IDs are in RID format: `user..<random-string>`
Example: `user..abc123def456`

## Key Features

### 1. Upsert Behavior
- If a record with the same `(user_id, date, source)` combination exists, it will be updated
- If no record exists, a new one will be created
- This prevents duplicate entries for the same time period and source

### 2. Data Validation
- `calories_burned`: Automatically rounded down to integers if floats are provided
- `steps`: Automatically rounded down to integers if floats are provided
- `source`: Required field, cannot be empty
- `date`: Must be valid ISO datetime string

### 3. Authentication
- All workout endpoints require valid JWT token
- User can only access their own data
- Automatic user identification from JWT token

### 4. Date Filtering
- Both GET endpoints support optional date range filtering
- Use ISO datetime strings for `start_date` and `end_date` parameters
- If no dates provided, returns all records for the authenticated user

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "record", "data", "metrics", 0, "data", 0, "source"],
      "msg": "Field required"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error ingesting data: <error_message>"
}
```

## Example Frontend Integration

### TypeScript Interfaces
```typescript
// User Types
interface User {
  id: string; // RID format: user..<random-string>
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
}

interface Token {
  access_token: string;
  token_type: "bearer";
}

// Heart Rate Types
interface HeartRateDataPoint {
  Min: number; // Will be rounded down if float
  Max: number; // Will be rounded down if float
  date: string; // ISO datetime string
  source: string; // Required
}

interface HeartRateMetric {
  name: "heart_rate";
  data: HeartRateDataPoint[];
  units: "bpm";
}

// Diet Types
interface DietDataPoint {
  protein: number;
  carbs: number;
  fat: number;
  calories: number;
  meal_name: string;
  notes: string | null;
  date: string; // ISO datetime string
  source: string; // Required
}

interface DietMetric {
  name: "diet";
  data: DietDataPoint[];
  units: "grams";
}

interface DietRecord {
  protein: number;
  carbs: number;
  fat: number;
  calories: number;
  meal_name: string;
  notes: string | null;
  datetime: string; // ISO datetime string
  source: string; // Required
}

// Weight Types
interface WeightCreate {
  weight: number;
  body_fat_percentage: number | null;
  muscle_mass_percentage: number | null;
  notes: string | null;
}

interface WeightResponse {
  id: string; // RID format: weight..<random-string>
  user_id: string;
  weight: number;
  body_fat_percentage: number | null;
  muscle_mass_percentage: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

// Goals Types
interface GoalWeightCreate {
  target_weight: number;
  target_body_fat_percentage: number | null;
  target_muscle_mass_percentage: number | null;
}

interface GoalWeightResponse {
  user_id: string;
  target_weight: number;
  target_body_fat_percentage: number | null;
  target_muscle_mass_percentage: number | null;
  created_at: string;
  updated_at: string | null;
}

// Workout Types
interface ActiveCaloriesDataPoint {
  calories_burned: number | null; // 0-2000, will be rounded down if float
  date: string; // ISO datetime string
  source: string; // Required, e.g., "Apple Watch", "Fitbit"
}

interface HourlyStepsDataPoint {
  steps: number | null; // 0-10000, will be rounded down if float
  date: string; // ISO datetime string
  source: string; // Required, e.g., "Apple Watch", "Fitbit"
}

interface ActiveCaloriesMetric {
  name: "active_calories";
  data: ActiveCaloriesDataPoint[];
  units: "calories";
}

interface HourlyStepsMetric {
  name: "hourly_steps";
  data: HourlyStepsDataPoint[];
  units: "steps";
}

// Common Types
interface SessionMetadata {
  id: string;
  name: string;
  createdAt: string;
  private: boolean;
}

interface WorkoutRecord {
  data: {
    metrics: (ActiveCaloriesMetric | HourlyStepsMetric)[];
  };
  metadata: SessionMetadata;
}

interface HeartRateRecord {
  data: {
    metrics: HeartRateMetric[];
  };
  metadata: SessionMetadata;
}

interface DietRecord {
  data: {
    metrics: DietMetric[];
  };
  metadata: SessionMetadata;
}

// Chat Types
interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
  timestamp: string;
}
```

### Complete API Client Example
```typescript
class SupaHealthAPI {
  private baseURL = 'http://localhost:8000';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // System
  async healthCheck() {
    return fetch(`${this.baseURL}/api/health`).then(r => r.json());
  }

  // Authentication
  async getCurrentUser(): Promise<User> {
    return this.request('/api/auth/me');
  }

  async refreshToken(): Promise<Token> {
    return this.request('/api/auth/refresh', { method: 'POST' });
  }

  // Heart Rate
  async ingestHeartRate(data: HeartRateRecord) {
    return this.request('/api/ingest-heart-rate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getHeartRate(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return this.request(`/api/heart-rate?${params.toString()}`);
  }

  // Diet
  async ingestDiet(data: DietRecord) {
    return this.request('/api/ingest-diet', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async addDietRecord(data: DietRecord) {
    return this.request('/api/diet/record', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteDietRecord(recordId: string) {
    return this.request(`/api/diet/record/${recordId}`, {
      method: 'DELETE',
    });
  }

  async getDietData(startDate?: string, endDate?: string, mealName?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (mealName) params.append('meal_name', mealName);
    
    return this.request(`/api/diet?${params.toString()}`);
  }

  async getDailyDietAggregation(date: string) {
    return this.request(`/api/diet/daily/${date}`);
  }

  async getDietAggregation(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return this.request(`/api/diet/aggregate?${params.toString()}`);
  }

  // Weight
  async createWeight(data: WeightCreate) {
    return this.request('/api/weight', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAllWeights() {
    return this.request('/api/weight');
  }

  async getWeight(weightId: string) {
    return this.request(`/api/weight/${weightId}`);
  }

  async updateWeight(weightId: string, data: WeightCreate) {
    return this.request(`/api/weight/${weightId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWeight(weightId: string) {
    return this.request(`/api/weight/${weightId}`, {
      method: 'DELETE',
    });
  }

  // Goals
  async createWeightGoal(data: GoalWeightCreate) {
    return this.request('/api/goals/weight', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWeightGoal() {
    return this.request('/api/goals/weight');
  }

  async updateWeightGoal(data: GoalWeightCreate) {
    return this.request('/api/goals/weight', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWeightGoal() {
    return this.request('/api/goals/weight', {
      method: 'DELETE',
    });
  }

  // Workout
  async ingestActiveCalories(data: WorkoutRecord) {
    return this.request('/api/ingest-active-calories', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getActiveCalories(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return this.request(`/api/active-calories?${params.toString()}`);
  }

  async ingestHourlySteps(data: WorkoutRecord) {
    return this.request('/api/ingest-hourly-steps', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getHourlySteps(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return this.request(`/api/hourly-steps?${params.toString()}`);
  }

  // Chat
  async chat(data: ChatRequest): Promise<ChatResponse> {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Static methods for authentication (no token required)
class AuthAPI {
  private static baseURL = 'http://localhost:8000';

  static async signup(userData: { email: string; password: string; full_name: string }): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Signup Error: ${response.status}`);
    }

    return response.json();
  }

  static async signin(email: string, password: string): Promise<Token> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Signin Error: ${response.status}`);
    }

    return response.json();
  }
}
```

## Testing the API

### 1. Get Authentication Token
```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin"
```

### 2. Test Active Calories Ingestion
```bash
curl -X POST "http://localhost:8000/api/ingest-active-calories" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "record": {
      "data": {
        "metrics": [
          {
            "name": "active_calories",
            "data": [
              {
                "calories_burned": 150.5,
                "date": "2025-01-15T10:00:00Z",
                "source": "Apple Watch"
              }
            ],
            "units": "calories"
          }
        ]
      }
    },
    "metadata": {
      "id": "test_session_123",
      "private": false,
      "createdAt": "2025-01-15T12:00:00Z",
      "name": "Test Workout"
    }
  }'
```

### 3. Test Data Retrieval
```bash
curl -X GET "http://localhost:8000/api/active-calories" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Complete API Endpoint Summary

### System (1 endpoint)
- `GET /api/health` - Health check

### Authentication (4 endpoints)
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh JWT token

### Heart Rate (2 endpoints)
- `POST /api/ingest-heart-rate` - Ingest heart rate data
- `GET /api/heart-rate` - Get heart rate data

### Diet (6 endpoints)
- `POST /api/ingest-diet` - Ingest diet data
- `POST /api/diet/record` - Add single diet record
- `DELETE /api/diet/record/{record_id}` - Delete diet record
- `GET /api/diet` - Get diet data
- `GET /api/diet/daily/{date}` - Get daily diet aggregation
- `GET /api/diet/aggregate` - Get diet aggregation

### Weight (5 endpoints)
- `POST /api/weight` - Create weight record
- `GET /api/weight` - Get all weight records
- `GET /api/weight/{weight_id}` - Get specific weight record
- `PUT /api/weight/{weight_id}` - Update weight record
- `DELETE /api/weight/{weight_id}` - Delete weight record

### Goals (4 endpoints)
- `POST /api/goals/weight` - Create weight goal
- `GET /api/goals/weight` - Get weight goal
- `PUT /api/goals/weight` - Update weight goal
- `DELETE /api/goals/weight` - Delete weight goal

### Workout (4 endpoints)
- `POST /api/ingest-active-calories` - Ingest active calories data
- `GET /api/active-calories` - Get active calories data
- `POST /api/ingest-hourly-steps` - Ingest hourly steps data
- `GET /api/hourly-steps` - Get hourly steps data

### Chat/AI (1 endpoint)
- `POST /api/chat` - Chat with AI

**Total: 27 API endpoints**

This comprehensive specification provides everything needed to integrate the complete SupaHealth API into your frontend application, including all health tracking features: heart rate, diet, weight, goals, workout tracking, and AI chat functionality.
