import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import BingGroundingTool
from azure.identity import ClientSecretCredential
from azure.core.credentials import AzureKeyCredential

# 1️⃣ Set environment variables (optional if using ClientSecretCredential directly)
#os.environ['AZURE_CLIENT_ID'] = ''

# 2️⃣ Azure AI Project endpoint
project_endpoint = ""

# 3️⃣ Authentication
tenant_id = ""
client_id = ''
client_secret = ""

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# project_client = AIProjectClient(
#     endpoint=project_endpoint,
#     credential=AzureKeyCredential("")
# )

# 4️⃣ Create AIProjectClient instance
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=credential,
)

# 5️⃣ ID of the already created agent
existing_agent_id = ""  # Replace with the actual agent ID

with project_client:
    # 6️⃣ Fetch the agent by ID
    agent = project_client.agents.get_agent(agent_id=existing_agent_id)
    print(f"Fetched agent: {agent.name}, ID: {agent.id}")

    # 7️⃣ Create a thread for conversation
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # 8️⃣ Add a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi! Find me the latest news about AI in healthcare.",
    )
    print(f"Created message, ID: {message['id']}")

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
    for msg in messages:
        print(f"Role: {msg.role}, Content: {msg.content}")
