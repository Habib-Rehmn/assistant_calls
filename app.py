import requests
from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Function to get all user competitions
def get_all_user_competitions():
    url = "http://74.208.220.213:8001/api/v1/all_users_competition/?page=1&status=0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve competitions"}

# Function to sign up a user with all fields as form data
def signup_user(first_name, last_name, email, password, file_path):
    url = "http://74.208.220.213:8001/api/v1/signup/"
    files = {
        'upload_credentials': open(file_path, 'rb'),
        'first_name': (None, first_name),
        'last_name': (None, last_name),
        'email': (None, email),
        'password': (None, password)
    }
    response = requests.post(url, files=files)
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": "Failed to sign up user"}

# Route for the chat interface
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # Create the assistant with the defined functions
        assistant = client.beta.assistants.create(
            instructions="You are a competition and signup assistant. Use the provided functions to answer questions about user competitions and to sign up users. and you will also give answer to the user question about shot pulse sp, using the file provided",
            model="gpt-4o",
            tools=[{"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "get_all_user_competitions",
                        "description": "Get all competitions for all users",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "signup_user",
                        "description": "Sign up a new user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "first_name": {
                                    "type": "string",
                                    "description": "First name of the user"
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "Last name of the user"
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Email of the user"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Password for the account"
                                },
                                "file_path": {
                                    "type": "string",
                                    "description": "Path to the file to be uploaded"
                                }
                            },
                            "required": ["first_name", "last_name", "email", "password", "file_path"]
                        }
                    }
                }
            ]
        )
        
        # Reteive the Vector Store
        vector_store = client.beta.vector_stores.retrieve("vs_9uYldVoicTMRvBvma5vw8Lch")
        

        # Update the knowledge base of the assistant 
        assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        # Create a thread and add a user message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Initiate a run and handle function calling
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        
        

        # Check if the run requires action
        if run.status == 'requires_action':
            tool_outputs = []
            
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "signup_user":
                    data = json.loads(tool.function.arguments)
                    
                    # Store data in session and redirect to verification form
                    session['signup_data'] = data

                    # Show the extracted parameters to the use and
                    # Get the updated or verified parameters from the user
                    
                    data = session.get('signup_data', {})
                    
                    # Call the API with verified parameters
                    if request.method == 'POST':
                        first_name = request.form['first_name']
                        last_name = request.form['last_name']
                        email = request.form['email']
                        password = request.form['password']
                        file_path = request.form['file_path']

                        signup_response = signup_user(first_name, last_name, email, password, file_path)
        
                    # Append the data to the tool_outputs
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": json.dumps(competitions)
                    })
                    
                    #return redirect(url_for('verify_signup'))
                
                elif tool.function.name == "get_all_user_competitions":
                    competitions = get_all_user_competitions()
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": json.dumps(competitions)
                    })

            # Submit all tool outputs
            if tool_outputs:
                try:
                    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    print("Tool outputs submitted successfully.")
                except Exception as e:
                    print("Failed to submit tool outputs:", e)
            else:
                print("No tool outputs to submit.")
        else:
            # Print the final messages
            if run.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                print(messages)
            else:
                print(run.status)
        
    return render_template('index.html', response=signup_response)

# @app.route('/verify_signup', methods=['GET', 'POST'])
# def verify_signup():
#     print("we got till hereeeeeeeeeeeeeeeeeeeeeeee")
#     if request.method == 'POST':
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         email = request.form['email']
#         password = request.form['password']
#         file_path = request.form['file_path']

#         signup_response = signup_user(first_name, last_name, email, password, file_path)
        
#         ##Convert the signup response back to json string
        
        
#         run = client.beta.threads.runs.retrieve(
#         thread_id="thread_abc123",
#         run_id="run_abc123"
#         )
#         #Append the signup response to tool output
#         tool_outputs.append({
#             "tool_call_id": tool.id,
#             "output": json.dumps(signup_response)
#         })
        
#         #Submitt the final tool output

#         return render_template('result.html', response=signup_response)

#     data = session.get('signup_data', {})
#     return render_template('verify_signup.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
