# Quick Start Guide

## Starting the Application

### Option 1: Windows
1. Double-click `setup.bat` to install dependencies
2. Run: `python backend/app.py` to start the backend server
3. Open `frontend/index.html` in your web browser

### Option 2: Linux/Mac
1. Run: `bash setup.sh` to install dependencies
2. Run: `python backend/app.py` to start the backend server
3. Open `frontend/index.html` in your web browser

### Option 3: Manual
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Start backend: `cd backend && python app.py`
3. Open frontend in browser

## Default Configuration
- Backend URL: http://localhost:5000
- Frontend: Open index.html in browser
- Database: SQLite (fvs_results.db)

## First Time Setup
1. School information is created automatically (Folusho Victory Schools)
2. Configure additional school details in Settings
3. Create academic sessions and terms
4. Add classes, students, teachers, and subjects
5. Start entering results

## Example Data Entry

### Adding a Class
Settings → Classes → Add New
- Name: "Primary 3"
- Level: "Primary"
- Arm: "A"

### Adding a Student
Students → Add New Student
- Admission #: "P3A001"
- First Name: "Chioma"
- Last Name: "Okafor"
- Class: "Primary 3"

### Adding a Result
Results → Enter Results
- Student: Select student
- Subject: Select subject
- CA: 15
- Assignment: 8
- Exam: 62
- Total will be calculated: 85 (Grade B)

## Common Tasks

### View Student Performance
Results → Student Performance → Select Student → View

### Generate Class Ranking
Reports → Class Ranking → Select Class & Term → Generate

### Print Student Report Card
Reports → Student Report Card → Select Student & Term → Print

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check all dependencies: `pip install -r backend/requirements.txt`
- Port 5000 might be in use; change in app.py

### Frontend won't load data
- Ensure backend is running (http://localhost:5000)
- Check browser console for errors (F12)
- Ensure CORS is enabled in Flask app

### Database errors
- Delete fvs_results.db file to reset database
- Restart the application

## API Testing

Use tools like Postman or cURL to test API:

```bash
# Get all students
curl http://localhost:5000/api/students

# Create a result
curl -X POST http://localhost:5000/api/results \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "subject_id": 1,
    "term_id": 1,
    "continuous_assessment": 15,
    "assignment": 8,
    "exam_score": 62
  }'
```

## Support
For detailed documentation, see README.md
