from flask import Blueprint, request, jsonify, render_template
from app.models import Contact
from app.utils import validate_contact_data
from app import db, mail, get_rabbit_connection
from datetime import datetime
from flask_mail import Message
import pika, json, os

contact_bp = Blueprint('contacts', __name__)

@contact_bp.route('/contacts/<int:id>', methods=['GET'])
def get_one_contact(id):
    contact = Contact.query.get_or_404(id)
    return jsonify([contact.to_dict()])

@contact_bp.route('/contacts', methods=['GET'])
def get_contacts():
    search = request.args.get('search', '')
    query = Contact.query
    if search:
        query = query.filter(
            db.or_(
                Contact.first_name.contains(search),
                Contact.last_name.contains(search),
                Contact.email.contains(search),
                Contact.company.contains(search)
            )
        )
    contacts = query.all()
    return jsonify([c.to_dict() for c in contacts])

@contact_bp.route('/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    errors = validate_contact_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    if Contact.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    contact = Contact(**data)
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201

@contact_bp.route('/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    errors = validate_contact_data(data, is_update=True)
    if errors:
        return jsonify({'errors': errors}), 400
    for field in data:
        setattr(contact, field, data[field])
    contact.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(contact.to_dict())

@contact_bp.route('/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'})

@contact_bp.route('/contacts/<int:id>/send-mail', methods=['POST'])
def send_contact_mail(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()

    # TODO: Validate data
    errors = validate_contact_data(data)
    # if errors is empty
    if errors:
        return jsonify({'errors': errors}), 400
    
    topic = data.get("topic", "Hello")
    context = {
        "name": "Vinicius",
        "message": data.get("message", "")
    }
    connection_info = get_rabbit_connection()
    # print(f"ConnectionInfo:", connection_info, flush=True)

    connection = pika.BlockingConnection(connection_info)
    try:
        channel = connection.channel()
        channel.queue_declare(queue='email_queue')
        print("Publishing job...")
        channel.basic_publish(
            exchange='',
            routing_key='email_queue',
            body=json.dumps({
                "to": contact.email,
                "subject": topic,
                "context": context
            })
        )
        connection.close()
    
        return jsonify({'message': 'Mail sent successfully'})
    except Exception as e:
        print(f"Error sending email: {e}", flush=True)
        print(e)
        return jsonify({'status': 'error', 'error': f'Error reading file: {str(e)}'}), 500

def validate_contact_data(data, is_update=False):
    errors = []
    if not data.get('topic'):
        errors.append('topic is required')
    if not data.get('message'):
        errors.append('message is required')
    return errors