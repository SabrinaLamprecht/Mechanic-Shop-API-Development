# /app/blueprints/customers/routes.py

from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# Customer login (with token) ⚡ Tested!
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials ['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()
    
    if customer and customer.password == password:
        token = encode_token(customer.id, user_type='customer')
        
        response = {
            'status': 'success',
            'message': 'Successfully logged in.',
            'token': token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401
       
# Create a customer ⚡ Tested!
@customers_bp.route("/", methods=['POST'])
# Rate limit applied
@limiter.limit("15 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201
 
# Get all customers ⚡ Tested!
@customers_bp.route("/", methods=['GET'])
# Rate limit applied
@limiter.exempt
# Caching applied
@cache.cached(timeout=30)
# Pagination 
def get_customers():
    try: 
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200

# Get a specific customer ⚡ Tested!
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer: 
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# Update a specific customer ⚡ Tested!
@customers_bp.route("/", methods=["PUT"])
@token_required(required_type='customer')
# Rate limit applied
@limiter.limit('5 per hour')
def update_customer(user_id, user_type):
    customer = db.session.get(Customer, user_id)
    
    if not customer: 
        return jsonify({"error": "Customer not found."}), 404
    
    try: 
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# Delete a specific customer ⚡ Tested!
@customers_bp.route("/", methods=["DELETE"])
@token_required(required_type='customer')
# Rate limit applied
@limiter.limit("5 per hour") 
def delete_customer(user_id, user_type):
    customer = db.session.get(Customer, user_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {user_id}, successfully deleted.'}), 200

# Search for a customer based on email ⚡ Tested!
@customers_bp.route("/search", methods=['GET'])
def search_by_email():
    email = request.args.get("email")
    
    query = select(Customer).where(Customer.email.like(f'%{email}%'))
    customer = db.session.execute(query).scalars().first()
    
    return customer_schema.jsonify(customer)
    