# BreakFree API Contract

## Overview
This document describes the REST API contract for the BreakFree backend. The service is currently implemented as a Django REST Framework application with JWT-based authentication.

Base URL (local development):
- http://127.0.0.1:8000

## Authentication

### JWT auth
The API uses Django REST Framework Simple JWT.

- Login returns access and refresh tokens.
- Protected routes require the `Authorization: Bearer <access_token>` header.

### Endpoints

#### 1. Register a user
- Method: `POST`
- Path: `/register/`
- Auth: None
- Request body:

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string"
}
```

- Success response: `201 Created`
- Error response: `400 Bad Request`

#### 2. Login
- Method: `POST`
- Path: `/login/`
- Auth: None
- Request body:

```json
{
  "username": "string",
  "password": "string"
}
```

- Success response:

```json
{
  "refresh": "string",
  "access": "string"
}
```

#### 3. Refresh access token
- Method: `POST`
- Path: `/refresh_login/`
- Auth: None
- Request body:

```json
{
  "refresh": "string"
}
```

## User and Profile

#### 4. Get home feed
- Method: `GET`
- Path: `/`
- Auth: Required
- Query parameters:
  - `genre` (optional): filter rooms by genre name
  - `page` (optional): pagination page number

- Success response: `200 OK`
- Response shape:

```json
{
  "has_next": true,
  "has_previous": false,
  "next_page_number": -1,
  "previous_page_number": -1,
  "genres": [
    {
      "id": 1,
      "name": "Fitness"
    }
  ],
  "genre_name": "",
  "rooms": [
    {
      "host": 1,
      "room_name": "Morning Run",
      "genre": 1,
      "participants": [1, 2],
      "description": "Daily streak room",
      "password": "",
      "private": false,
      "created": "2026-07-19T12:00:00Z",
      "updated": "2026-07-19T12:00:00Z",
      "room_authenticated": true
    }
  ],
  "is_authenticated": true
}
```

#### 5. Get user profile
- Method: `GET`
- Path: `/profile/<int:pk>/`
- Auth: Required
- Success response: `200 OK`
- Response shape:

```json
{
  "user": {
    "id": 1,
    "username": "alice",
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice@example.com"
  },
  "bio": "Hello world",
  "phone_no": "1234567890",
  "profile_pic": "http://127.0.0.1:8000/media/pp/default.jpg",
  "friend_count": 2,
  "is_friend": false,
  "pending": false
}
```

#### 6. Get editable profile data
- Method: `GET`
- Path: `/edit_profile/`
- Auth: Required
- Success response: `200 OK`

#### 7. Update profile
- Method: `PATCH`
- Path: `/edit_profile/`
- Auth: Required
- Request body:

```json
{
  "user": {
    "username": "new_username",
    "email": "new@example.com"
  },
  "profile": {
    "bio": "Updated bio",
    "phone_no": "9876543210",
    "profile_pic": "file"
  }
}
```

- Success response: `200 OK`
- Error response: `400 Bad Request` or `401 Unauthorized`

## Rooms

#### 8. Create a room
- Method: `POST`
- Path: `/room_viewset/`
- Auth: Required
- Request body:

```json
{
  "host": 1,
  "room_name": "Morning Jog",
  "genre_name": "Fitness",
  "description": "Join the daily streak",
  "password": "secret",
  "private": false
}
```

- Success response: `201 Created`

#### 9. List rooms
- Method: `GET`
- Path: `/room_viewset/`
- Auth: Required
- Success response: `200 OK`

#### 10. Retrieve a room
- Method: `GET`
- Path: `/room_viewset/<id>/`
- Auth: Required
- Success response: `200 OK`

#### 11. Update a room
- Method: `PATCH`
- Path: `/room_viewset/<id>/`
- Auth: Required
- Success response: `200 OK`

#### 12. Delete a room
- Method: `DELETE`
- Path: `/room_viewset/<id>/`
- Auth: Required
- Success response: `204 No Content`

#### 13. Get room details and participants
- Method: `GET`
- Path: `/room/<int:pk>/`
- Auth: Required
- Success response: `200 OK`
- Response shape:

```json
{
  "room_info": {
    "room_name": "Morning Jog",
    "description": "Join the daily streak"
  },
  "participants": [
    {
      "id": 1,
      "username": "alice"
    }
  ],
  "leaderboard": [
    {
      "rank": 1,
      "user": {
        "id": 1,
        "username": "alice"
      },
      "raw_timesince": "00:15:30"
    }
  ],
  "counting": false
}
```

#### 14. Authorize room access
- Method: `POST`
- Path: `/room_authorize/<int:pk>/`
- Auth: None or optional
- Request body:

```json
{
  "password": "secret"
}
```

- Success response: `200 OK`
- Invalid password response: `401 Unauthorized`

#### 15. List room participants
- Method: `GET`
- Path: `/room_participants/<int:pk>`
- Auth: Required
- Success response: `200 OK`
- Response shape:

```json
{
  "room_name": "Morning Jog",
  "participants": [
    {
      "username": "alice"
    }
  ],
  "is_user_host": true,
  "is_user_moderator": false,
  "is_room_private": true
}
```

## Genres

#### 16. List genres
- Method: `GET`
- Path: `/view_all_genre/`
- Auth: Required
- Success response: `200 OK`

## Friends and Requests

#### 17. Send a friend request
- Method: `POST`
- Path: `/create_friend_request/<int:pk>/`
- Auth: Required
- Success response: `201 Created`

#### 18. View incoming friend requests
- Method: `GET`
- Path: `/view_friend_requests/`
- Auth: Required
- Success response: `200 OK`

#### 19. Accept a friend request
- Method: `POST`
- Path: `/accept_friend_request/<int:pk>/`
- Auth: Required
- Success response: `200 OK`

#### 20. Reject a friend request
- Method: `POST`
- Path: `/reject_friend_request/<int:pk>/`
- Auth: Required
- Success response: `204 No Content`

#### 21. Remove a friend
- Method: `POST`
- Path: `/remove_friend/<int:pk>/`
- Auth: Required
- Success response: `204 No Content`

#### 22. View friend list
- Method: `GET`
- Path: `/friend_list/`
- Auth: Required
- Success response: `200 OK`

#### 23. Search friends or users
- Method: `GET`
- Path: `/search_friend/`
- Auth: Required
- Query parameters:
  - `search` (required): search term
- Success response: `200 OK`

## Counter and Leaderboard

#### 24. Start counter for a room
- Method: `POST`
- Path: `/start_counter/<int:pk>/`
- Auth: Required
- Success response: `200 OK`

#### 25. Stop counter for a room
- Method: `POST`
- Path: `/stop_counter/<int:pk>/`
- Auth: Required
- Success response: `200 OK`

#### 26. View room leaderboard
- Method: `GET`
- Path: `/view_leaderboard/<int:pk>/`
- Auth: Required
- Success response: `200 OK`

## Moderation

#### 27. Add a moderator
- Method: `POST`
- Path: `/add_moderator/<int:room_pk>/user/<int:user_pk>/`
- Auth: Required
- Success response: `201 Created`

#### 28. Remove a moderator
- Method: `POST`
- Path: `/remove_moderator/<int:room_pk>/user/<int:user_pk>/`
- Auth: Required
- Success response: `404 Not Found` in the current implementation

#### 29. Remove a participant
- Method: `POST`
- Path: `/remove_participant/<int:room_pk>/user/<int:user_pk>/`
- Auth: Required
- Success response: `404 Not Found` in the current implementation

## Common Data Models

### User
```json
{
  "id": 1,
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

### Profile
```json
{
  "user": { "id": 1, "username": "string" },
  "bio": "string",
  "phone_no": "string",
  "profile_pic": "string"
}
```

### Room
```json
{
  "id": 1,
  "host": 1,
  "room_name": "string",
  "genre": 1,
  "participants": [1, 2],
  "description": "string",
  "password": "string",
  "private": false,
  "created": "datetime",
  "updated": "datetime"
}
```

## Notes
- Some endpoints currently return `404 Not Found` for moderator removal and participant removal actions even on successful delete operations; this is worth aligning with the intended API behavior in a future refactor.
- The API is currently route-oriented and does not yet expose a fully formal OpenAPI schema.
