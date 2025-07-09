#!/bin/bash
echo "Launching Gizmo BuyBot..."
python gizmo_buybot.py &
python dummy_server.py
