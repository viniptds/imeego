import pika
import json
import sys
import time
import traceback
from flask import render_template
from flask_mail import Message
from app import create_app, mail

app = create_app()

def send_email(data):
    print(f"Sending email to {data['to']}")
    # sys.stdout.flush()  # ensure logs show up in Docker immediately
    try:
        with app.app_context():
            print("[DEBUG] Inside app context ✅", flush=True)
            msg = Message(
                subject=data.get('subject', 'No Subject'),
                recipients=[data['to']],
            )
            msg.html = render_template('email.html', **data['context'])
            mail.send(msg)
            print(f"Sent email to {data['to']}", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}", flush=True)
        traceback.print_exc()  # full stack trace

def callback(ch, method, properties, body):
    print("Received task:", body)
    data = json.loads(body)
    send_email(data)

def consume():
    while True:  # Auto-reconnect loop
        try:
            print('Start consuming queue...')
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            
            channel.queue_declare(queue='email_queue')

            channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=True)
            print('[*] Waiting for email tasks...')

            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"⚠️ Lost connection to RabbitMQ: {e}. Retrying in 5s...", flush=True)
            time.sleep(5)


if __name__ == '__main__':
    consume()