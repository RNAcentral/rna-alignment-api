from flask import Flask, jsonify
from flask_cors import CORS
import os
from sto_parser import parse_stockholm_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample data - you can replace this with your actual data source
sto_file = 'rf03116.sto'
sequence_data = parse_stockholm_file(sto_file)

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
                'source': f'Stockholm file: {sto_file}',
                'count': len(sequences),
                'identifier': identifier
            }
        },
        'message': 'Data loaded successfully'
    }

@app.route('/family/<identifier>', methods=['GET'])
def get_sequences(identifier):
    """
    Get sequences by identifier
    URL pattern: /family/{identifier}
    Returns: JSON in MSA component expected format
    """
    try:
        if not sequence_data:
            return jsonify({
                'status': 'error',
                'message': 'No sequence data available',
                'data': None
            }), 404
        
        # Format the response for the MSA component
        response = format_msa_response(sequence_data, identifier)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve sequences: {str(e)}',
            'data': None
        }), 500

@app.route('/family/<identifier>/raw', methods=['GET'])
def get_sequences_raw(identifier):
    """
    Get sequences in raw format (original behavior)
    URL pattern: /family/{identifier}/raw
    Returns: JSON array of sequence objects
    """
    return jsonify(sequence_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'data': {
            'service': 'RNA Sequence API',
            'version': '1.0.0',
            'sequences_loaded': len(sequence_data) if sequence_data else 0
        }
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
                'raw_sequences': '/family/{identifier}/raw',
                'health': '/health'
            },
            'examples': {
                'msa_format': '/family/RF03116',
                'raw_format': '/family/RF03116/raw'
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
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting RNA Sequence API on port {port}")
    print(f"MSA format: http://localhost:{port}/family/RF03116")
    print(f"Raw format: http://localhost:{port}/family/RF03116/raw")
    print(f"Health check: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)