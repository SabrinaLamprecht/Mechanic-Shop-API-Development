Mechanic Shop API Project

This project is a API built using Flask, SQLAlchemy, Marshmallow, Flask-Limiter, and Flask-Caching. This project simulates a backend system for a mechanic shop. It manages four main resources: customers, mechanics, service tickets, and inventory.

It features:
--- CRUD operatins for all major resources
--- Many-to-Many relationship between Service Tickts and Mechanics
--- One-to-Many relationship between Customers and Service Tickets
--- Data serialization & validation using Marshmallow schemas
--- MySQL database integration with SQLAlchemy ORM
--- Rate limiting using Flask-Limiter
--- Caching with Flask-Caching
--- Fully tested endpoints using Postman
--- Full API Documentation with Flask_Swagger and Swagger-UI
--- Unit tests for every endpoint using Pythons's built in unittest module

Instructions:

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Configure MySQL Database
5. Initialize the Database
6. For API Documentation - use the Swagger UI available at: http://localhost:5000/api/docs
7. For unit testing, run the following (below) in the terminal: \***\* Windows: python -m unittest discover tests
   \*\*** Mac/Linux: python3 -m unittest discover tests
