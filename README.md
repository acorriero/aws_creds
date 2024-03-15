# AWS MFA Session Helper

## Description

This tool simplifies the process of setting up a new AWS CLI session when an MFA token is required.

- Creates an STS request using your existing Access Key credentials.
- Creates and retrieves a temporary Access Key, KeyId, and Session Token
- Sets up an AWS credentials profile called MFA for you to use with your API calls.

## Setup Environment
- Create a file in your home directory called .mfa_identifier.txt
- Example: 
    - C:\Users\\<username\>\.mfa_identifier.txt
    - Make sure the file starts with a "."
- Place your AWS MFA Identifier as the first line of that file.
- Example: 
    - ![Example Identifier][sc-ident]

[sc-ident]: ./images/mfa_identifier.png

## Usage
- With python: `python3 aws_creds.py <mfa code>`
- Example:
    - ![Example Screenshot][sc-example]

[sc-example]: ./images/example_screenshot.png
