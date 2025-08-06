import re

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def validate_contact_data(data, is_update=False):
    errors = []
    if not is_update or 'first_name' in data:
        if not data.get('first_name', '').strip():
            errors.append('First name is required')
    if not is_update or 'last_name' in data:
        if not data.get('last_name', '').strip():
            errors.append('Last name is required')
    if not is_update or 'email' in data:
        email = data.get('email', '').strip()
        if not email:
            errors.append('Email is required')
        elif not validate_email(email):
            errors.append('Invalid email format')
    return errors