@echo off
echo Starting React Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
echo Starting development server...
npm start
pause
