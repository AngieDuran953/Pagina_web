from google.cloud import storage
from google.auth import exceptions

try:
    storage_client = storage.Client.from_service_account_json("credentials.json")
    print("Storage access successful")
except exceptions.GoogleAuthError as e:
    print("Error:", e)