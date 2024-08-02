# from openai import OpenAI
# import requests
# import os
# import json


# openai_api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI()


# # Function to get all user competitions
# def get_all_user_competitions():
#     url = "http://74.208.220.213:8001/api/v1/all_users_competition/?page=1&status=0"
#     response = requests.get(url)
#     if response.status_code == 200:
#         #print(response.json())
#         return response.json()
#     else:
#         return {"error": "Failed to retrieve competitions"}

# # Initialize OpenAI client
# client = OpenAI()

# # Create the assistant with the defined function
# assistant = client.beta.assistants.create(
#     name = "Coach V Assistant",
#     instructions="You are a competition assistant. Use the provided function to answer questions about user competitions.",
#     model="gpt-4o-mini-2024-07-18",
#     tools=[
#         {"type": "file_search"},
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_all_user_competitions",
#                 "description": "Get all competitions for all users",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {}
#                 },
                
#             }
#         }
#     ]
# )


# # Retreive the Vector Store
# vector_store = client.beta.vector_stores.retrieve("vs_8HoAoxEzhK6EOVvXYCM7Fv5s")


# # Update the Assistant to use the vector store
# assistant = client.beta.assistants.update(
#   assistant_id=assistant.id,
#   tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
# )


# # Create a thread and add a user message
# thread = client.beta.threads.create()
# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="I want to get competitions for all users."
# )

# # Initiate a run and handle function calling
# run = client.beta.threads.runs.create_and_poll(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
# )

# # Check if the run requires action
# if run.status == 'requires_action':
#     tool_outputs = []
    
#     for tool in run.required_action.submit_tool_outputs.tool_calls:
#         if tool.function.name == "get_all_user_competitions":
#             competitions = get_all_user_competitions()
#             tool_outputs.append({
#                 "tool_call_id": tool.id,
#                 "output": json.dumps(competitions)
#             })

#     # Submit all tool outputs
#     if tool_outputs:
#         try:
#             run = client.beta.threads.runs.submit_tool_outputs_and_poll(
#                 thread_id=thread.id,
#                 run_id=run.id,
#                 tool_outputs=tool_outputs
#             )
#             print("Tool outputs submitted successfully.")
#         except Exception as e:
#             print("Failed to submit tool outputs:", e)
#     else:
#         print("No tool outputs to submit.")
# else:
#     print(run.status)

# # Print the final messages
# if run.status == 'completed':
#     messages = client.beta.threads.messages.list(
#         thread_id=thread.id
#     )
#     print(messages)
# else:
#     print(run.status)






import requests
from openai import OpenAI
import os
import json


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
        print(response.text, 'thisssssssssssssssssssssss')
        return {"error": "Failed to sign up user"}

# Initialize OpenAI client
client = OpenAI()

# Create the assistant with the defined functions
assistant = client.beta.assistants.create(
    instructions="You are a competition and signup assistant. Use the provided functions to answer questions about user competitions and to sign up users.",
    model="gpt-4o",
    tools=[
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

# Create a thread and add a user message
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I want to signup here are my details first name john last name harry email johnhlack@gmail.com password 1234h$h1234 and here is my filepah './sp_data.txt'."
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
        if tool.function.name == "get_all_user_competitions":
            competitions = get_all_user_competitions()
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(competitions)
            })
        elif tool.function.name == "signup_user":
            print(tool,"tolllllllllllllllllllllllllllllll")
            # Assume we have the required parameters, for example:
            str = tool.function.arguments
            # Parse JSON string into a dictionary
            data = json.loads(str)

            # Extract values
            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
            password = data["password"]
            file_path = data["file_path"]
            # first_name = "John"
            # last_name = "Doe"
            # email = "john.doe@example.com"
            # password = "securepa$ssword123"
            # file_path = "./sp_data.txt"  # Make sure this file exists
            
            signup_response = signup_user(first_name, last_name, email, password, file_path)
            print(signup_response, "got ittttttttttttttttttttttttttttttttttttttttt")
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(signup_response)
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
    print(run.status)

# Print the final messages
if run.status == 'completed':
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages)
else:
    print(run.status)
    
    

