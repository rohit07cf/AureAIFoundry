# from azure.ai.projects import AIProjectClient
# from azure.identity import ClientSecretCredential
# from azure.identity import DefaultAzureCredential
# import time
# #az login
# #az account show
# #az account list --output table
# #az account set --subscription ""
# #az resource list --name  --query "[].resourceGroup" -o tsv
# #credential = DefaultAzureCredential()


# # ---- Credentials ----
# tenant_id = ""
# client_id = ""
# client_secret = ""

# credential = ClientSecretCredential(
#     tenant_id=tenant_id,
#     client_id=client_id,
#     client_secret=client_secret
# )

# # ---- Project & Agent ----
# CONNECTION_STRING = ""
# AGENT_ID = ""

# project_client = AIProjectClient(endpoint=CONNECTION_STRING, credential=credential)

# # ---- Query function ----
# def query_agent(user_input):
#     agent = project_client.agents.get_agent(agent_id=AGENT_ID)

#     # Create a thread
#     thread = project_client.agents.threads.create()
    
#     # Add user message
#     project_client.agents.messages.create(thread_id=thread.id, role="user", content=user_input)
    
#    # 9️⃣ Create and process an agent run
#     run = project_client.agents.runs.create_and_process(
#         thread_id=thread.id,
#         agent_id=agent.id,
#         additional_instructions="Please summarize the results concisely and cite sources."
#     )
#     print(f"Run finished with status: {run.status}")

#     # 🔟 Check if the run failed
#     if run.status == "failed":
#         print(f"Run failed: {run.last_error}")

#     # 1️⃣1️⃣ Fetch and print all messages
#     messages = project_client.agents.messages.list(thread_id=thread.id)
#     #print("MESSAGES=========>",messages)
#     for msg in messages:
#         print(f"Content: {msg.content}")
    

# # ---- Example ----
# query_agent("Hi! Find me the latest news about AI in healthcare.")


import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import ClientSecretCredential

# ---- Credentials ----
TENANT_ID = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

# ---- Project & Agent ----
CONNECTION_STRING = ""
AGENT_ID = ""

# Limit concurrency (optional, production-safe)
SEMAPHORE_LIMIT = 20  # Adjust depending on backend capacity

async def query_agent(project_client, user_input, sem):
    async with sem:
        try:
            # Create a new thread
            thread = await project_client.agents.threads.create()

            # Add user message
            await project_client.agents.messages.create(thread_id=thread.id, role="user", content=user_input)

            # Run agent
            run = await project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=AGENT_ID,
                additional_instructions="Please summarize the results concisely and cite sources."
            )

            if run.status == "failed":
                print(f"[FAILED] Query: {user_input}, Error: {run.last_error}")
                return

            # Fetch messages
            messages = await project_client.agents.messages.list(thread_id=thread.id)
            
            print(f"\n[RESULT] Query: {user_input}")
            for msg in messages:
                print(f"- {msg.content}")
        
        except Exception as e:
            print(f"[ERROR] Query: {user_input}, Exception: {e}")


async def main():
    # Async credential and client (singleton)
    async with ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET) as credential:
        async with AIProjectClient(endpoint=CONNECTION_STRING, credential=credential) as client:

            semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

            # Simulate 100 concurrent user queries
            user_inputs = [f"User query #{i}: Latest AI news in healthcare" for i in range(1, 101)]

            # Fire-and-forget style: print results as they complete
            tasks = [asyncio.create_task(query_agent(client, ui, semaphore)) for ui in user_inputs]

            # Wait for all tasks to finish
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())



# import asyncio
# from azure.ai.projects.aio import AIProjectClient
# from azure.identity.aio import ClientSecretCredential
# import re
# import time

# # ---- Credentials ----
# TENANT_ID = ""
# CLIENT_ID = ""
# CLIENT_SECRET = ""

# # ---- Project & Agent ----
# CONNECTION_STRING = ""
# AGENT_ID = ""

# # ---- Adaptive concurrency settings ----
# MAX_CONCURRENT_REQUESTS = 50
# STEP = 5                  # Increase concurrency by this amount each round
# REQUESTS_PER_ROUND = 20   # Number of queries to send per concurrency level
# RETRY_DELAY_DEFAULT = 5   # seconds, default wait on rate-limit

# async def query_agent(project_client, user_input, sem):
#     async with sem:
#         attempt = 1
#         while True:
#             try:
#                 thread = await project_client.agents.threads.create()
#                 await project_client.agents.messages.create(
#                     thread_id=thread.id,
#                     role="user",
#                     content=user_input
#                 )

#                 run = await project_client.agents.runs.create_and_process(
#                     thread_id=thread.id,
#                     agent_id=AGENT_ID,
#                     additional_instructions="Please summarize the results concisely and cite sources."
#                 )

#                 if run.status == "failed":
#                     print(f"[FAILED] Attempt {attempt} - Query: {user_input}, Error: {run.last_error}")
#                     return

#                 messages = await project_client.agents.messages.list(thread_id=thread.id)
#                 print(f"\n[RESULT] Query: {user_input}")
#                 for msg in messages:
#                     print(f"- {msg.content}")
#                 return

#             except Exception as e:
#                 err_msg = str(e)
#                 retry_after = None
#                 if "rate_limit" in err_msg.lower() or "429" in err_msg:
#                     match = re.search(r"(\d+)\s*seconds", err_msg)
#                     retry_after = int(match.group(1)) if match else RETRY_DELAY_DEFAULT
#                     print(f"[RATE-LIMIT] Attempt {attempt} - Query: {user_input}, retrying in {retry_after}s...")
#                     await asyncio.sleep(retry_after)
#                     attempt += 1
#                     continue
#                 print(f"[ERROR] Attempt {attempt} - Query: {user_input}, Exception: {err_msg}")
#                 return

# async def run_round(project_client, concurrency, user_inputs):
#     semaphore = asyncio.Semaphore(concurrency)
#     tasks = [asyncio.create_task(query_agent(project_client, ui, semaphore)) for ui in user_inputs]
#     await asyncio.gather(*tasks)

# async def main():
#     async with ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET) as credential:
#         async with AIProjectClient(endpoint=CONNECTION_STRING, credential=credential) as client:
#             current_concurrency = STEP  # start small
#             total_queries_sent = 0

#             while current_concurrency <= MAX_CONCURRENT_REQUESTS:
#                 print(f"\n=== Running round with concurrency: {current_concurrency} ===")
#                 user_inputs = [
#                     f"User query #{i + total_queries_sent + 1}: Latest AI news in healthcare"
#                     for i in range(REQUESTS_PER_ROUND)
#                 ]

#                 await run_round(client, current_concurrency, user_inputs)
                
#                 total_queries_sent += REQUESTS_PER_ROUND
#                 current_concurrency += STEP
#                 await asyncio.sleep(1)  # small pause between rounds

# if __name__ == "__main__":
#     start_time = time.time()
#     asyncio.run(main())
#     print(f"\nAll queries completed in {time.time() - start_time:.2f} seconds")
