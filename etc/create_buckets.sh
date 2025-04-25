#!/bin/bash

# Add host "myminio" to mc 
bash -c "until (mc config host add myminio ${MINIO_S3_ENDPOINT_URL} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}) do echo '...waiting...' && sleep 1; done;"

# Create buckets if not exist
mc mb --ignore-existing myminio/${AWS_STORAGE_BUCKET_NAME};
# Set bucket policy to public
mc anonymous set download myminio/${AWS_STORAGE_BUCKET_NAME};
# Create user
mc admin user add myminio ${MINIO_USER_ACCESS_KEY} ${MINIO_USER_SECRET_KEY};
mc admin policy attach myminio readwrite --user ${MINIO_USER_ACCESS_KEY};