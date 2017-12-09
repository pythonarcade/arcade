rem This is a batch file used to sync the documentation for arcade.academy to
rem the bucket it is hosted on. Doesn't do much good if you don't have
rem the credentials.
aws s3 sync doc/build/html s3://craven-arcade