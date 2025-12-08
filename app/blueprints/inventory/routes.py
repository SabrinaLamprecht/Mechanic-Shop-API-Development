# /app/blueprints/inventory/routes.py

from .schemas import inventory_schema, inventory_create_schema, inventory_update_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp
from app.extensions import limiter, cache
from app.utils.util import token_required

# Create an inventory item ⚡ Tested!
@inventory_bp.route("/", methods=['POST'])
# Rate limit applied
@limiter.limit("15 per hour")
def create_inventory():
    print("Request JSON:", request.json)
    try:
        inventory_data = inventory_create_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    print("Loaded inventory data:", inventory_data)
    
    query = select(Inventory).where(Inventory.part_name == inventory_data['part_name'])
    existing_inventory = db.session.execute(query).scalars().all()
    
    if existing_inventory:
        return jsonify({"error": "Part name already associated with an inventory item."}), 400
    
    new_inventory = Inventory(**inventory_data)
    db.session.add(new_inventory)
    db.session.commit()
    
    result = inventory_schema.dump(new_inventory)  
    return jsonify(result), 201
 
# Get all inventory items ⚡ Tested!
@inventory_bp.route("/", methods=['GET'])
# Rate limit applied
@limiter.exempt
# Caching applied
@cache.cached(timeout=60)
# Pagination 
def get_all_inventory():
    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Inventory)
        inventory = db.paginate(query, page=page, per_page=per_page)
        return inventory_schema.dump(inventory.items, many=True), 200
    except:
        query = select(Inventory)
        inventory_list = db.session.execute(select(Inventory)).scalars().all()
        return jsonify(inventory_schema.dump(inventory_list, many=True)), 200

# Get a specific inventory item ⚡ Tested!
@inventory_bp.route("/<int:inventory_id>", methods=['GET'])
def get_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if inventory: 
        return inventory_schema.jsonify(inventory), 200
    return jsonify({"error": "Inventory not found."}), 404


# Update a specific inventory item ⚡ Tested!
@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
# Will need to first login as mechanic, get token, and pass token in Authorization section (as Bearer Token)
@token_required(required_type='mechanic')
# Rate limit applied
@limiter.limit('5 per hour')
def update_inventory(user_id, user_type, inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if not inventory: 
        return jsonify({"error": "Inventory not found."}), 404
    
    try: 
        inventory_data = inventory_update_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
        setattr(inventory, key, value)
        
    db.session.commit()
    return jsonify (inventory_update_schema.dump(inventory)), 201

# Delete a specific inventory  ⚡ Tested!
@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
# Will need to first login as mechanic, get token, and pass token in Authorization section (as Bearer Token)
@token_required(required_type='mechanic')
# Rate limit applied
@limiter.limit("5 per hour") 
def delete_inventory(user_id, user_type, inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if not inventory:
        return jsonify({"error": "Inventory not found."}), 404
    
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({"message": f'inventory id: {inventory_id}, successfully deleted.'}), 200

# Search for an inventory item based on part_name ⚡ Tested!
@inventory_bp.route("/search", methods=['GET'])
def search_by_part_name():
    part_name = request.args.get("part_name")
    
    query = select(Inventory).where(Inventory.part_name.like(f'%{part_name}%'))
    inventory = db.session.execute(query).scalars().first()
    
    return inventory_schema.jsonify(inventory)
    