import pymongo
import sys
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# Get credentials from environment variables
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')

# Create a MongoDB client
client = pymongo.MongoClient(
    f'mongodb://{mongo_user}:{mongo_pass}@sinyicrawler.cluster-c3f5m2eagzla.ap-northeast-1.docdb.amazonaws.com:27017/'
    '?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
)

# Specify the database to be used
db = client.sample_database

# Specify the collection to be used
col = db.sample_collection

# Insert a single document
col.insert_one({'hello':'Amazon DocumentDB'})

# Find the document that was previously written
x = col.find_one({'hello':'Amazon DocumentDB'})

# Print the result to the screen
print(x)

# Close the connection
client.close()