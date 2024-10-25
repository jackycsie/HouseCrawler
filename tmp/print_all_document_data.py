import pymongo
import sys
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# Get credentials from environment variables
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')

def print_all_documents(uri, database_name, collection_name):
    client = None
    try:
        # Establish the MongoDB connection
        client = pymongo.MongoClient(uri)
        db = client[database_name]
        collection = db[collection_name]

        # Fetch and print all documents in the collection
        all_documents = collection.find()
        for document in all_documents:
            for key, value in document.items():
                print(f"{key}: {value}")
            print("-" * 30)  # Adds a separator line to distinguish between documents
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the MongoDB client is closed properly
        if client:
            client.close()

# URI and collection details
docdb_uri = f'mongodb://{mongo_user}:{mongo_pass}@sinyicrawler.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/''?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
database = 'sinyi_buy_house'
collection = 'sinyi_house_info'

# Call the function to print all documents
print_all_documents(docdb_uri, database, collection)