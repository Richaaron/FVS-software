const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'fvs_secret_key_2025_secure';

app.use(cors());
app.use(bodyParser.json());

const DATA_FILE = path.join(__dirname, 'data.json');

function loadData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.error('Error loading data:', err);
    }
    return {
        schoolName: 'Folusho Victory Schools',
        schoolType: 'primary',
        academicSession: '2025/2026',
        term: 'First Term',
        admin: { username: 'admin', password: '' },
        teachers: [],
        students: [],
        subjects: [],
        scores: [],
        activities: []
    };
}

function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

let data = loadData();
if (!data.admin.password) {
    data.admin.password = bcrypt.hashSync('admin123', 10);
    saveData(data);
}

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Access denied' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token' });
        req.user = user;
        next();
    });
}

app.post('/api/login', (req, res) => {
    const { username, password, type } = req.body;
    data = loadData();

    if (type === 'admin') {
        if (username === data.admin.username && bcrypt.compareSync(password, data.admin.password)) {
            const token = jwt.sign({ username, role: 'admin' }, JWT_SECRET, { expiresIn: '24h' });
            return res.json({ token, user: { username, role: 'admin' } });
        }
    } else if (type === 'teacher') {
        const teacher = data.teachers.find(t => t.username === username);
        if (teacher && bcrypt.compareSync(password, teacher.password)) {
            const token = jwt.sign({ username, role: 'teacher', id: teacher.id }, JWT_SECRET, { expiresIn: '24h' });
            return res.json({ token, user: { username: teacher.name, role: 'teacher', teacher } });
        }
    }
    res.status(401).json({ error: 'Invalid credentials' });
});

app.get('/api/data', authenticateToken, (req, res) => {
    data = loadData();
    const safeData = { ...data };
    safeData.teachers = safeData.teachers.map(t => ({ ...t, password: '***' }));
    safeData.scores = [];
    res.json(safeData);
});

app.post('/api/school', authenticateToken, (req, res) => {
    data = loadData();
    Object.assign(data, req.body);
    saveData(data);
    res.json({ success: true });
});

app.post('/api/admin/reset-password', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    const { username, password } = req.body;
    if (username) data.admin.username = username;
    if (password) data.admin.password = bcrypt.hashSync(password, 10);
    saveData(data);
    res.json({ success: true });
});

app.get('/api/teachers', authenticateToken, (req, res) => {
    data = loadData();
    res.json(data.teachers.map(t => ({ ...t, password: '***' })));
});

app.post('/api/teachers', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    const { name, email, username, password, assignedClass, assignedSubject } = req.body;
    const teacher = {
        id: 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        name, email, username,
        password: bcrypt.hashSync(password, 10),
        assignedClass, assignedSubject
    };
    data.teachers.push(teacher);
    saveData(data);
    res.json({ success: true, teacher: { ...teacher, password: '***' } });
});

app.delete('/api/teachers/:id', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    data.teachers = data.teachers.filter(t => t.id !== req.params.id);
    saveData(data);
    res.json({ success: true });
});

app.get('/api/students', authenticateToken, (req, res) => {
    data = loadData();
    res.json(data.students);
});

app.post('/api/students', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    const student = {
        id: 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        ...req.body
    };
    data.students.push(student);
    saveData(data);
    res.json({ success: true, student });
});

app.delete('/api/students/:id', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    data.students = data.students.filter(s => s.id !== req.params.id);
    data.scores = data.scores.filter(s => s.studentId !== req.params.id);
    saveData(data);
    res.json({ success: true });
});

app.get('/api/subjects', authenticateToken, (req, res) => {
    data = loadData();
    res.json(data.subjects);
});

app.post('/api/subjects', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    const subject = {
        id: 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        ...req.body
    };
    data.subjects.push(subject);
    saveData(data);
    res.json({ success: true, subject });
});

app.delete('/api/subjects/:id', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = loadData();
    data.subjects = data.subjects.filter(s => s.id !== req.params.id);
    saveData(data);
    res.json({ success: true });
});

app.get('/api/scores', authenticateToken, (req, res) => {
    data = loadData();
    res.json(data.scores);
});

app.post('/api/scores', authenticateToken, (req, res) => {
    data = loadData();
    const { scores } = req.body;
    scores.forEach(scoreData => {
        const existingIndex = data.scores.findIndex(s =>
            s.studentId === scoreData.studentId &&
            s.subject === scoreData.subject &&
            s.className === scoreData.className
        );
        if (existingIndex > -1) {
            data.scores[existingIndex] = scoreData;
        } else {
            data.scores.push(scoreData);
        }
    });
    saveData(data);
    res.json({ success: true });
});

app.get('/api/results', authenticateToken, (req, res) => {
    data = loadData();
    res.json(data.scores);
});

app.get('/api/export', authenticateToken, (req, res) => {
    data = loadData();
    res.setHeader('Content-Disposition', 'attachment; filename=school_data.json');
    res.json(data);
});

app.post('/api/import', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    data = req.body;
    saveData(data);
    res.json({ success: true });
});

app.post('/api/clear', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
    fs.unlinkSync(DATA_FILE);
    data = loadData();
    saveData(data);
    res.json({ success: true });
});

app.listen(PORT, () => {
    console.log(`FVS Backend running on http://localhost:${PORT}`);
});