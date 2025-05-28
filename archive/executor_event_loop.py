import asyncio
import time
import httpx 

def fetch_sync_data(url):
    """A synchronous function that makes a blocking network request."""
    print(f"[{time.time():.2f}] Starting blocking fetch for {url}...")
    response = httpx.get(url)
    print(f"[{time.time():.2f}] Finished blocking fetch for {url}.")
    return response.status_code

async def main():
    loop = asyncio.get_running_loop() # Modern way to get the loop

    print(f"[{time.time():.2f}] Main: Starting main coroutine.")

    # Schedule a non-blocking task that runs concurrently
    async def non_blocking_task():
        for i in range(3):
            print(f"[{time.time():.2f}] Non-blocking task running... {i}")
            await asyncio.sleep(0.5) # Simulate async I/O
        print(f"[{time.time():.2f}] Non-blocking task finished.")

    task_non_blocking = asyncio.create_task(non_blocking_task())

    # Schedule the blocking operation to run in the executor
    # This will run in a separate thread from the event loop
    url1 = "https://www.google.com"
    url2 = "https://www.example.com"

    status_code_future1 = loop.run_in_executor(None, fetch_sync_data, url1)
    status_code_future2 = loop.run_in_executor(None, fetch_sync_data, url2)

    print(f"[{time.time():.2f}] Main: Blocking tasks submitted to executor. Loop is free.")

    # Await the results from the executor tasks
    status1 = await status_code_future1
    status2 = await status_code_future2

    print(f"[{time.time():.2f}] Main: Received status from {url1}: {status1}")
    print(f"[{time.time():.2f}] Main: Received status from {url2}: {status2}")

    await task_non_blocking # Ensure the non-blocking task completes

    print(f"[{time.time():.2f}] Main: All tasks completed.")

if __name__ == "__main__":
    asyncio.run(main())