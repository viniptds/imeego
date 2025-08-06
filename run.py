from app import create_app, db

app = create_app()
first_request_processed = False

@app.before_request
def run_on_first_request():
    global first_request_processed
    if not first_request_processed:
        print("This runs only on the very first request!")
        # Perform your one-time setup here
        setup()
        first_request_processed = True

def setup():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)