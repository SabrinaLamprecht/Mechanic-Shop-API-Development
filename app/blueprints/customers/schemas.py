# /app/blueprints/customers/schemas.py

from app.extensions import ma
from app.models import Customer

# Schemas
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer 

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)