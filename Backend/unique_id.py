from pymongo import MongoClient

# Connect to your MongoDB database

client = MongoClient("mongodb://localhost:27017/")
db = client["steganography_db"]
collection = db["audio_fingerprints"]


def unique_id_generator():
# Find the document with the highest ID
    last_doc = collection.find_one({}, sort=[("unique_id", -1)])

    # If no document exists, start the ID from 1
    if last_doc:
        new_id = last_doc["unique_id"] + 1
    else:
        new_id = 1

    
    


    return new_id

    
