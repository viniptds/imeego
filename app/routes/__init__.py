from flask import Blueprint

# Import individual route modules
from .contacts import contact_bp

# You can optionally group all blueprints here
__all__ = ["contact_bp"]