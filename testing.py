from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def proxy_password():
    target_url = 'https://ptu-ctf.s3.ap-southeast-1.amazonaws.com/password.txt'
    try:
        # Fetch the resource from the target URL
        response = requests.get(target_url)
        response.raise_for_status()  # Raise an error for HTTP error responses

        # Return the fetched content to the client
        return Response(response.text, content_type='text/plain')
    except requests.exceptions.RequestException as e:
        # Handle errors
        return Response(f"Error fetching the resource: {e}", status=500)

if __name__ == '__main__':
    # Run the Flask app on localhost:3000
    app.run(host='0.0.0.0', port=8000)
