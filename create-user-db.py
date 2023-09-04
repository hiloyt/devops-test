import yaml
from pymongo import MongoClient

# MongoDB yaml input
with open("db_envs.yaml", "r") as config_file:
    mongo_yaml = yaml.safe_load(config_file)

mongo_host = mongo_yaml["mongo_host"]
mongo_port = mongo_yaml["mongo_port"]
mongo_username = mongo_yaml["mongo_username"]
mongo_password = mongo_yaml["mongo_password"]
mongo_database = mongo_yaml["mongo_database"]

try:
    # MongoDB connection
    admin_client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/admin")

    # check if the db exists
    if mongo_database in admin_client.list_database_names():
        print(f"Database '{mongo_database}' already exists.")
    else:
        # create the new database without the collection
        admin_client[mongo_database].command({"create": mongo_database})
        print(f"Database '{mongo_database}' created successfully.")

        # create the admin user for this db
        admin_client[mongo_database].command(
            "createUser",
            mongo_username,
            pwd=mongo_password,
            roles=[
                {"role": "dbAdmin", "db": mongo_database},
                {"role": "readWrite", "db": mongo_database},
            ],
        )
        print(
            f"Admin user '{mongo_username}' created and granted access to '{mongo_database}'."
        )

except Exception as e:
    print(f"Error: {e}")

finally:
    # close connection
    admin_client.close()