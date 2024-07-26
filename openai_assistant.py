from openai import OpenAI
import os
client = OpenAI()

open_ai_key = os.getenv("OPENAI_API_KEY")
 
 
# Define Functions
assistant = client.beta.assistants.create(
  name="Coach V",
  instructions="You are a weather bot. Use the provided functions to answer questions. and you will also give answer to the user questoin based on the retrieved context about shot pulse sp and the setup instructions for shot pulse sp",
  model="gpt-4o-mini-2024-07-18",
  tools=[
    {"type": "file_search"},
    {
      "type": "function",
      "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["Celsius", "Fahrenheit"],
              "description": "The temperature unit to use. Infer this from the user's location."
            }
          },
          "required": ["location", "unit"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_rain_probability",
        "description": "Get the probability of rain for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
)


# Create a vector store caled "SP"
vector_store = client.beta.vector_stores.create(name="tool_test")

# Ready the files for upload to OpenAI
file_path = 'sp_data.txt'
file_streams = [open(file_path, "rb")]


# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)
print(vector_store.id)


#Update the assistant to to use the new Vector Store
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)



#Create a Thread and Add a message
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="What is sp",
)


#Initiate a Run
from typing_extensions import override
from openai import AssistantEventHandler
 
class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
      # Retrieve events that are denoted with 'requires_action'
      # since these will have our tool_calls
      if event.event == 'thread.run.requires_action':
        run_id = event.data.id  # Retrieve the run ID from the event data
        self.handle_requires_action(event.data, run_id)
 
    def handle_requires_action(self, data, run_id):
      tool_outputs = []
        
      for tool in data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name == "get_current_temperature":
          tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
        elif tool.function.name == "get_rain_probability":
          tool_outputs.append({"tool_call_id": tool.id, "output": "0.06"})
        
      # Submit all tool_outputs at the same time
      self.submit_tool_outputs(tool_outputs, run_id)
 
    def submit_tool_outputs(self, tool_outputs, run_id):
      # Use the submit_tool_outputs_stream helper
      with client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=self.current_run.id,
        tool_outputs=tool_outputs,
        event_handler=EventHandler(),
      ) as stream:
        for text in stream.text_deltas:
          print(text, end="", flush=True)
        print()
 
 
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id,
  event_handler=EventHandler()
) as stream:
  stream.until_done()
