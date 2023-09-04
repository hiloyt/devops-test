import yaml
import argparse
import random
from pymongo import MongoClient
from faker import Faker

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("num_entries", type=int)
args = parser.parse_args()

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

# create or access the "transaction" collection
transaction_collection = client[mongo_database]["transaction"]

# create a Faker instance
fake = Faker()

# generate random data with Faker
def generate_random_transactions():
    card_type = fake.random_element(elements=("Visa", "Mastercard", "Amex", "Maestro", "Discover"))
    card_number = fake.credit_card_number(card_type=card_type.lower())

    # generate a random datetime within the last year and convert to unix ms
    date = int(
        fake.date_time_between(
            start_date="-1y", end_date="now", tzinfo=None
        ).timestamp()
        * 1000
    )

    transaction_document = {
        "_id": str(fake.uuid4()),
        "date": date,
        "currency": str(fake.currency_code()),
        "amount": round(random.uniform(1.0, 1000.0), 2),
        "vendor": str(fake.company()),
        "cardType": str(card_type),
        "cardNumber": str(card_number),
        "address": str(fake.address()),
        "countryOrigin": str(fake.country_code(representation="alpha-2")),
    }
    return transaction_document

# populate the collection
created_entries = 0
for _ in range(args.num_entries):
    random_transaction = generate_random_transactions()

    transaction_collection.insert_one(random_transaction)
    created_entries += 1

# End the connection
client.close()

# output how many entries have been created
print(
    f"{created_entries} entries were created."
)
