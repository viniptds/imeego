from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import pika, json, os, ssl
import traceback

mail = Mail()
db = SQLAlchemy()
load_dotenv()

def create_app():

    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://user:pass@localhost/crm_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    
    app.config.update(
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.example.com"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
    )

    mail.init_app(app)
    db.init_app(app)

    from app.routes import contact_bp,main_bp
    app.register_blueprint(contact_bp)
    app.register_blueprint(main_bp)

    return app

def get_rabbit_connection():

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_USE_SSL = os.getenv("RABBITMQ_USE_SSL", "false").lower() == "true"

    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

    if RABBITMQ_USE_SSL:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ssl_options = pika.SSLOptions(context, RABBITMQ_HOST)
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials,
            ssl_options=ssl_options
        )
    else:
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials,
        )  
    return connection_params