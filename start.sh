#!/bin/bash

echo "Starting SmoothBooks Accounting Software..."
echo ""

echo "Starting Backend Server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

echo ""
echo "Starting Frontend Server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "SmoothBooks is starting up!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
