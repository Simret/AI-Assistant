from app.lib.auth import token_required
from flask import Blueprint, request, current_app, jsonify
from dotenv import load_dotenv
import traceback
import json

load_dotenv()
main_bp = Blueprint('main', __name__)

@main_bp.route('/query', methods=['POST'])
@token_required
def process_query(current_user_id, auth_token):
    """
    Notes:
    - `query`: Contains the user's question or prompt.
    - `file`: Used when a file (e.g., a PDF) is uploaded for processing.
    - `id`: Represents a graph ID and should be included if relevant to the query.(when Explaining a node is asked from a given graph)
    - `resource`: Identifies the type of resource associated with the `id`. Currently not in use but it may support other types (e.g., "Hypothesis") in the future.
    """

    try:
        ai_assistant = current_app.config['ai_assistant']
    
        if not request.form and 'file' not in request.files:
            return jsonify({
                "error": "Invalid request format.",
                "message": "No form data found in the request. Please provide the required fields."
            }), 400
            

        data = request.form
        query = data.get('query', None)
        context = json.loads(data.get('context', '{}'))  
        context_id = context.get('id', None)
        resource = context.get('resource', None)
        graph = data.get('graph',None)
        
        # Handle file upload
        file = None
        if 'file' in request.files:
            file = request.files['file']            
            # Check if the file has no value (no PDF attached)
            if not file or file.filename == '':
                return jsonify({
                    "error": "No file provided.",
                    "message": "The 'file' key is empty. Please attach a valid PDF file."
                }), 400

        if query and 'file' not in request.files:
            return jsonify({
                "error": "Missing input.",
                "message": "Please attach a PDF file."
            }), 400
               
        response = ai_assistant.assistant_response(
            query=query,
            file=file,
            user_id=current_user_id,
            token=auth_token,
            graph_id=context_id,
            graph=graph)
        return response

    except Exception as e:
        traceback.print_exc()
        return f"Bad Response: {e}", 400

 