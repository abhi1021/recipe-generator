#!/usr/bin/env bash
# --------------------------------------------------
# recipes-genie deploy script
# --------------------------------------------------
set -euo pipefail
IFS=$'\n\t'

# -----------------------------
# 1. Configuration
# -----------------------------
AWS_REGION="eu-west-1"
LAMBDA_NAME="recipes-genie"
GOOGLE_API_KEY="recipes-genie"

# -----------------------------
# 2. Load secret from .env
# -----------------------------
if [[ ! -f .env ]]; then
  echo "❌ .env file not found. Abort."
  exit 1
fi

# Source .env safely – we only import the key we need
# Change the key name if your .env uses something else
export $(grep -E '^GOOGLE_API_KEY=' .env | xargs)

if [[ -z "${GOOGLE_API_KEY:-}" ]]; then
  echo "❌ .env does not contain GOOGLE_API_KEY. Abort."
  exit 1
fi

# -----------------------------
# 3. Create / Update Secret in Secrets Manager
# -----------------------------
echo "🔐 Creating/Updating secret '${GOOGLE_API_KEY}' in Secrets Manager..."
if aws secretsmanager describe-secret --region "$AWS_REGION" --secret-id "api-key" >/dev/null 2>&1; then
  aws secretsmanager update-secret \
    --region "$AWS_REGION" \
    --secret-id "api-key" \
    --secret-string "$GOOGLE_API_KEY" \
    > /dev/null
  echo "✅ Secret updated."
else
  aws secretsmanager create-secret \
    --region "$AWS_REGION" \
    --name "api-key" \
    --secret-string "$GOOGLE_API_KEY" \
    > /dev/null
  echo "✅ Secret created."
fi

# -----------------------------
# 4. Create IAM Role for Lambda
# -----------------------------
ROLE_NAME="${LAMBDA_NAME}-role"
TRUST_POLICY_FILE="trust_policy.json"
POLICY_FILE="lambda_secrets_policy.json"

cat > "$TRUST_POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

cat > "$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:$AWS_REGION:*:secret:api-key-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:$AWS_REGION:*:*"
    }
  ]
}
EOF

echo "🛠️ Creating IAM role '${ROLE_NAME}'..."
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo "✅ Role already exists – skipping creation."
else
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document "file://$TRUST_POLICY_FILE" \
    --description "Role for Lambda to access ${GOOGLE_API_KEY} secret" \
    > /dev/null
  echo "✅ Role created."
fi

# Attach the inline policy
echo "📎 Attaching policy to role..."
aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "LambdaSecretsPolicy" \
  --policy-document "file://$POLICY_FILE" \
  > /dev/null
echo "✅ Policy attached."

# Get the ARN for later use
ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)

# -----------------------------
# 5. Package Lambda source
# -----------------------------
ZIP_FILE="lambda.zip"

# If you already have a folder with your code, copy it into a temp dir.
# For demo purposes we create a very small Python handler if none exists.
#SRC_DIR="lambda_src"
#mkdir -p "$SRC_DIR"

# Create zip
#echo "📦 Packaging Lambda source..."
#rm -f "$ZIP_FILE"
#(cd "$SRC_DIR" && zip -r "../$ZIP_FILE" .)

# -----------------------------
# 6. Create / Update Lambda Function
# -----------------------------
echo "🚀 Deploying Lambda function '${LAMBDA_NAME}'..."
if aws lambda get-function --function-name "$LAMBDA_NAME" >/dev/null 2>&1; then
  # Update existing function
  aws lambda update-function-code \
    --function-name "$LAMBDA_NAME" \
    --zip-file "fileb://$ZIP_FILE" \
    > /dev/null
  aws lambda update-function-configuration \
    --function-name "$LAMBDA_NAME" \
    --role "$ROLE_ARN" \
    --environment Variables="{GOOGLE_API_KEY=${GOOGLE_API_KEY}}" \
    > /dev/null
  echo "✅ Lambda function updated."
else
  # Create new function
  aws lambda create-function \
    --function-name "$LAMBDA_NAME" \
    --runtime python3.12 \
    --role "$ROLE_ARN" \
    --handler lambda_handler.lambda_handler \
    --zip-file "fileb://$ZIP_FILE" \
    --description "recipes‑genie Lambda – reads secret from Secrets Manager" \
    > /dev/null
  echo "✅ Lambda function created."
#fi




# -----------------------------
# 7. Clean up temporary files
# -----------------------------
rm -f "$TRUST_POLICY_FILE" "$POLICY_FILE" "$ZIP_FILE"

echo "🎉 All done! Lambda '${LAMBDA_NAME}' is ready to go."

aws lambda create-function
--function-name recipes-genie
--runtime python3.12
--role arn:aws:iam::537907620791:role/recipes-genie-role
--handler lambda_function.lambda_handler
--zip-file "fileb://lambda.zip     --description "Recipe Genie Function"
