API Reference
=============

This section provides detailed information about the API endpoints, request/response formats, and usage examples.

For interactive API documentation, visit:

* **Swagger UI**: http://localhost:8000/docs  
* **ReDoc**: http://localhost:8000/redoc

Main Endpoints
--------------

The API is organized into the following main endpoint groups:

Weather Endpoints
~~~~~~~~~~~~~~~~~
Retrieve weather information and forecasts.

**Base Path**: ``/weather``

Activity Endpoints  
~~~~~~~~~~~~~~~~~~
Get activity recommendations and manage activities.

**Base Path**: ``/activities``

User Management
~~~~~~~~~~~~~~~
Handle user registration, authentication, and profile management.

**Base Paths**: ``/user``, ``/users``

Voting System
~~~~~~~~~~~~~
Rate and vote on activities and recommendations.

**Base Path**: ``/vote``

Air Quality
~~~~~~~~~~~
Monitor air quality conditions.

**Base Path**: ``/air-quality``

Admin Functions
~~~~~~~~~~~~~~~
Administrative endpoints for system management.

**Base Path**: ``/admin``

Response Formats
----------------

All API responses follow a consistent JSON format:

.. code-block:: json

   {
     "status": "success|error",
     "data": {...},
     "message": "Optional status message"
   }

Error Handling
--------------

The API uses standard HTTP status codes:

* **200**: Success
* **400**: Bad Request  
* **401**: Unauthorized
* **404**: Not Found
* **422**: Validation Error
* **500**: Internal Server Error

Authentication
--------------

Some endpoints require authentication. Include the authentication token in the request headers:

.. code-block:: http

   Authorization: Bearer <your-token>

Rate Limiting
-------------

API requests may be subject to rate limiting to ensure fair usage and system stability.

For detailed endpoint documentation, see the automatically generated API reference in the next section.