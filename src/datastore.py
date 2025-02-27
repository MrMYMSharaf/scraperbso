import ibm_boto3
from ibm_botocore.client import Config, ClientError
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

# ✅ Get credentials from .env file
IBM_API_KEY_ID = os.getenv('IBM_COS_API_KEY_ID')
IBM_SERVICE_INSTANCE_ID = os.getenv('IBM_COS_SERVICE_INSTANCE_ID')
BUCKET_NAME = os.getenv('IBM_COS_BUCKET')  # Use env variable for bucket name
ENDPOINT_URL = "https://s3.us-south.cloud-object-storage.appdomain.cloud"

# ✅ Initialize COS client
cos_client = ibm_boto3.client(
    service_name='s3',
    ibm_api_key_id=IBM_API_KEY_ID,
    ibm_service_instance_id=IBM_SERVICE_INSTANCE_ID,
    config=Config(signature_version='oauth'),
    endpoint_url=ENDPOINT_URL
)

# ✅ Upload Function with Error Handling
def upload_to_cos(file_path, bucket_name, object_name):
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        print(f"📂 Uploading {file_path} to {bucket_name} as {object_name}...")

        cos_client.upload_file(file_path, bucket_name, object_name)

        print(f"✅ Successfully uploaded: {object_name} to {bucket_name}")
        return True

    except ClientError as e:
        print(f"❌ Upload failed: {e}")
        return False

# ✅ Example Usage
file_path = "C:/Users/sharafM/Desktop/BOC/01.Dashboard for App comment evaluation/backend/data/27-02-2025_06-43-BOC_Smart_Passbook_reviews.csv"
object_name = os.path.basename(file_path)  # Extract filename from path

upload_to_cos(file_path, BUCKET_NAME, object_name)
