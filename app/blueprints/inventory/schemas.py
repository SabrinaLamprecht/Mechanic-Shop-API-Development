# /app/blueprints/inventory/schemas.py

from app.extensions import ma
from app.models import Inventory, ServiceTicketInventory
from marshmallow import fields

# Schemas
class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True
        include_fk = True   # <--- important, includes foreign keys
        fields = ("id", "part_name", "price", "service_ticket_inventory")  
    service_ticket_inventory = fields.Nested("ServiceTicketInventorySchema", exclude=['id'], many=True)
    
    
    
class InventoryCreateSchema(ma.Schema):
    part_name = fields.Str(required=True)
    price = fields.Float(required=True)
    
class InventoryUpdateSchema(ma.Schema):
    part_name = fields.Str()
    price = fields.Float()
        
class InventoryQuantitySchema(ma.Schema):
    part_id = fields.Int(required=True)
    part_quantity = fields.Int(required=True)   
    
class ServiceTicketInventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicketInventory
        include_fk = True
        load_instance = True

inventory_schema = InventorySchema()
inventory_create_schema = InventoryCreateSchema()
inventory_update_schema = InventoryUpdateSchema()

