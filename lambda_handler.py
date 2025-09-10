import json
import boto3
import os
from typing import Dict, Any
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    from werkzeug.middleware.proxy_fix import ProxyFix
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Configure app for Lambda
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

def get_secrets() -> Dict[str, str]:
    """Retrieve secrets from AWS Secrets Manager"""
    secrets_name = os.environ.get('SECRETS_NAME')
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    
    if not secrets_name:
        print("No SECRETS_NAME environment variable found")
        return {}
    
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        get_secret_value_response = client.get_secret_value(
            SecretId=secrets_name
        )
        
        secrets = json.loads(get_secret_value_response['SecretString'])
        return secrets
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        return {}

def setup_environment():
    """Setup environment variables from Secrets Manager"""
    secrets = get_secrets()
    
    # Set environment variables for the Flask app
    for key, value in secrets.items():
        if value:  # Only set non-empty values
            os.environ[key] = value

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for API Gateway HTTP API events"""
    
    # Setup environment on first invocation
    if not hasattr(lambda_handler, '_initialized'):
        setup_environment()
        lambda_handler._initialized = True
    
    try:
        # Handle different event formats
        if 'version' in event and event['version'] == '2.0':
            # HTTP API format
            http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
            path = event.get('rawPath', '/')
            query_string = event.get('rawQueryString', '')
            headers = event.get('headers', {})
            body = event.get('body', '')
            is_base64_encoded = event.get('isBase64Encoded', False)
        else:
            # REST API format (fallback)
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            query_string = event.get('queryStringParameters') or {}
            if isinstance(query_string, dict):
                query_string = '&'.join([f"{k}={v}" for k, v in query_string.items()])
            headers = event.get('headers', {})
            body = event.get('body', '')
            is_base64_encoded = event.get('isBase64Encoded', False)
        
        # Handle base64 encoded body
        if is_base64_encoded and body:
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': http_method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.input': StringIOWrapper(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
        }
        
        # Add headers to environ
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = f'HTTP_{key}'
            environ[key] = value
        
        # Capture response
        response_data = {}
        
        def start_response(status, headers, exc_info=None):
            response_data['status'] = status
            response_data['headers'] = dict(headers)
        
        # Call Flask app
        response_body = app.wsgi_app(environ, start_response)
        
        # Format response for API Gateway
        body_content = b''.join(response_body).decode('utf-8')
        status_code = int(response_data['status'].split()[0])
        
        return {
            'statusCode': status_code,
            'headers': response_data.get('headers', {}),
            'body': body_content,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'}),
            'isBase64Encoded': False
        }

class StringIOWrapper:
    """Wrapper to make string behave like file object for WSGI"""
    def __init__(self, content):
        self.content = content
        self.position = 0
    
    def read(self, size=-1):
        if size == -1:
            result = self.content[self.position:]
            self.position = len(self.content)
        else:
            result = self.content[self.position:self.position + size]
            self.position += len(result)
        return result.encode('utf-8')
    
    def readline(self, size=-1):
        newline_pos = self.content.find('\n', self.position)
        if newline_pos == -1:
            return self.read(size)
        else:
            end_pos = newline_pos + 1
            if size != -1:
                end_pos = min(end_pos, self.position + size)
            result = self.content[self.position:end_pos]
            self.position = end_pos
            return result.encode('utf-8')
    
    def readlines(self):
        lines = []
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines