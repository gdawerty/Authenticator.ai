#!/bin/bash

# Authentia AI - Start Script
# Runs both backend and frontend simultaneously

echo "🚀 Starting Authentia AI..."
echo ""

# Kill any existing processes on ports 8002 and 5175
lsof -ti:8002 | xargs kill -9 2>/dev/null
lsof -ti:5175 | xargs kill -9 2>/dev/null

# Start backend in background
echo "📦 Starting Backend (port 8002)..."
cd backend_new
source ../.venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --reload-dir app --port 8002 &
BACKEND_PID=$!
cd ..

# Give backend a moment to start
sleep 2

# Start frontend in background
echo "🎨 Starting Frontend (port 5175)..."
cd frontend_new
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers starting!"
echo ""
echo "   Frontend: http://localhost:5175"
echo "   Backend:  http://localhost:8002"
echo ""
echo "Press Ctrl+C to stop both servers"

# Handle Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for both processes
wait
