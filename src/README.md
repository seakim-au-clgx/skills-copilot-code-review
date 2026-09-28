# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active announcements
- Authenticated teachers can create, edit, and delete announcements

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
| GET    | `/announcements`                                                   | Get announcements active today                                      |
| GET    | `/announcements/manage?teacher_username=mrodriguez`               | Get all announcements for a signed-in teacher                       |
| POST   | `/announcements?teacher_username=mrodriguez`                       | Create an announcement                                              |
| PUT    | `/announcements/{announcement_id}?teacher_username=mrodriguez`     | Update an announcement                                              |
| DELETE | `/announcements/{announcement_id}?teacher_username=mrodriguez`     | Delete an announcement                                              |

Announcement create and update requests use a JSON body with a required
`message` and `expiration_date` (`YYYY-MM-DD`), plus an optional `start_date`.
The expiration date must be on or after the start date.

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

All data is stored in MongoDB and example data is inserted by `database.py` when
the corresponding collection is empty.
