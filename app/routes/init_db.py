# # app/routes/init_db.py

# from flask import Blueprint, jsonify
# from app.models import db

# init_bp = Blueprint('init_db', __name__)

# @init_bp.route('/init_db', methods=['POST'])
# def init_db():
#     """
#     Creates all database tables that are missing.
#     Run this once after deployment, then remove this route.
#     """
#     db.create_all()  # Creates all tables based on your models
#     return jsonify({"message": "✅ All tables created"}), 200