import argparse
import boto3, botocore
import os, sys


def validate_mfa_code(value):
    if len(value) != 6:
        raise argparse.ArgumentTypeError("MFA Code must be exactly 6 characters long")
    if not value.isdigit():
        raise argparse.ArgumentTypeError("MFA Code must contain only digits")
    return str(value)


def insert_mfa_profile(access_key, secret_key, session_token):
    aws_credentials_path = os.path.expanduser("~/.aws/credentials")

    # If the credentials file doesn't exist, create it with a default profile
    if not os.path.exists(aws_credentials_path):
        os.makedirs(os.path.dirname(aws_credentials_path), exist_ok=True)
        with open(aws_credentials_path, "w") as f:
            f.write("[default]\n")

    # Read the existing credentials file
    with open(aws_credentials_path, "r") as f:
        lines = f.readlines()

    # Update the AWS access key ID, secret access key, and session token for the "mfa" profile
    start_index = None
    for i, line in enumerate(lines):
        if line.startswith("[mfa]"):
            start_index = i
            break
    if start_index is None:
        # If the "mfa" profile doesn't exist, create it
        start_index = len(lines)
        lines.append("\n[mfa]\n")

    for i in range(start_index + 1, len(lines)):
        if lines[i].startswith("["):
            end_index = i - 1
            break
    else:
        end_index = len(lines) - 1

    lines[start_index + 1 : end_index + 1] = [
        f"aws_access_key_id = {access_key}\n",
        f"aws_secret_access_key = {secret_key}\n",
        f"aws_session_token = {session_token}\n",
    ]

    # Write the updated credentials file
    with open(aws_credentials_path, "w") as f:
        f.writelines(lines)


parser = argparse.ArgumentParser(description="Provide your MFA Code")
parser.add_argument("mfa_code", type=validate_mfa_code)
args = parser.parse_args()


mfa_code = args.mfa_code
mfa_serial_file = os.path.expanduser("~/.mfa_identifier.txt")

# Read mfa serial number from a file
try:
    with open(mfa_serial_file, "r") as f:
        mfa_serial = f.read().strip()
except FileNotFoundError as e:
    missing_file_statement = """
    Your .mfa_identifier.txt file is missing from you home directory.
    Create a file in your home directory called .mfa_identifier.txt.
    Place your AWS MFA Identifier as the first line of that file.
    """
    print(missing_file_statement)
    sys.exit()

# Set up AWS session
session = boto3.Session(profile_name="default")
sts_client = session.client("sts")

try:
    response = sts_client.get_session_token(SerialNumber=mfa_serial, TokenCode=mfa_code)
except botocore.exceptions.ClientError as e:
    print(str(e).partition(": ")[2])
    sys.exit()

# Extract the session token and credentials from the response
access_key = response["Credentials"]["AccessKeyId"]
secret_key = response["Credentials"]["SecretAccessKey"]
session_token = response["Credentials"]["SessionToken"]

# Set the environment variables
# os.environ["AWS_ACCESS_KEY_ID"] = access_key
# os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
# os.environ["AWS_SESSION_TOKEN"] = session_token


insert_mfa_profile(access_key, secret_key, session_token)

print("\nAll set: Remember to add '--profile mfa' to the end of your aws statements.\n")
