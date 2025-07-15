from flask import Flask, jsonify, Response
from flask_cors import CORS
import os
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_HOST'),
    aws_access_key_id=os.getenv('S3_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET')
)

def get_sto_file_from_s3(identifier):
    """
    Get .sto file from S3 bucket ebi-rnacentral/dev/alignments/
    """
    bucket_name = 'ebi-rnacentral'
    object_key = f'dev/alignments/{identifier.lower()}.sto'
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to retrieve {object_key} from S3: {str(e)}")

@app.route('/family/<identifier>', methods=['GET'])
def get_sequences(identifier):
    """
    Get Stockholm file content by identifier from S3
    URL pattern: /family/{identifier}
    Returns: Raw Stockholm file content as plain text
    """
    try:
        # Get .sto file content from S3
        sto_content = get_sto_file_from_s3(identifier)
        
        if not sto_content.strip():
            return jsonify({
                'status': 'error',
                'message': f'No content found for identifier {identifier}',
                'data': None
            }), 404
        
        # Return raw Stockholm content as plain text
        return Response(
            sto_content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'inline; filename="{identifier.lower()}.sto"'
            }
        )
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve Stockholm file for {identifier}: {str(e)}',
            'data': None
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with usage information"""
    return jsonify({
        'status': 'success',
        'message': 'RNA Sequence API',
        'data': {
            'endpoints': {
                'stockholm_file': '/family/{identifier}',
                'health': '/health'
            },
            'examples': {
                'stockholm_format': '/family/RF03116',
            },
            'description': 'API for RNA Stockholm alignment files - returns raw .sto file content'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'data': None
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'data': None
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)