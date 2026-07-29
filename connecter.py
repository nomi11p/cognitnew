import os
import socket
import importlib
from pathlib import Path

print("=" * 45)
print("        COGNIT TEST LAUNCHER")
print("=" * 45)

# ---------------------------------
# Check project files
# ---------------------------------

files = [
    "server.py",
    "database.py",
    "manager.py",
    "apiforserver.py"
]

for file in files:
    if Path(file).exists():
        print(f"[PASS] {file}")
    else:
        print(f"[FAIL] {file}")

print()

# ---------------------------------
# Import tests
# ---------------------------------

modules = [
    "database",
    "manager",
    "apiforserver",
]

for module in modules:
    try:
        importlib.import_module(module)
        print(f"[PASS] Import {module}")
    except Exception as e:
        print(f"[FAIL] Import {module}")
        print("      ", e)

print()

# ---------------------------------
# Environment variables
# ---------------------------------

keys = [
    "OPENROUTER_API_KEY",
    "GROQ_API_KEY",
    "MISTRAL_API_KEY",
    "COHERE_API_KEY",
    "FLASK_SECRET_KEY"
]

for key in keys:
    if os.getenv(key):
        print(f"[PASS] {key}")
    else:
        print(f"[WARN] {key} missing")

print()

# ---------------------------------
# Is Flask running?
# ---------------------------------

HOST = "127.0.0.1"
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)

try:
    sock.connect((HOST, PORT))
    print("[PASS] Flask Server Running")
except:
    print("[FAIL] Flask Server NOT Running")

sock.close()

print()
print("=" * 45)
print("         TEST COMPLETE")
print("=" * 45)