# app.py
from app import create_app
from app.models import db
from flask import redirect

app = create_app('ProductionConfig')

# Redirect to documentation
@app.route('/', methods=['GET'])
def index():
    return redirect('/api/docs/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  

