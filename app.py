from flask import Flask, jsonify
from flask_cors import CORS
import os
from utils.sto_parser import parse_stockholm_file
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

def format_msa_response(sequences, identifier):
    """
    Format sequences into the expected MSA component format
    """
    return {
        'status': 'success',
        'data': {
            'sequences': sequences,
            'metadata': {
                'title': f'{identifier} RNA Family',
                'description': f'Multiple sequence alignment for RNA family {identifier}',
                'source': f'S3: ebi-rnacentral/dev/alignments/{identifier.lower()}.sto',
                'count': len(sequences),
                'identifier': identifier
            }
        },
        'message': 'Data loaded successfully'
    }

@app.route('/family/<identifier>', methods=['GET'])
def get_sequences(identifier):
    """
    Get sequences by identifier from S3 .sto file
    URL pattern: /family/{identifier}
    Returns: JSON in MSA component expected format
    """
    try:
        # Get .sto file content from S3
        sto_content = get_sto_file_from_s3(identifier)
        
        # Parse the Stockholm file content
        sequence_data = parse_stockholm_file(sto_content)
        
        if not sequence_data:
            return jsonify({
                'status': 'error',
                'message': f'No sequence data found for identifier {identifier}',
                'data': None
            }), 404
        
        # Format the response for the MSA component
        response = format_msa_response(sequence_data, identifier)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve sequences for {identifier}: {str(e)}',
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
                'sequences': '/family/{identifier}',
                'health': '/health'
            },
            'examples': {
                'msa_format': '/family/RF03116',
            },
            'description': 'API for RNA multiple sequence alignment data'
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