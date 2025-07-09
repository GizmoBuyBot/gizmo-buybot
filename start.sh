#!/bin/bash
echo "Launching Gizmo BuyBot..."

# Start dummy Flask server to keep Render port open
python dummy_server.py &

# Start the actual buybot
python gizmo_buybot.py
