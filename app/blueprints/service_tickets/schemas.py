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
        
        
class EditService_TicketSchema(ma.Schema):
    add_ids = fields.List(fields.Int(), required=True)
    remove_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_ids", "remove_ids")
        
class AddPartSchema(ma.Schema):
    part_id = fields.Int(required=True)
    class Meta:
        fields = ("part_id",)
    

service_ticket_schema = Service_TicketSchema()
service_tickets_schema = Service_TicketSchema(many=True)
return_service_ticket_schema = Service_TicketSchema()
edit_service_ticket_schema = EditService_TicketSchema()
add_part_schema = AddPartSchema()
