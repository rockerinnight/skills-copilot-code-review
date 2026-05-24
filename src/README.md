# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active announcements
- Manage announcements (authenticated teachers/admin)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get active announcements only                                       |
| GET    | `/announcements/all?teacher_username=<username>`                 | Get all announcements for management                                |
| POST   | `/announcements?message=<text>&expiration_date=YYYY-MM-DD&teacher_username=<username>` | Create announcement (start date optional)                          |
| PUT    | `/announcements/{announcement_id}?message=<text>&expiration_date=YYYY-MM-DD&teacher_username=<username>` | Update announcement (start date optional)                          |
| DELETE | `/announcements/{announcement_id}?teacher_username=<username>`    | Delete announcement                                                 |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in MongoDB (`mergington_high`), including activities, teacher accounts, and announcements.
