from flask import Flask, jsonify, Response
from flask_cors import CORS
import os
import boto3
from dotenv import load_dotenv
from utils.sto_parser import parse_stockholm_file

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
def get_msa_data(identifier):
    """
    Get MSA data by identifier from S3, parsed and formatted for the MSA viewer.
    URL pattern: /family/{identifier}
    Returns: JSON data structure ready for MSA viewer consumption
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
        
        # Parse Stockholm content and format for MSA viewer
        msa_data = parse_stockholm_file(sto_content)
        
        # Add metadata
        response_data = {
            'status': 'success',
            'message': f'MSA data retrieved successfully for {identifier}',
            'data': {
                'identifier': identifier,
                'sequences': msa_data['sequences'],
                'reference': msa_data.get('reference'),
                'secondaryStructure': msa_data.get('secondaryStructure'),
                'metadata': {
                    'sequenceCount': len(msa_data['sequences']),
                    'sequenceLength': len(msa_data['sequences'][0]['sequence']) if msa_data['sequences'] else 0,
                    'hasReference': bool(msa_data.get('reference')),
                    'hasSecondaryStructure': bool(msa_data.get('secondaryStructure'))
                }
            }
        }
        
        return jsonify(response_data)
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid Stockholm format for {identifier}: {str(e)}',
            'data': None
        }), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve and parse Stockholm file for {identifier}: {str(e)}',
            'data': None
        }), 500

@app.route('/family/<identifier>/raw', methods=['GET'])
def get_raw_stockholm(identifier):
    """
    Get raw Stockholm file content by identifier from S3.
    URL pattern: /family/{identifier}/raw
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
        'message': 'API is running',
        'data': {
            'version': '2.0',
            'features': ['stockholm_parsing', 'secondary_structure', 'base_pairs']
        }
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with usage information"""
    return jsonify({
        'status': 'success',
        'message': 'RNA Multiple Sequence Alignment API v2.0',
        'data': {
            'endpoints': {
                'msa_data': '/family/{identifier}',
                'raw_stockholm': '/family/{identifier}/raw',
                'health': '/health'
            },
            'examples': {
                'parsed_msa_data': '/family/RF03116',
                'raw_stockholm_file': '/family/RF03116/raw'
            },
            'description': 'API for RNA Stockholm alignment files - returns parsed MSA data or raw .sto content',
            'data_format': {
                'sequences': 'Array of {name, sequence} objects',
                'reference': 'Reference sequence string (if available)',
                'secondaryStructure': 'Object with consensus and basePairs (if available)'
            }
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
    app.run(host='0.0.0.0', port=port, debug=True)