# /app/blueprints/service_tickets/routes.py

from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema, return_service_ticket_schema, add_part_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_Ticket, db, Inventory
from . import service_tickets_bp
from app.models import Mechanic, Customer, ServiceTicketInventory
from app.utils.util import token_required
from app.extensions import limiter

# Create a service ticket ⚡ Tested!
@service_tickets_bp.route("/", methods=['POST'])
def create_service_ticket():
    try: 
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = Service_Ticket(
        VIN=service_ticket_data["VIN"],
        service_date=service_ticket_data.get("service_date"),
        service_desc=service_ticket_data["service_desc"],
        customer_id=service_ticket_data["customer_id"]
    )
    
    # Validate mechanic IDs
    mechanic_ids = service_ticket_data.get("mechanic_ids", [])

    if mechanic_ids:
        # Fetch mechanics that actually exist
        found_mechanics = (
            db.session.query(Mechanic)
            .filter(Mechanic.id.in_(mechanic_ids))
            .all()
        )

        found_ids = {m.id for m in found_mechanics}
        requested_ids = set(mechanic_ids)

        # Compare sets to find missing IDs
        missing_ids = requested_ids - found_ids

        if missing_ids:
            return jsonify({
                "error": "Some mechanic IDs do not exist.",
                "invalid_mechanic_ids": list(missing_ids)
            }), 400

        # If everything checks out, attach mechanics
        new_service_ticket.mechanics = found_mechanics

    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket), 201
        

# Get all service tickets ⚡ Tested!
@service_tickets_bp.route("/", methods=['GET'])
# Rate limit applied
@limiter.exempt
# Pagination 
def get_service_tickets():
    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Service_Ticket)
        service_tickets = db.paginate(query, page=page, per_page=per_page)
        return service_tickets_schema.jsonify(service_tickets), 200
    except:
        query = select(Service_Ticket)
        service_tickets = db.session.execute(query).scalars().all()
        return service_tickets_schema.jsonify(service_tickets), 200

# Get a specific ticket ⚡ Tested!
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['GET'])
# Rate limit applied
@limiter.exempt
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_Ticket, service_ticket_id)
    
    if service_ticket:       
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({'error': "Invalid service ticket ID."}), 404

# Update a service ticket by adding or removing mechanic(s) ⚡ Tested!
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def update_mechanics_on_ticket(service_ticket_id):
    try:
        edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Fetch ticket
    service_ticket = db.session.get(Service_Ticket, service_ticket_id)
    if not service_ticket:
        return jsonify({"message": "Service ticket not found."}), 404
    
    # Add mechanics
    for mechanic_id in edits.get('add_ids', []):
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"message": f"Mechanic ID {mechanic_id} not found."}), 404
        if mechanic in service_ticket.mechanics:
            continue  # skip duplicates
        service_ticket.mechanics.append(mechanic)

    # Remove mechanics
    for mechanic_id in edits.get('remove_ids', []):
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()

    return return_service_ticket_schema.jsonify(service_ticket), 200


# Get all service tickets for a specific customer ⚡ Tested!
@service_tickets_bp.route("/my-tickets", methods=['GET'])
@token_required (required_type='customer')
def get_my_tickets(user_id, user_type):
    query = select(Service_Ticket).where(Service_Ticket.customer_id == user_id)
    service_tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_tickets), 200

# Update a service ticket by adding a part ⚡ Tested!
@service_tickets_bp.route("/<int:service_ticket_id>/add-part", methods=['PUT'])
def add_part(service_ticket_id):
    try: 
        service_ticket_edits = add_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    service_ticket = db.session.get(Service_Ticket, service_ticket_id)
    if not service_ticket:
        return jsonify({"message": "Service ticket not found."}), 404
    
    part_id = service_ticket_edits['part_id']
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": f"Part ID {part_id} not found."}), 404
    
    # Check if part already exists in this ticket
    existing_link = db.session.scalar(
        select(ServiceTicketInventory).where(
            ServiceTicketInventory.service_ticket_id == service_ticket_id,
            ServiceTicketInventory.inventory_id == part_id
        )
    )
    
    
    if existing_link:
        return jsonify({"message": f"Part {part.part_name} already added to ticket."}), 400

    # Create the association
    new_link = ServiceTicketInventory(
        service_ticket_id=service_ticket_id,
        inventory_id=part_id,
        quantity=1  # default quantity, you can extend your schema to allow custom quantity
    )
    db.session.add(new_link)
    db.session.commit()

    return jsonify({
        "message": f"Added part {part.part_name} (ID {part_id}) to service ticket {service_ticket_id}."
    }), 200
 


