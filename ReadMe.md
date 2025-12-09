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
--- CI/CD Pipeline

Instructions:

1. Clone the repository:
   git clone <repository_url>

2. Create and activate a virtual environment:

# Windows

python -m venv venv
venv\Scripts\activate

# Mac/Linux

python3 -m venv venv
source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure Environment Variables:
   export SECRET_KEY
   export DATABASE_URL

5. Initialize the Database:
   flask db upgrade

6. Run the API:
   flask run - use the Swagger UI available at: http://localhost:5000/api/docs

7. Test & Swagger Run:

# Windows

python -m unittest discover tests

# Mac/Linux

python3 -m unittest discover tests

8. Viewing API Documentation (SwaggerUI):
   Once the server is running, navigate to: http://localhost:5000/api/docs and:

- Explore all endpoints
- Try requests directly from the browser
- View request/response schemas
