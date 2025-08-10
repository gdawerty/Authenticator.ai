# Authenticator.ai

## 1️⃣ Create & Activate Virtual Environment (Backend)
```bash
# Go into the backend folder
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Activate virtual environment (Windows PowerShell)
venv\Scripts\Activate
```

---

## 2️⃣ Install Required Packages (Backend)
```bash
pip install flask==3.0.3 flask-restx==1.3.0 werkzeug==3.0.3
```
Or install from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 3️⃣ Run the Backend Server
```bash
python app.py
```
You should see:
```
Flask API Server Starting...
 * Running on http://localhost:8000
```

---

## 4️⃣ Access the API
- Root Endpoint → http://localhost:8000/
- Swagger Docs → http://localhost:8000/docs
- Health Check → http://localhost:8000/health
- Upload Endpoint (POST) → http://localhost:8000/upload

---

## 5️⃣ Example File Upload with cURL
```bash
curl -X POST "http://localhost:8000/upload"   -H "accept: application/json"   -H "Content-Type: multipart/form-data"   -F "file=@/path/to/your/file.txt"
```

---

## 6️⃣ Run the Frontend
```bash
# Go into the frontend folder
cd frontend

# Install Node.js if not already installed
# For Mac with Homebrew:
brew install node
# For Windows: Download from https://nodejs.org/

# Install dependencies
npm install

# Start the development server
npm run dev
```
By default, the frontend will be available at:
```
http://localhost:3000
```
