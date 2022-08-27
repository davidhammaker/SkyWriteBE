#!/usr/bin/env python

import boto3

resource = boto3.resource(
    "s3",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    endpoint_url="http://localhost:9444",
)

# print(list(resource.buckets.all()))

# resource.Bucket("sky-write-bucket").put_object(Key="other/new_test.txt", Body=b"new data")
new_key = resource.Bucket("sky-write-bucket").new_key("test_folder/new_dir/")
new_key.set_contents_from_string("")
