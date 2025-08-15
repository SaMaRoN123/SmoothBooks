@echo off
echo Starting SmoothBooks Accounting Software...
echo.

echo Starting Backend Server...
cd backend
start "SmoothBooks Backend" cmd /k "venv\Scripts\activate && python app.py"

echo.
echo Starting Frontend Server...
cd ..\frontend
start "SmoothBooks Frontend" cmd /k "npm start"

echo.
echo SmoothBooks is starting up!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul 