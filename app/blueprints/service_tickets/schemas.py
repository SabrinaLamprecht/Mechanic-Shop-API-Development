# /app/blueprints/service-tickets/schemas.py

from app.extensions import ma
from app.models import Service_Ticket
from marshmallow import fields

# Schemas
class Service_TicketSchema(ma.SQLAlchemyAutoSchema):
    mechanic_ids = fields.List(fields.Integer(), load_only=True)
    
    class Meta:
        model = Service_Ticket 
        load_instance = False
        include_fk = True 

service_ticket_schema = Service_TicketSchema()
service_tickets_schema = Service_TicketSchema(many=True)