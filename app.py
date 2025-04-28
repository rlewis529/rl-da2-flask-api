from flask import Flask, jsonify, request
from models import db, Stock
from config import Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def home():
    return {"message": "Welcome to the Flask API!"}

@app.route("/stocks")
def get_stocks():
    stocks = Stock.query.all()    
    return jsonify([{"symbol": s.symbol, "name": s.name} for s in stocks])

@app.route("/add-stock", methods=["POST"])
def add_stock():
    data = request.get_json()
    if not data or not 'symbol' in data or not 'name' in data:
        return {"error": "Invalid request data"}, 400

    new_stock = Stock(
        symbol=data['symbol'],
        name=data['name']
    )
    db.session.add(new_stock)
    db.session.commit()
    return {"message": f"Stock {new_stock.symbol} added successfully!"}, 201

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
