from flask import Blueprint, jsonify

# Import individual route modules
from .contacts import contact_bp


main_bp = Blueprint('home', __name__)
@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "CRM API is running", "version": "1.0.0"})

# You can optionally group all blueprints here
__all__ = ["mail_bp", "contact_bp"]