# /app/blueprints/mechanics/routes.py

from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, Service_Ticket, db
from . import mechanics_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# Login Authorization (with token) ⚡ Tested!
@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials ['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id, user_type='mechanic')
        
        response = {
            'status': 'success',
            'message': 'Successfully logged in.',
            'token': token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401

# Create a mechanic ⚡ Tested!
@mechanics_bp.route("/", methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
        
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# Get all mechanics ⚡ Tested!
@mechanics_bp.route("/", methods=['GET'])
# Caching applied
@cache.cached(timeout=20)
# Pagination 
def get_mechanics():
    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    except:
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics), 200


# Get a specific mechanic ⚡ Tested!
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
# Rate limit applied
@limiter.limit("20 per day")
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if mechanic: 
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found"}), 404

# Update a specific mechanic  ⚡ Tested!
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
@token_required(required_type='mechanic')
# Rate limit applied
@limiter.limit('5 per day')
def update_mechanic(user_id, user_type, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic: 
        return jsonify({"error": "Mechanic not found."}), 404
    
    try: 
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
    
# Delete a specific mechanic ⚡ Tested!
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@token_required(required_type='mechanic') 
# Rate limit applied
@limiter.limit('5 per day')
def delete_mechanic(user_id, user_type, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200

# Add mechanic to service ticket ⚡ Tested!
@mechanics_bp.route("/<int:mechanic_id>/add-ticket/<int:ticket_id>", methods=['POST'])
@token_required(required_type='mechanic')
def add_mechanic_to_ticket(user_id, user_type, mechanic_id, ticket_id):

    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Service_Ticket, ticket_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    if not ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    # Avoid duplicates
    if ticket in mechanic.service_tickets:
        return jsonify({"message": "Mechanic is already assigned to this ticket."}), 200
    
    mechanic.service_tickets.append(ticket)
    db.session.commit()

    return jsonify({"message": f"Mechanic {mechanic_id} assigned to ticket {ticket_id}."}), 200

# Remove mechanic from service ticket ⚡ Tested!
@mechanics_bp.route("/<int:mechanic_id>/remove-ticket/<int:ticket_id>", methods=['DELETE'])
@token_required(required_type='mechanic')
def remove_mechanic_from_ticket(user_id, user_type, mechanic_id, ticket_id):

    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Service_Ticket, ticket_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    if not ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    # Check if mechanic is even assigned
    if ticket not in mechanic.service_tickets:
        return jsonify({"message": "Mechanic is not assigned to this ticket."}), 400

    mechanic.service_tickets.remove(ticket)
    db.session.commit()

    return jsonify({"message": f"Mechanic {mechanic_id} removed from ticket {ticket_id}."}), 200

# Get mechanics who have worked on the most tickets ⚡ Tested!
@mechanics_bp.route("/popular", methods=['GET'])
def popular_mechanic():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    
    return mechanics_schema.jsonify(mechanics)


