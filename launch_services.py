import subprocess
import psutil
import time
import signal
import sys
import os

# Store process references
processes = []

def start_service(name, command):
    print(f"Starting {name}...")
    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    processes.append((name, process))
    print(f"{name} started with PID {process.pid}")

def stop_services():
    print("\nStopping all services...")
    for name, process in processes:
        print(f"Stopping {name} (PID {process.pid})...")
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):  # terminate child processes if any
                child.terminate()
            parent.terminate()
            print(f"{name} stopped.")
        except psutil.NoSuchProcess:
            print(f"{name} was already terminated.")
    print("All services stopped.")

# Start each service
try:
    start_service("Database Service", "uvicorn db_service:app --host 127.0.0.1 --port 8002 --reload")
    start_service("Embedding Service", "uvicorn embedding_service:app --host 127.0.0.1 --port 8001 --reload")
    start_service("Composite API", "uvicorn main_composite_api:app --host 127.0.0.1 --port 8000 --reload")
    start_service("Watchdog Script", "python watchdog_script.py")
    start_service("Web Interface", "uvicorn web_interface:app --host 127.0.0.1 --port 8003 --reload")

    print("All services started. Press Ctrl+C to stop.")

    # Keep the main thread alive to catch Ctrl+C
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected.")
    stop_services()
    sys.exit(0)

except Exception as e:
    print(f"An error occurred: {e}")
    stop_services()
    sys.exit(1)
