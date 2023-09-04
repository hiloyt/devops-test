import datetime
import yaml
import json
from pymongo import MongoClient
from bson import ObjectId
from flask import Flask, jsonify

app = Flask(__name__)

# MongoDB yaml input
with open("db_envs.yaml", "r") as config_file:
    mongo_yaml = yaml.safe_load(config_file)

mongo_host = mongo_yaml["mongo_host"]
mongo_port = mongo_yaml["mongo_port"]
mongo_username = mongo_yaml["mongo_username"]
mongo_password = mongo_yaml["mongo_password"]
mongo_database = mongo_yaml["mongo_database"]

# MongoDB auth url
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}"

# MongoDB connection
client = MongoClient(mongo_uri)
db = client.get_database()

# custom JSON encoder for Flask
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# query transactions based on date range
def query_transactions_by_date_range(start_date, end_date):
    query = {
        "date": {
            "$gte": start_date.timestamp() * 1000,
            "$lte": end_date.timestamp() * 1000,
        }
    }
    transactions = db.transaction.find(query)
    return [
        json.loads(json.dumps(transaction, cls=CustomJSONEncoder))
        for transaction in transactions
    ]


# Endpoint 1: Transactions made in the last n days, where n is provided by the requestor.
@app.route("/transactions/<int:days>", methods=["GET"])
def get_transactions_last_n_days(days):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    transactions = query_transactions_by_date_range(start_date, end_date)

    return jsonify(transactions)


# Endpoint 2: The number of transactions made in the last n days where CardType is xyz, where n and xyz are provided by the requestor.
@app.route("/transactions/<int:days>/card/<string:card_type>", methods=["GET"])
def get_transactions_count_last_n_days_card_type(days, card_type):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    transactions = query_transactions_by_date_range(start_date, end_date)
    count = sum(
        1 for transaction in transactions if transaction["cardType"] == card_type
    )

    return jsonify({"count": count})


# Endpoint 3: A list of all the transactions made in the last n days where the CountryOrigin is xyz, where n and xyz are provided by the requestor.
@app.route("/transactions/<int:days>/country/<string:country_origin>", methods=["GET"])
def get_transactions_last_n_days_country_origin(days, country_origin):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    transactions = query_transactions_by_date_range(start_date, end_date)
    filtered_transactions = [
        transaction
        for transaction in transactions
        if transaction["countryOrigin"] == country_origin
    ]

    return jsonify(filtered_transactions)


# Endpoint 4: A list of all transactions made in the last n days where the Amount is between abc and xyz, where n, abc and xyz are provided by the requestor.
@app.route("/transactions/<int:days>/amount/<float:min_amount>/<float:max_amount>", methods=["GET"])
def get_transactions_last_n_days_amount_range(days, min_amount, max_amount):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    transactions = query_transactions_by_date_range(start_date, end_date)
    filtered_transactions = [
        transaction
        for transaction in transactions
        if min_amount <= transaction["amount"] <= max_amount
    ]

    return jsonify(filtered_transactions)


if __name__ == "__main__":
    app.run(debug=True)