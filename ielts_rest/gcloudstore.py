# from google.cloud import storage


# def batch_request(bucket_name, prefix=None):
#     """Use a batch request to patch a list of objects with the given prefix in a bucket."""
#     # The ID of your GCS bucket
#     bucket_name = "ielts-capstone"
#     # The prefix of the object paths
#     prefix = "ielts-capstone/"

#     client = storage.Client()
#     bucket = client.bucket(bucket_name)

#     # Accumulate in a list the objects with a given prefix.
#     blobs_to_patch = [blob for blob in bucket.list_blobs(prefix=prefix)]

#     # Use a batch context manager to edit metadata in the list of blobs.
#     # The batch request is sent out when the context manager closes.
#     # No more than 100 calls should be included in a single batch request.
#     with client.batch():
#         for blob in blobs_to_patch:
#             metadata = {"your-metadata-key": "your-metadata-value"}
#             blob.metadata = metadata
#             blob.patch()

#     print(
#         f"Batch request edited metadata for all objects with the given prefix in {bucket.name}."
#     )

# Imports the Google Cloud client library
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "my-new-bucket"

# Creates the new bucket
bucket = storage_client.create_bucket(bucket_name)

print(f"Bucket {bucket.name} created.")