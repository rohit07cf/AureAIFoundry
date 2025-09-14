import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import BingGroundingTool
from azure.identity import ClientSecretCredential

os.environ['AZURE_CLIENT_ID'] = ''

# 1️⃣ Set your Azure AI Project endpoint
project_endpoint = ""


tenant_id = ""
client_id = ''
client_secret = ""

ok=ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# 2️⃣ Create AIProjectClient instance
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=ok,
)


conn_id = ""  # Ensure the BING_CONNECTION_NAME environment variable is set

# Initialize the Bing Grounding tool
bing = BingGroundingTool(connection_id=conn_id)

with project_client:
    # 4️⃣ Create an agent using the Bing Search tool
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",                # Your deployed model
        name="BingSearchAgent",             # Name of your agent
        instructions="You assist with search queries politely.",  # Agent instructions
        tools=bing.definitions,  # Attach the Bing Grounding tool
    )
    print(f"Created agent, ID: {agent.id}")

    # 5️⃣ Create a thread for conversation
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # 6️⃣ Add a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi! Find me the latest news about AI in healthcare.",
    )
    print(f"Created message, ID: {message['id']}")

    # 7️⃣ Create and process an agent run
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
        additional_instructions="Please summarize the results concisely and cite sources."
    )
    print(f"Run finished with status: {run.status}")

    # 8️⃣ Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # 9️⃣ Fetch and print all messages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for msg in messages:
        print(f"Role: {msg.role}, Content: {msg.content}")

    # 1️⃣0️⃣ Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
