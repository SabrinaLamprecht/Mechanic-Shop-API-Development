# /app/blueprints/service_tickets/routes.py

from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_Ticket, db
from . import service_tickets_bp
from app.models import Mechanic


# CREATE A NEW SERVICE TICKET
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

    # If mechanics were included in request, attach them
    mechanic_ids = service_ticket_data.get("mechanic_ids", [])
    if mechanic_ids:
        new_service_ticket.mechanics = (
            db.session.query(Mechanic)
            .filter(Mechanic.id.in_(mechanic_ids))
            .all()
        )
    
    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket), 201

# PUT Adds a relationship between a service ticket and the mechanics. 
@service_tickets_bp.route("/<int:service_ticket_id>/add_mechanic/<int:mechanic_id>", methods=['PUT'])
def assign_mechanic_to_service_ticket(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_Ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not service_ticket or not mechanic: 
        return jsonify({"message": "Invalid service ticket or mechanic ID."}), 400
    
    if mechanic in service_ticket.mechanics:
        return jsonify({"message": "Mechanic already in service ticket."}), 400
    
    service_ticket.mechanics.append(mechanic)
    db.session.commit()
    
    return jsonify({"message": f"Added mechanic {mechanic_id} to service ticket {service_ticket_id}."}), 200

# PUT Removes the relationship from the service ticket and the mechanic.
@service_tickets_bp.route("/<int:service_ticket_id>/remove_mechanic/<int:mechanic_id>", methods=['PUT'])
def remove_mechanic_from_service_ticket(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_Ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not service_ticket or not mechanic:
        return jsonify({"message": "Invalid service ticket or order ID."}), 400
    
    if mechanic not in service_ticket.mechanics:
        return jsonify({"message": "Mechanic not found in service ticket."}), 400
    
    service_ticket.mechanics.remove(mechanic)
    db.session.commit()
    
    return jsonify({"message": f"Removed mechanic {mechanic_id} from service ticket {service_ticket_id}."}), 200
        

# GET Retrieves all service tickets
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(Service_Ticket)
    service_tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_tickets), 200
