from flask import Flask, jsonify, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.sto_parser import parse_stockholm_file
from utils.s3 import get_sto_file_from_s3

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/<identifier>', methods=['GET'])
def get_msa_data(identifier):
    """
    Get MSA data by identifier from S3, parsed and formatted for the MSA viewer.
    URL pattern: /{identifier}
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
                'consensus': msa_data['consensus'],
                'notation': msa_data.get('notation'),
                'sequences': msa_data.get('sequences')
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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)