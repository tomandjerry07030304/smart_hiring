"""
OpenAPI/Swagger Documentation Generator
=======================================
Automatic API documentation for Smart Hiring System

Features:
- Complete API endpoint documentation
- Request/response schemas
- Authentication documentation
- Example requests and responses
- Interactive Swagger UI integration
- Downloadable OpenAPI 3.0 spec

Author: Smart Hiring System Team
Date: December 2025
"""

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields
import json


# Define schemas for documentation
class ErrorSchema(Schema):
    """Error response schema"""
    error = fields.Str(required=True, description="Error message")
    code = fields.Int(description="Error code")


class UserSchema(Schema):
    """User schema"""
    id = fields.Str(description="User ID")
    email = fields.Email(required=True, description="User email")
    role = fields.Str(required=True, description="User role (candidate/recruiter/admin)")
    full_name = fields.Str(description="Full name")
    created_at = fields.DateTime(description="Account creation timestamp")


class LoginSchema(Schema):
    """Login request schema"""
    email = fields.Email(required=True, description="User email")
    password = fields.Str(required=True, description="Password")


class TokenSchema(Schema):
    """Authentication token response"""
    access_token = fields.Str(required=True, description="JWT access token")
    refresh_token = fields.Str(description="JWT refresh token")
    user = fields.Nested(UserSchema)


class JobSchema(Schema):
    """Job posting schema"""
    id = fields.Str(description="Job ID")
    title = fields.Str(required=True, description="Job title")
    description = fields.Str(required=True, description="Job description")
    company_name = fields.Str(required=True, description="Company name")
    location = fields.Str(description="Job location")
    required_skills = fields.List(fields.Str(), description="Required skills")
    min_experience_years = fields.Int(description="Minimum years of experience")
    salary_range = fields.Dict(description="Salary range")
    status = fields.Str(description="Job status (active/closed/filled)")
    created_at = fields.DateTime(description="Creation timestamp")


class ApplicationSchema(Schema):
    """Job application schema"""
    id = fields.Str(description="Application ID")
    job_id = fields.Str(required=True, description="Job ID")
    candidate_id = fields.Str(description="Candidate ID")
    resume_url = fields.Str(description="Resume file URL")
    cover_letter = fields.Str(description="Cover letter text")
    status = fields.Str(description="Application status")
    parsed_resume = fields.Dict(description="Parsed resume data")
    job_match_score = fields.Dict(description="Job matching scores")
    fairness_audit = fields.Dict(description="Fairness audit results")
    created_at = fields.DateTime(description="Submission timestamp")


class AssessmentSchema(Schema):
    """Assessment schema"""
    id = fields.Str(description="Assessment ID")
    title = fields.Str(required=True, description="Assessment title")
    description = fields.Str(description="Assessment description")
    questions = fields.List(fields.Dict(), description="Assessment questions")
    time_limit_minutes = fields.Int(description="Time limit in minutes")
    passing_score = fields.Int(description="Minimum passing score")


class NotificationSchema(Schema):
    """Notification schema"""
    id = fields.Str(description="Notification ID")
    user_id = fields.Str(description="Recipient user ID")
    type = fields.Str(description="Notification type")
    title = fields.Str(description="Notification title")
    message = fields.Str(description="Notification message")
    data = fields.Dict(description="Additional notification data")
    read = fields.Bool(description="Read status")
    created_at = fields.DateTime(description="Creation timestamp")


class FairnessMetricsSchema(Schema):
    """Fairness evaluation metrics"""
    demographic_parity = fields.Float(description="Demographic parity difference")
    disparate_impact = fields.Float(description="Disparate impact ratio")
    equal_opportunity = fields.Float(description="Equal opportunity difference")
    equalized_odds = fields.Float(description="Equalized odds difference")
    overall_fairness_score = fields.Float(description="Overall fairness score (0-1)")
    is_fair = fields.Bool(description="Whether evaluation passed fairness thresholds")


class AnalyticsSchema(Schema):
    """Analytics dashboard data"""
    summary = fields.Dict(description="Summary statistics")
    charts = fields.Dict(description="Chart data")
    diversity = fields.Dict(description="Diversity metrics")
    period_days = fields.Int(description="Analysis period in days")


def create_api_spec():
    """
    Create OpenAPI specification for Smart Hiring System API
    
    Returns:
        APISpec instance with full API documentation
    """
    spec = APISpec(
        title="Smart Hiring System API",
        version="2.0.0",
        openapi_version="3.0.3",
        info=dict(
            description="""
# Smart Hiring System API Documentation

## Overview
The Smart Hiring System provides a comprehensive, AI-powered recruitment platform with built-in fairness auditing and bias detection.

## Features
- 🤖 AI-powered resume parsing and candidate matching
- ⚖️ Automated fairness auditing with multiple metrics
- 📊 Real-time analytics and reporting
- 🔔 WebSocket-based real-time notifications
- 📧 Automated email notifications
- 🎯 Skills-based candidate ranking
- 📝 Customizable assessments and quizzes
- 🔐 Secure authentication with JWT
- 🌐 RESTful API design

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting
- Unauthenticated: 100 requests/hour
- Authenticated: 1000 requests/hour
- Admin: Unlimited

## Response Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Fairness Guarantees
All candidate evaluations undergo automated fairness auditing using:
- Demographic Parity Analysis
- Disparate Impact Measurement
- Equal Opportunity Assessment
- Equalized Odds Verification

Results below fairness thresholds are flagged for review.
            """,
            contact=dict(
                name="Smart Hiring System Team",
                email="support@smarthiring.com",
                url="https://github.com/your-repo"
            ),
            license=dict(
                name="MIT",
                url="https://opensource.org/licenses/MIT"
            )
        ),
        servers=[
            dict(url="https://api.smarthiring.com/v1", description="Production Server"),
            dict(url="https://staging-api.smarthiring.com/v1", description="Staging Server"),
            dict(url="http://localhost:5000", description="Local Development Server")
        ],
        plugins=[MarshmallowPlugin(), FlaskPlugin()],
    )
    
    # Add security scheme
    api_key_scheme = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    spec.components.security_scheme("bearerAuth", api_key_scheme)
    
    # Register schemas
    spec.components.schema("Error", schema=ErrorSchema)
    spec.components.schema("User", schema=UserSchema)
    spec.components.schema("Login", schema=LoginSchema)
    spec.components.schema("Token", schema=TokenSchema)
    spec.components.schema("Job", schema=JobSchema)
    spec.components.schema("Application", schema=ApplicationSchema)
    spec.components.schema("Assessment", schema=AssessmentSchema)
    spec.components.schema("Notification", schema=NotificationSchema)
    spec.components.schema("FairnessMetrics", schema=FairnessMetricsSchema)
    spec.components.schema("Analytics", schema=AnalyticsSchema)
    
    # Add example paths/operations
    spec.path(
        path="/auth/register",
        operations=dict(
            post=dict(
                tags=["Authentication"],
                summary="Register new user",
                description="Create a new user account (candidate or recruiter)",
                requestBody={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["email", "password", "role", "full_name"],
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "minLength": 8},
                                    "role": {"type": "string", "enum": ["candidate", "recruiter"]},
                                    "full_name": {"type": "string"}
                                }
                            },
                            "example": {
                                "email": "john.doe@example.com",
                                "password": "SecureP@ss123",
                                "role": "candidate",
                                "full_name": "John Doe"
                            }
                        }
                    }
                },
                responses={
                    "201": {
                        "description": "User created successfully",
                        "content": {
                            "application/json": {
                                "schema": TokenSchema
                            }
                        }
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": ErrorSchema
                            }
                        }
                    }
                }
            )
        )
    )
    
    spec.path(
        path="/auth/login",
        operations=dict(
            post=dict(
                tags=["Authentication"],
                summary="User login",
                description="Authenticate user and receive JWT tokens",
                requestBody={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": LoginSchema,
                            "example": {
                                "email": "john.doe@example.com",
                                "password": "SecureP@ss123"
                            }
                        }
                    }
                },
                responses={
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": TokenSchema
                            }
                        }
                    },
                    "401": {
                        "description": "Invalid credentials",
                        "content": {
                            "application/json": {
                                "schema": ErrorSchema
                            }
                        }
                    }
                }
            )
        )
    )
    
    spec.path(
        path="/jobs",
        operations=dict(
            get=dict(
                tags=["Jobs"],
                summary="List all jobs",
                description="Get paginated list of job postings with optional filtering",
                parameters=[
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["active", "closed", "filled"]}},
                    {"name": "search", "in": "query", "schema": {"type": "string"}}
                ],
                responses={
                    "200": {
                        "description": "Jobs retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "jobs": {"type": "array", "items": JobSchema},
                                        "total": {"type": "integer"},
                                        "page": {"type": "integer"},
                                        "per_page": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            ),
            post=dict(
                tags=["Jobs"],
                summary="Create new job",
                description="Post a new job opening (recruiter only)",
                security=[{"bearerAuth": []}],
                requestBody={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": JobSchema
                        }
                    }
                },
                responses={
                    "201": {
                        "description": "Job created successfully",
                        "content": {
                            "application/json": {
                                "schema": JobSchema
                            }
                        }
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - recruiter role required"}
                }
            )
        )
    )
    
    spec.path(
        path="/applications",
        operations=dict(
            post=dict(
                tags=["Applications"],
                summary="Submit job application",
                description="Apply to a job posting with resume",
                security=[{"bearerAuth": []}],
                requestBody={
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["job_id", "resume"],
                                "properties": {
                                    "job_id": {"type": "string"},
                                    "resume": {"type": "string", "format": "binary"},
                                    "cover_letter": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                responses={
                    "201": {
                        "description": "Application submitted successfully",
                        "content": {
                            "application/json": {
                                "schema": ApplicationSchema
                            }
                        }
                    }
                }
            )
        )
    )
    
    spec.path(
        path="/analytics/dashboard",
        operations=dict(
            get=dict(
                tags=["Analytics"],
                summary="Get dashboard analytics",
                description="Retrieve comprehensive analytics and metrics",
                security=[{"bearerAuth": []}],
                parameters=[
                    {"name": "days", "in": "query", "schema": {"type": "integer", "default": 30}}
                ],
                responses={
                    "200": {
                        "description": "Analytics data retrieved",
                        "content": {
                            "application/json": {
                                "schema": AnalyticsSchema
                            }
                        }
                    }
                }
            )
        )
    )
    
    spec.path(
        path="/fairness/evaluate",
        operations=dict(
            post=dict(
                tags=["Fairness"],
                summary="Evaluate fairness metrics",
                description="Run fairness audit on candidate evaluation data",
                security=[{"bearerAuth": []}],
                requestBody={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["predictions", "labels", "sensitive_features"],
                                "properties": {
                                    "predictions": {"type": "array", "items": {"type": "integer"}},
                                    "labels": {"type": "array", "items": {"type": "integer"}},
                                    "sensitive_features": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    }
                },
                responses={
                    "200": {
                        "description": "Fairness metrics calculated",
                        "content": {
                            "application/json": {
                                "schema": FairnessMetricsSchema
                            }
                        }
                    }
                }
            )
        )
    )
    
    return spec


def generate_swagger_json():
    """
    Generate Swagger/OpenAPI JSON specification
    
    Returns:
        JSON string of API specification
    """
    spec = create_api_spec()
    return json.dumps(spec.to_dict(), indent=2)


def generate_swagger_yaml():
    """
    Generate Swagger/OpenAPI YAML specification
    
    Returns:
        YAML string of API specification
    """
    import yaml
    spec = create_api_spec()
    return yaml.dump(spec.to_dict(), default_flow_style=False)


if __name__ == "__main__":
    # Generate and save OpenAPI spec
    print("Generating OpenAPI 3.0 specification...")
    
    spec_json = generate_swagger_json()
    with open("openapi.json", "w") as f:
        f.write(spec_json)
    
    print("✅ Generated: openapi.json")
    print("📖 View in Swagger UI: https://editor.swagger.io/")
    print("📘 API Documentation complete!")
