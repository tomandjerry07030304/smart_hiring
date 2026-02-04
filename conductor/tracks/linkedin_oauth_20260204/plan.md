# Implementation Plan: LinkedIn OAuth Login

## Phase 1: Setup and Configuration
- [ ] Task: Configure LinkedIn Developer Application
    - [ ] Create application in LinkedIn Developer Portal.
    - [ ] Configure Redirect URIs.
    - [ ] Add CLIENT_ID and CLIENT_SECRET to `.env.template` and local `.env`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Configuration' (Protocol in workflow.md)

## Phase 2: Backend Implementation
- [ ] Task: Create OAuth Routes
    - [ ] Write Tests: Authentication routes for LinkedIn redirect and callback.
    - [ ] Implement Feature: `/auth/linkedin/login` and `/auth/linkedin/callback` endpoints in Flask.
- [ ] Task: User Integration
    - [ ] Write Tests: Logic for creating or updating a user from LinkedIn profile data.
    - [ ] Implement Feature: Service logic to fetch LinkedIn profile data and sync with MongoDB.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backend Implementation' (Protocol in workflow.md)

## Phase 3: Frontend Integration
- [ ] Task: Add Login UI
    - [ ] Write Tests: Check for presence of LinkedIn button and correct redirect link.
    - [ ] Implement Feature: Add "Login with LinkedIn" button to `index.html` and relevant templates.
- [ ] Task: Handle Auth State
    - [ ] Implement Feature: Update `app.js` to handle successful OAuth login and store JWT.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Integration' (Protocol in workflow.md)
