from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential
import time

#credential = DefaultAzureCredential()


# ---- Credentials ----
tenant_id = ""
client_id = ""
client_secret = ""

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# ---- Project & Agent ----
CONNECTION_STRING = ""
AGENT_ID = ""

project_client = AIProjectClient(endpoint=CONNECTION_STRING, credential=credential)

# ---- Query function ----
def query_agent(user_input):
    agent = project_client.agents.get_agent(agent_id=AGENT_ID)

    # Create a thread
    thread = project_client.agents.threads.create()
    
    # Add user message
    project_client.agents.messages.create(thread_id=thread.id, role="user", content=user_input)
    
   # 9️⃣ Create and process an agent run
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
        additional_instructions="Please summarize the results concisely and cite sources."
    )
    print(f"Run finished with status: {run.status}")

    # 🔟 Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # 1️⃣1️⃣ Fetch and print all messages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    print("MESSAGES=========>",messages)
    for msg in messages:
        print(f"Role: {msg.role}, Content: {msg.content}")
    

# ---- Example ----
query_agent("Hi! Find me the latest news about AI in healthcare.")
