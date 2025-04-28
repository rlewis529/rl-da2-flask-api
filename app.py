from flask import Flask, jsonify
from models import db, Stock
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def home():
    return {"message": "Welcome to the Flask API!"}

@app.route("/stocks")
def get_stocks():
    stocks = Stock.query.all()
    return jsonify([{"symbol": s.symbol, "name": s.name} for s in stocks])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
