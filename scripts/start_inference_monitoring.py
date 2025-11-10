#!/usr/bin/env python3
"""
Simple Inference Monitoring Starter
Starts the inference API for agent monitoring
"""

import sys
import os
import subprocess
import signal
from datetime import datetime

def main():
    print("=" * 60)
    print("INFERENCE MONITORING STARTER")
    print("=" * 60)

    try:
        # Start inference API
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Inference API on port 8004...")

        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Start the inference API
        cmd = [sys.executable, "-m", "uvicorn", "src.health.inference_api:app",
               "--host", "0.0.0.0", "--port", "8004", "--reload"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True, bufsize=1)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Inference API started with PID: {process.pid}")
        print(f"[INFO] API available at: http://localhost:8004")
        print(f"[INFO] Health check: http://localhost:8004/api/health")
        print(f"[INFO] Real-time metrics: http://localhost:8004/api/realtime/metrics")
        print()
        print("Press Ctrl+C to stop the inference API")
        print("-" * 60)

        # Handle graceful shutdown
        def signal_handler(sig, frame):
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Shutting down Inference API...")
            process.terminate()
            process.wait()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Inference API stopped")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Stream output
        try:
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(f"[API] {line.strip()}")
        except KeyboardInterrupt:
            pass
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait()

    except Exception as e:
        print(f"[ERROR] Failed to start Inference API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()