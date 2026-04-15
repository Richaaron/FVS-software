# FVS Software - Folusho Victory Schools Result Management System

A comprehensive result management system for schools with a Node.js backend and HTML/CSS/JavaScript frontend.

## Features

- 🎓 Student management
- 👨‍🏫 Teacher management
- 📚 Subject management
- 📊 Score management and tracking
- 🔐 User authentication with role-based access
- 📱 Responsive web interface

## Project Structure

```
FVS-Software/
├── server.js              # Node.js Express server
├── index.html             # Main frontend interface
├── script.js              # Frontend JavaScript logic
├── style.css              # Frontend styling
├── package.json           # Node.js dependencies
├── data.json              # Sample data file
└── AGENTS.md              # Project documentation
```

## Technology Stack

- **Backend**: Node.js with Express.js
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: JSON-based data storage

## Installation

### Prerequisites
- [Node.js](https://nodejs.org/) (v12 or higher)
- npm (comes with Node.js)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/FVS-Software.git
   cd FVS-Software
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## Running the Application

### Backend Server
```bash
npm start
```
The backend server will run on **http://localhost:3000**

### Frontend
1. Open `index.html` in a web browser
2. Or use a local server to serve the files:
   ```bash
   npx http-server
   ```
   Then navigate to `http://localhost:8080`

## API Endpoints

The backend provides the following REST API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | User authentication |
| GET | `/api/data` | Retrieve all data |
| POST | `/api/data` | Create new data |
| GET | `/api/teachers` | Get all teachers |
| POST | `/api/teachers` | Add new teacher |
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add new student |
| GET | `/api/subjects` | Get all subjects |
| POST | `/api/subjects` | Add new subject |
| GET | `/api/scores` | Get all scores |
| POST | `/api/scores` | Record new score |

## Default Admin Credentials

For testing purposes, use the following credentials:

- **Username**: `admin`
- **Password**: `admin123`

## Project Components

### Backend (server.js)
- Express.js REST API server
- Handles authentication
- Manages school data (students, teachers, subjects, scores)
- Serves as the data backend for the frontend

### Frontend (index.html, script.js, style.css)
- Single-page application interface
- User login and authentication
- Dashboard for managing school data
- Forms for adding/updating records

## Usage

1. Start the backend server
2. Open `index.html` in your browser
3. Login with the default admin credentials
4. Manage students, teachers, subjects, and scores through the interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue in the GitHub repository.

---

**Created**: April 2026  
**Version**: 1.0.0
