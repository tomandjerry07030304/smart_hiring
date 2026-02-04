# Specification: LinkedIn OAuth Login

## Overview
Implement a secure OAuth 2.0 flow using LinkedIn as an identity provider. This will allow candidates to register and log in to the Smart Hiring System using their LinkedIn profiles, automatically pulling relevant profile data to populate their accounts.

## User Stories
- As a candidate, I want to sign up using my LinkedIn account so that I don't have to fill out a long registration form.
- As a candidate, I want to log in securely using LinkedIn to access my dashboard.
- As a recruiter, I want candidates to have verified LinkedIn profiles linked to their applications.

## Functional Requirements
- "Login with LinkedIn" button on the frontend registration/login pages.
- Backend OAuth2 flow handling:
    - Redirect to LinkedIn authorization page.
    - Handle the callback/redirect URI.
    - Exchange authorization code for an access token.
    - Retrieve candidate's basic profile (name, email, profile picture URL) and optionally professional details.
- User account creation/linkage in MongoDB.
- JWT generation for the authenticated session.

## Technical Constraints
- Use `requests-oauthlib` for handling the OAuth flow (as identified in the tech stack).
- Store LinkedIn Client ID and Client Secret in environment variables (`.env`).
- Ensure HTTPS is used for redirect URIs (or handled correctly in development).
