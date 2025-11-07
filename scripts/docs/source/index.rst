Weather Activity Recommendation API Documentation
===================================================

Welcome to the Weather Activity Recommendation API documentation. This FastAPI application provides weather information, activity recommendations, and user management features.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   api_reference
   autoapi/index

Project Overview
================

This API provides the following main functionality:

* **Weather Services**: Get current weather conditions and forecasts
* **Activity Recommendations**: Discover activities based on weather and preferences  
* **User Management**: User registration, authentication, and profile management
* **Voting System**: Rate and vote on activities and recommendations
* **Air Quality**: Monitor air quality conditions
* **Admin Features**: Administrative functions and user management

Getting Started
===============

Installation
------------

1. Clone the repository
2. Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

3. Run the application:

.. code-block:: bash

   uvicorn app.main:app --reload

The API will be available at http://localhost:8000

API Documentation
=================

Interactive API documentation is available at:

* **Swagger UI**: http://localhost:8000/docs
* **ReDoc**: http://localhost:8000/redoc

Project Structure
=================

.. code-block::

   app/
   ├── main.py              # FastAPI application entry point
   ├── data/                # Data storage and management
   ├── models/              # Data models and database schemas
   │   ├── db/              # Database models
   │   ├── requests/        # Request models
   │   └── response/        # Response models
   ├── routes/              # API route definitions
   ├── services/            # Business logic and external services
   tests/                   # Test suite

Key Features
============

Weather Integration
-------------------
Get real-time weather data and forecasts to power activity recommendations.

Activity Recommendations  
------------------------
Intelligent activity suggestions based on current weather conditions and user preferences.

User Management
---------------
Complete user lifecycle management including registration, authentication, and preferences.

Voting & Feedback
-----------------
Community-driven rating system for activities and recommendations.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`