from flask import Flask, request, jsonify, Response
import requests
import json
import os

app = Flask(__name__)

# Get Dify API Endpoint and Key from environment variables
DIFY_URL = os.getenv("DIFY_URL")
DIFY_KEY = os.getenv("DIFY_KEY")

# Function to extract user message from OpenAI format
def get_user_message(openai_messages):
    """
    Extracts the latest user message from OpenAI format messages.

    Args:
        openai_messages (list): List of messages in OpenAI format.

    Returns:
        str: The latest user message content.
    """
    for message in reversed(openai_messages):
        if message.get("role") == "user":
            return message.get("content", "")
    return ""

# Transform OpenAI request to Dify request
def transform_openai_to_dify(data):
    """
    Transforms OpenAI format request to Dify format.

    Args:
        data (dict): Request data in OpenAI format.

    Returns:
        dict: Transformed request data in Dify format.
    """
    user_message = get_user_message(data.get("messages", []))
    transformed_data = {
        "inputs": {"text": user_message},  # Assuming "text" is the input key for Dify
        "query": user_message,  # Adding the query parameter
        "response_mode": "streaming" if data.get("stream", False) else "blocking",
        "user": data.get("user", "default-user"),
        "conversation_id": data.get("conversation_id", None)
    }
    return transformed_data

# Transform Dify response to OpenAI response
def transform_dify_to_openai(data):
    """
    Transforms Dify format response to OpenAI format.

    Args:
        data (dict): Response data in Dify format.

    Returns:
        dict: Transformed response data in OpenAI format.
    """
    if "answer" in data:
        return {
            "choices": [
                {
                    "delta": {"content": data["answer"]},
                    "index": 0,
                    "finish_reason": None
                }
            ],
            "id": data.get("task_id", ""),
            "object": "chat.completion.chunk",
            "created": data.get("created_at", ""),
            "model": "dify",
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    else:
        return {
            "choices": [
                {
                    "delta": {},
                    "index": 0,
                    "finish_reason": "stop"
                }
            ],
            "id": data.get("task_id", ""),
            "object": "chat.completion.chunk",
            "created": data.get("created_at", ""),
            "model": "dify",
            "usage": data.get("metadata", {}).get("usage", {})
        }

@app.route('/v1/chat/completions', methods=['POST'])
def forward_to_dify():
    """
    Forwards OpenAI format requests to Dify API.

    Returns:
        flask.Response: Transformed response from Dify API in OpenAI format.
    """
    data = request.json
    app.logger.info(f"Received request: {data}")
    
    if "model" in data:
        del data["model"]  # Remove the model field if present

    dify_request_data = transform_openai_to_dify(data)
    app.logger.info(f"Transformed request to Dify format: {dify_request_data}")

    headers = {
        'Authorization': f'Bearer {DIFY_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post(DIFY_URL, headers=headers, data=json.dumps(dify_request_data), stream=True)

    if response.status_code != 200:
        app.logger.error(f"Dify API request failed with status code {response.status_code}: {response.text}")
        return jsonify({"error": "Dify API request failed", "status_code": response.status_code}), response.status_code

    def generate():
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8').replace("data: ", ""))
                openai_chunk = transform_dify_to_openai(chunk)
                yield f"data: {json.dumps(openai_chunk)}\n\n"

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
