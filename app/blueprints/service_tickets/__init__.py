# /app/blueprints/service-tickets/__init__.py

from flask import Blueprint

service_tickets_bp = Blueprint("service_tickets_bp", __name__)

from . import routes