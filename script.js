const USE_BACKEND = true;
const API_URL = 'http://localhost:3000/api';

let authToken = null;

const schoolData = {
    schoolName: 'Folusho Victory Schools',
    schoolType: '',
    academicSession: '',
    term: '',
    admin: {
        username: 'admin',
        password: 'admin123'
    },
    classes: {
        nursery: ['Nursery 1', 'Nursery 2', 'Kindergarten 1', 'Kindergarten 2'],
        primary: ['Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6'],
        secondary: ['JSS 1', 'JSS 2', 'JSS 3', 'SSS 1', 'SSS 2', 'SSS 3']
    },
    teachers: [],
    students: [],
    subjects: [],
    scores: [],
    activities: [],
    currentUser: null,
    currentRole: null
};

async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (authToken) options.headers['Authorization'] = `Bearer ${authToken}`;
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${API_URL}${endpoint}`, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
}

async function loadAllData() {
    try {
        const data = await apiRequest('/data');
        schoolData.schoolName = data.schoolName;
        schoolData.schoolType = data.schoolType;
        schoolData.academicSession = data.academicSession;
        schoolData.term = data.term;
        schoolData.admin = data.admin;
        schoolData.teachers = data.teachers || [];
        schoolData.students = data.students || [];
        schoolData.subjects = data.subjects || [];
        schoolData.activities = data.activities || [];
        schoolData.scores = data.scores || [];
        renderTeacherTable();
        renderStudentTable();
        renderSubjectTable();
        updateDashboard();
    } catch (err) {
        console.error('Failed to load data:', err);
    }
}

function renderScoreEntryTable(classSelectId, subjectSelectId, tableId) {
    const className = document.getElementById(classSelectId)?.value;
    const subjectName = document.getElementById(subjectSelectId)?.value;
    const tbody = document.querySelector(`#${tableId} tbody`);

    if (!className || !subjectName || !tbody) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Please select class and subject</td></tr>';
        return;
    }

    const classStudents = schoolData.students.filter(s => s.class === className);

    if (classStudents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No students in this class</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    classStudents.forEach(student => {
        const existingScore = schoolData.scores.find(s =>
            s.studentId === student.id &&
            s.subject === subjectName &&
            s.className === className
        );

        const tr = document.createElement('tr');
        tr.dataset.studentId = student.id;
        tr.innerHTML = `
            <td>${student.admissionNo}</td>
            <td>${student.name}</td>
            <td><input type="number" class="ca-score" min="0" max="40" value="${existingScore?.ca || ''}" placeholder="0-40"></td>
            <td><input type="number" class="exam-score" min="0" max="60" value="${existingScore?.exam || ''}" placeholder="0-60"></td>
            <td>${existingScore?.total || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}
}

const gradeScale = {
    secondary: [
        { min: 90, max: 100, grade: 'A1', remark: 'Excellent' },
        { min: 80, max: 89, grade: 'A2', remark: 'Very Good' },
        { min: 70, max: 79, grade: 'B3', remark: 'Good' },
        { min: 65, max: 69, grade: 'C4', remark: 'Credit' },
        { min: 60, max: 64, grade: 'C5', remark: 'Credit' },
        { min: 55, max: 59, grade: 'C6', remark: 'Credit' },
        { min: 50, max: 54, grade: 'D7', remark: 'Pass' },
        { min: 45, max: 49, grade: 'D8', remark: 'Pass' },
        { min: 40, max: 44, grade: 'E9', remark: 'Fair' },
        { min: 0, max: 39, grade: 'F9', remark: 'Fail' }
    ],
    primary: [
        { min: 90, max: 100, grade: 'A', remark: 'Excellent' },
        { min: 75, max: 89, grade: 'B', remark: 'Very Good' },
        { min: 60, max: 74, grade: 'C', remark: 'Good' },
        { min: 50, max: 59, grade: 'D', remark: 'Fair' },
        { min: 0, max: 49, grade: 'F', remark: 'Fail' }
    ],
    nursery: [
        { min: 80, max: 100, grade: 'A', remark: 'Excellent' },
        { min: 60, max: 79, grade: 'B', remark: 'Very Good' },
        { min: 40, max: 59, grade: 'C', remark: 'Good' },
        { min: 0, max: 39, grade: 'D', remark: 'Developing' }
    ]
};

document.addEventListener('DOMContentLoaded', () => {
    loadFromStorage();
    initLogin();
    initLogout();
    initTabs();
    initSchoolForm();
    initTeacherForm();
    initStudentForm();
    initSubjectForm();
    initScoreForm();
    initResultForm();
    initSettings();
    initTeacherViews();
    initPrintButton();
    updateDashboard();
});

function loadFromStorage() {
    const stored = localStorage.getItem('schoolData');
    if (stored) {
        const parsed = JSON.parse(stored);
        Object.assign(schoolData, parsed);
    }
}

function saveToStorage() {
    localStorage.setItem('schoolData', JSON.stringify(schoolData));
}

function addActivity(type, message) {
    const activity = {
        id: generateId(),
        type,
        message,
        time: new Date().toLocaleString()
    };
    schoolData.activities.unshift(activity);
    if (schoolData.activities.length > 50) {
        schoolData.activities.pop();
    }
    saveToStorage();
    renderActivityLog();
}

function initLogin() {
    const loginTabs = document.querySelectorAll('.login-tab');
    const teacherAssignSection = document.getElementById('teacherAssignSection');
    const teacherSubjectSection = document.getElementById('teacherSubjectSection');
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    let loginType = 'admin';

    loginTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            loginTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            loginType = tab.dataset.type;

            if (loginType === 'teacher') {
                teacherAssignSection.style.display = 'block';
                teacherSubjectSection.style.display = 'block';
                updateClassSelectForTeacher();
            } else {
                teacherAssignSection.style.display = 'none';
                teacherSubjectSection.style.display = 'none';
            }
            loginError.textContent = '';
        });
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        try {
            if (USE_BACKEND) {
                const result = await apiRequest('/login', 'POST', { username, password, type: loginType });
                authToken = result.token;
                schoolData.currentUser = result.user.username;
                schoolData.currentRole = result.user.role;
                if (result.user.teacher) schoolData.currentTeacher = result.user.teacher;
                showMainApp(result.user.role);
            } else {
                if (loginType === 'admin') {
                    if (username === schoolData.admin.username && password === schoolData.admin.password) {
                        schoolData.currentUser = username;
                        schoolData.currentRole = 'admin';
                        showMainApp('admin');
                        addActivity('login', 'Admin logged in');
                    } else {
                        loginError.textContent = 'Invalid admin credentials';
                    }
                } else {
                    const teacher = schoolData.teachers.find(t => t.username === username && t.password === password);
                    if (teacher) {
                        schoolData.currentUser = teacher.name;
                        schoolData.currentRole = 'teacher';
                        schoolData.currentTeacher = teacher;
                        showMainApp('teacher');
                        addActivity('login', `Teacher ${teacher.name} logged in`);
                    } else {
                        loginError.textContent = 'Invalid teacher credentials';
                    }
                }
            }
        } catch (err) {
            loginError.textContent = err.message || 'Login failed';
        }
    });
}

function showMainApp(role) {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';

    const currentUser = document.getElementById('currentUser');
    const currentRole = document.getElementById('currentRole');

    currentUser.textContent = schoolData.currentUser;
    currentRole.textContent = role === 'admin' ? 'Administrator' : 'Teacher';
    currentRole.className = `user-role ${role}`;

    if (role === 'admin') {
        document.getElementById('adminContent').style.display = 'block';
        document.getElementById('teacherContent').style.display = 'none';
    } else {
        document.getElementById('adminContent').style.display = 'none';
        document.getElementById('teacherContent').style.display = 'block';
        setupTeacherView();
    }

    updateClassSelects();
    if (USE_BACKEND && authToken) {
        loadAllData();
    }
    updateDashboard();
}

function initLogout() {
    document.getElementById('logoutBtn').addEventListener('click', () => {
        const role = schoolData.currentRole;
        schoolData.currentUser = null;
        schoolData.currentRole = null;
        schoolData.currentTeacher = null;
        authToken = null;

        addActivity('logout', `${role === 'admin' ? 'Admin' : 'Teacher'} logged out`);

        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('mainApp').style.display = 'none';
        document.getElementById('loginForm').reset();
        document.getElementById('loginError').textContent = '';
    });
}

function initTabs() {
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn')) {
            const tabId = e.target.dataset.tab;
            const parent = e.target.closest('.management-tabs');

            parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            parent.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            e.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }
    });
}

function updateClassSelects() {
    const schoolType = schoolData.schoolType || 'primary';
    const classes = schoolData.classes[schoolType] || [];

    const classSelects = [
        document.getElementById('studentClass'),
        document.getElementById('subjectClass'),
        document.getElementById('scoreClass'),
        document.getElementById('resultClass'),
        document.getElementById('teacherClassAssign'),
        document.getElementById('teacherScoreClass'),
        document.getElementById('teacherResultClass')
    ];

    classSelects.forEach(select => {
        if (select) {
            select.innerHTML = '<option value="">Select class</option>';
            classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls;
                option.textContent = cls;
                select.appendChild(option);
            });
        }
    });
}

function updateSubjectSelect() {
    const selectedClass = document.getElementById('scoreClass')?.value || document.getElementById('teacherScoreClass')?.value;
    const subjectSelect = document.getElementById('scoreSubject') || document.getElementById('teacherScoreSubject');

    if (!subjectSelect) return;

    subjectSelect.innerHTML = '<option value="">Select subject</option>';

    if (selectedClass) {
        const availableSubjects = schoolData.subjects.filter(s => s.classes.includes(selectedClass));
        availableSubjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.name;
            option.textContent = subject.name;
            subjectSelect.appendChild(option);
        });
    }
}

function initSchoolForm() {
    const form = document.getElementById('schoolForm');

    if (schoolData.schoolName) {
        document.getElementById('schoolName').value = schoolData.schoolName;
        document.getElementById('schoolType').value = schoolData.schoolType;
        document.getElementById('academicSession').value = schoolData.academicSession;
        document.getElementById('currentTerm').value = schoolData.term;
    }

    const schoolType = document.getElementById('schoolType');
    schoolType.addEventListener('change', () => {
        updateClassSelects();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const schoolInfo = {
            schoolName: document.getElementById('schoolName').value,
            schoolType: document.getElementById('schoolType').value,
            academicSession: document.getElementById('academicSession').value,
            term: document.getElementById('currentTerm').value
        };

        if (USE_BACKEND) {
            try {
                await apiRequest('/school', 'POST', schoolInfo);
                Object.assign(schoolData, schoolInfo);
                showAlert('School information saved successfully!', 'success');
            } catch (err) {
                showAlert(err.message, 'error');
            }
        } else {
            Object.assign(schoolData, schoolInfo);
            saveToStorage();
            updateClassSelects();
            showAlert('School information saved successfully!', 'success');
            addActivity('school', 'School settings updated');
        }
    });
}

function initTeacherForm() {
    const form = document.getElementById('teacherForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('teacherUsername').value;

        if (USE_BACKEND) {
            try {
                await apiRequest('/teachers', 'POST', {
                    name: document.getElementById('teacherName').value,
                    email: document.getElementById('teacherEmail').value,
                    username: username,
                    password: document.getElementById('teacherPassword').value,
                    assignedClass: document.getElementById('teacherClassAssign').value,
                    assignedSubject: document.getElementById('teacherSubjectAssign').value
                });
                await loadAllData();
                form.reset();
                showAlert('Teacher added successfully!', 'success');
            } catch (err) {
                showAlert(err.message, 'error');
            }
        } else {
            if (schoolData.teachers.find(t => t.username === username)) {
                showAlert('Username already exists!', 'error');
                return;
            }

            const teacher = {
                id: generateId(),
                name: document.getElementById('teacherName').value,
                email: document.getElementById('teacherEmail').value,
                username: username,
                password: document.getElementById('teacherPassword').value,
                assignedClass: document.getElementById('teacherClassAssign').value,
                assignedSubject: document.getElementById('teacherSubjectAssign').value
            };

            schoolData.teachers.push(teacher);
            saveToStorage();
            renderTeacherTable();
            updateSubjectSelect();
            form.reset();
            showAlert('Teacher added successfully!', 'success');
            addActivity('teacher', `Teacher ${teacher.name} added`);
        }
    });
}

function renderTeacherTable() {
    const tbody = document.querySelector('#teacherTable tbody');
    tbody.innerHTML = '';

    schoolData.teachers.forEach(teacher => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${teacher.username}</td>
            <td>${teacher.name}</td>
            <td>${teacher.email}</td>
            <td>${teacher.assignedClass || '-'}</td>
            <td>${teacher.assignedSubject || '-'}</td>
            <td><button class="btn btn-danger" onclick="deleteTeacher('${teacher.id}')">Delete</button></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('statTeachers').textContent = schoolData.teachers.length;
}

function deleteTeacher(id) {
    if (USE_BACKEND) {
        apiRequest(`/teachers/${id}`, 'DELETE').then(() => {
            loadAllData();
            showAlert('Teacher deleted!', 'success');
        }).catch(err => showAlert(err.message, 'error'));
    } else {
        const index = schoolData.teachers.findIndex(t => t.id === id);
        if (index > -1) {
            const name = schoolData.teachers[index].name;
            schoolData.teachers.splice(index, 1);
            saveToStorage();
            renderTeacherTable();
            showAlert('Teacher deleted!', 'success');
            addActivity('teacher', `Teacher ${name} removed`);
        }
    }
}

function updateClassSelectForTeacher() {
    const select = document.getElementById('teacherClassAssign');
    if (!select) return;

    const schoolType = schoolData.schoolType || 'primary';
    const classes = schoolData.classes[schoolType] || [];

    select.innerHTML = '<option value="">No class assigned</option>';
    classes.forEach(cls => {
        const option = document.createElement('option');
        option.value = cls;
        option.textContent = cls;
        select.appendChild(option);
    });

    const subjectSelect = document.getElementById('teacherSubjectAssign');
    if (subjectSelect) {
        subjectSelect.innerHTML = '<option value="">No subject assigned</option>';
        schoolData.subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.name;
            option.textContent = subject.name;
            subjectSelect.appendChild(option);
        });
    }
}

function initStudentForm() {
    const form = document.getElementById('studentForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const studentData = {
            name: document.getElementById('studentName').value,
            admissionNo: document.getElementById('studentAdmission').value,
            class: document.getElementById('studentClass').value,
            gender: document.getElementById('studentGender').value
        };

        if (USE_BACKEND) {
            try {
                await apiRequest('/students', 'POST', studentData);
                await loadAllData();
                form.reset();
                showAlert('Student added successfully!', 'success');
            } catch (err) {
                showAlert(err.message, 'error');
            }
        } else {
            const student = {
                id: generateId(),
                ...studentData
            };

            schoolData.students.push(student);
            saveToStorage();
            renderStudentTable();
            updateDashboard();
            form.reset();
            showAlert('Student added successfully!', 'success');
            addActivity('student', `Student ${student.name} added`);
        }
    });
}

function renderStudentTable() {
    const tbody = document.querySelector('#studentTable tbody');
    tbody.innerHTML = '';

    schoolData.students.forEach(student => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${student.admissionNo}</td>
            <td>${student.name}</td>
            <td>${student.class}</td>
            <td>${student.gender}</td>
            <td><button class="btn btn-danger" onclick="deleteStudent('${student.id}')">Delete</button></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('statStudents').textContent = schoolData.students.length;
}

function deleteStudent(id) {
    if (USE_BACKEND) {
        apiRequest(`/students/${id}`, 'DELETE').then(() => {
            loadAllData();
            showAlert('Student deleted!', 'success');
        }).catch(err => showAlert(err.message, 'error'));
    } else {
        const index = schoolData.students.findIndex(s => s.id === id);
        if (index > -1) {
            const name = schoolData.students[index].name;
            schoolData.students.splice(index, 1);
            schoolData.scores = schoolData.scores.filter(s => s.studentId !== id);
            saveToStorage();
            renderStudentTable();
            updateDashboard();
            showAlert('Student deleted!', 'success');
            addActivity('student', `Student ${name} removed`);
        }
    }
}

function initSubjectForm() {
    const form = document.getElementById('subjectForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const selectedClasses = Array.from(document.getElementById('subjectClass').selectedOptions).map(opt => opt.value);
        const subjectData = {
            name: document.getElementById('subjectName').value,
            classes: selectedClasses,
            category: document.getElementById('subjectCategory').value,
            creditHours: parseInt(document.getElementById('creditHours').value)
        };

        if (USE_BACKEND) {
            try {
                await apiRequest('/subjects', 'POST', subjectData);
                await loadAllData();
                form.reset();
                showAlert('Subject added successfully!', 'success');
            } catch (err) {
                showAlert(err.message, 'error');
            }
        } else {
            const subject = {
                id: generateId(),
                ...subjectData
            };

            schoolData.subjects.push(subject);
            saveToStorage();
            renderSubjectTable();
            updateSubjectSelect();
            form.reset();
            showAlert('Subject added successfully!', 'success');
            addActivity('subject', `Subject ${subject.name} added`);
        }
    });
}

function renderSubjectTable() {
    const tbody = document.querySelector('#subjectTable tbody');
    tbody.innerHTML = '';

    schoolData.subjects.forEach(subject => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${subject.name}</td>
            <td>${subject.classes.join(', ')}</td>
            <td>${subject.category}</td>
            <td>${subject.creditHours}</td>
            <td><button class="btn btn-danger" onclick="deleteSubject('${subject.id}')">Delete</button></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('statSubjects').textContent = schoolData.subjects.length;
}

function deleteSubject(id) {
    if (USE_BACKEND) {
        apiRequest(`/subjects/${id}`, 'DELETE').then(() => {
            loadAllData();
            showAlert('Subject deleted!', 'success');
        }).catch(err => showAlert(err.message, 'error'));
    } else {
        const index = schoolData.subjects.findIndex(s => s.id === id);
        if (index > -1) {
            const name = schoolData.subjects[index].name;
            schoolData.subjects.splice(index, 1);
            saveToStorage();
            renderSubjectTable();
            updateSubjectSelect();
            showAlert('Subject deleted!', 'success');
            addActivity('subject', `Subject ${name} removed`);
        }
    }
}

function initScoreForm() {
    const scoreClass = document.getElementById('scoreClass');
    const scoreSubject = document.getElementById('scoreSubject');

    if (scoreClass) {
        scoreClass.addEventListener('change', updateSubjectSelect);
    }

    const scoreForm = document.getElementById('scoreForm');
    if (scoreForm) {
        scoreForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveScores('scoreClass', 'scoreSubject', 'scoreEntryTable');
        });
    }

    if (scoreSubject) {
        scoreSubject.addEventListener('change', () => {
            renderScoreEntryTable('scoreClass', 'scoreSubject', 'scoreEntryTable');
        });
    }
}

function renderScoreEntryTable(classSelectId, subjectSelectId, tableId) {
    const className = document.getElementById(classSelectId)?.value;
    const subjectName = document.getElementById(subjectSelectId)?.value;
    const tbody = document.querySelector(`#${tableId} tbody`);

    if (!className || !subjectName || !tbody) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Please select class and subject</td></tr>';
        return;
    }

    const classStudents = schoolData.students.filter(s => s.class === className);

    if (classStudents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No students in this class</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    classStudents.forEach(student => {
        const existingScore = schoolData.scores.find(s =>
            s.studentId === student.id &&
            s.subject === subjectName &&
            s.className === className
        );

        const tr = document.createElement('tr');
        tr.dataset.studentId = student.id;
        tr.innerHTML = `
            <td>${student.admissionNo}</td>
            <td>${student.name}</td>
            <td><input type="number" class="ca-score" min="0" max="40" value="${existingScore?.ca || ''}" placeholder="0-40"></td>
            <td><input type="number" class="exam-score" min="0" max="60" value="${existingScore?.exam || ''}" placeholder="0-60"></td>
            <td>${existingScore?.total || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function saveScores(classSelectId, subjectSelectId, tableId) {
    const className = document.getElementById(classSelectId).value;
    const subjectName = document.getElementById(subjectSelectId).value;
    const tbody = document.querySelector(`#${tableId} tbody`);
    const rows = tbody.querySelectorAll('tr');

    const scoresToSave = [];

    rows.forEach(row => {
        const studentId = row.dataset.studentId;
        const ca = parseFloat(row.querySelector('.ca-score').value) || 0;
        const exam = parseFloat(row.querySelector('.exam-score').value) || 0;

        if (ca > 40 || exam > 60) {
            showAlert('CA cannot exceed 40 and Exam cannot exceed 60', 'error');
            return;
        }

        scoresToSave.push({
            studentId,
            subject: subjectName,
            className,
            ca,
            exam,
            total: ca + exam
        });
    });

    if (USE_BACKEND) {
        try {
            await apiRequest('/scores', 'POST', { scores: scoresToSave });
            await loadAllData();
            showAlert('Scores saved successfully!', 'success');
        } catch (err) {
            showAlert(err.message, 'error');
        }
    } else {
        scoresToSave.forEach(scoreData => {
            const existingIndex = schoolData.scores.findIndex(s =>
                s.studentId === scoreData.studentId &&
                s.subject === scoreData.subject &&
                s.className === scoreData.className
            );

            if (existingIndex > -1) {
                schoolData.scores[existingIndex] = scoreData;
            } else {
                schoolData.scores.push(scoreData);
            }
        });

        saveToStorage();
        updateDashboard();
        showAlert('Scores saved successfully!', 'success');
        addActivity('score', `Scores entered for ${className} - ${subjectName}`);
    }
}

function initResultForm() {
    const form = document.getElementById('resultForm');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const className = document.getElementById('resultClass').value;
        const term = document.getElementById('resultTerm').value;

        if (!className || !term) {
            showAlert('Please select class and term', 'error');
            return;
        }

        generateResults(className, term, 'teacherResultDisplay');
    });
}

function generateResults(className, term, targetId = 'resultDisplay') {
    const classStudents = schoolData.students.filter(s => s.class === className);
    const classSubjects = schoolData.subjects.filter(s => s.classes.includes(className));

    if (classStudents.length === 0) {
        showAlert('No students found in this class', 'error');
        return;
    }

    if (classSubjects.length === 0) {
        showAlert('No subjects found for this class', 'error');
        return;
    }

    const results = classStudents.map(student => {
        const studentScores = schoolData.scores.filter(s =>
            s.studentId === student.id && s.className === className
        );

        let totalMarks = 0;
        let totalCreditHours = 0;

        const subjectResults = classSubjects.map(subject => {
            const score = studentScores.find(s => s.subject === subject.name);
            const marks = score?.total || 0;
            totalMarks += marks;
            totalCreditHours += subject.creditHours;

            const gradeInfo = getGrade(marks);

            return {
                subject: subject.name,
                ca: score?.ca || 0,
                exam: score?.exam || 0,
                total: marks,
                grade: gradeInfo.grade,
                remark: gradeInfo.remark
            };
        });

        const average = totalMarks / classSubjects.length;
        const gradeInfo = getGrade(average);

        return {
            student,
            subjects: subjectResults,
            totalMarks,
            average: average.toFixed(2),
            grade: gradeInfo.grade,
            gradeRemark: gradeInfo.remark
        };
    });

    results.sort((a, b) => parseFloat(b.average) - parseFloat(a.average));

    results.forEach((result, index) => {
        result.position = index + 1;
    });

    renderResults(results, classSubjects.length, className, term);
}

function getGrade(marks) {
    const scale = gradeScale[schoolData.schoolType] || gradeScale.primary;

    for (const range of scale) {
        if (marks >= range.min && marks <= range.max) {
            return { grade: range.grade, remark: range.remark };
        }
    }

    return { grade: 'N/A', remark: 'No Grade' };
}

function renderResults(results, subjectCount, className, term, targetId = 'resultDisplay') {
    const display = document.getElementById(targetId);
    if (!display) return;

    const passCount = results.filter(r => r.gradeRemark !== 'Fail' && r.grade !== 'F9').length;
    const failCount = results.length - passCount;
    const highestAvg = results.length > 0 ? results[0].average : 0;
    const lowestAvg = results.length > 0 ? results[results.length - 1].average : 0;

    display.innerHTML = `
        <div class="summary-section" style="margin-bottom: 30px;">
            <div class="summary-item">
                <span>Total Students</span>
                <strong>${results.length}</strong>
            </div>
            <div class="summary-item">
                <span>Pass</span>
                <strong>${passCount}</strong>
            </div>
            <div class="summary-item">
                <span>Fail</span>
                <strong>${failCount}</strong>
            </div>
            <div class="summary-item">
                <span>Highest Avg</span>
                <strong>${highestAvg}%</strong>
            </div>
            <div class="summary-item">
                <span>Lowest Avg</span>
                <strong>${lowestAvg}%</strong>
            </div>
        </div>

        ${results.map(result => `
            <div class="report-card">
                <div class="report-header">
                    <h2>${schoolData.schoolName || 'School Name'}</h2>
                    <p>${schoolData.academicSession || '2025/2026'} - ${term}</p>
                </div>

                <div class="student-info">
                    <div><strong>Admission No:</strong> ${result.student.admissionNo}</div>
                    <div><strong>Name:</strong> ${result.student.name}</div>
                    <div><strong>Class:</strong> ${className}</div>
                    <div><strong>Gender:</strong> ${result.student.gender}</div>
                </div>

                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>CA (40)</th>
                            <th>Exam (60)</th>
                            <th>Total (100)</th>
                            <th>Grade</th>
                            <th>Remark</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${result.subjects.map(s => `
                            <tr>
                                <td>${s.subject}</td>
                                <td>${s.ca}</td>
                                <td>${s.exam}</td>
                                <td>${s.total}</td>
                                <td class="grade-${s.grade.charAt(0).toLowerCase()}">${s.grade}</td>
                                <td>${s.remark}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <div class="summary-section" style="margin-top: 20px;">
                    <div class="summary-item">
                        <span>Total Marks</span>
                        <strong>${result.totalMarks}</strong>
                    </div>
                    <div class="summary-item">
                        <span>Average</span>
                        <strong>${result.average}%</strong>
                    </div>
                    <div class="summary-item">
                        <span>Overall Grade</span>
                        <strong>${result.grade}</strong>
                    </div>
                    <div class="summary-item">
                        <span>Position</span>
                        <strong>${result.position}${getOrdinalSuffix(result.position)}</strong>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

function getOrdinalSuffix(n) {
    const s = ['th', 'st', 'nd', 'rd'];
    const v = n % 100;
    return s[(v - 20) % 10] || s[v] || s[0];
}

function initPrintButton() {
    document.getElementById('printBtn')?.addEventListener('click', () => {
        window.print();
    });
}

function initSettings() {
    const adminUsername = document.getElementById('adminUsername');
    const adminPassword = document.getElementById('adminPassword');

    if (adminUsername) adminUsername.value = schoolData.admin?.username || 'admin';

    if (adminUsername) {
        adminUsername.addEventListener('change', () => {
            if (USE_BACKEND) {
                apiRequest('/admin/reset-password', 'POST', { username: adminUsername.value }).then(() => {
                    showAlert('Admin username updated!', 'success');
                }).catch(err => showAlert(err.message, 'error'));
            } else {
                schoolData.admin.username = adminUsername.value;
                saveToStorage();
                showAlert('Admin username updated!', 'success');
            }
        });
    }

    if (adminPassword) {
        adminPassword.addEventListener('change', () => {
            if (adminPassword.value.length >= 4) {
                if (USE_BACKEND) {
                    apiRequest('/admin/reset-password', 'POST', { password: adminPassword.value }).then(() => {
                        showAlert('Admin password updated!', 'success');
                    }).catch(err => showAlert(err.message, 'error'));
                } else {
                    schoolData.admin.password = adminPassword.value;
                    saveToStorage();
                    showAlert('Admin password updated!', 'success');
                }
            }
        });
    }

    document.getElementById('exportBtn')?.addEventListener('click', exportData);
    document.getElementById('importBtn')?.addEventListener('click', importData);
    document.getElementById('clearDataBtn')?.addEventListener('click', clearAllData);
}

function exportData() {
    if (USE_BACKEND) {
        apiRequest('/export', 'GET').then(data => {
            const dataStr = JSON.stringify(data, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `school_data_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showAlert('Data exported successfully!', 'success');
        }).catch(err => showAlert(err.message, 'error'));
    } else {
        const dataStr = JSON.stringify(schoolData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `school_data_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showAlert('Data exported successfully!', 'success');
    }
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                if (USE_BACKEND) {
                    apiRequest('/import', 'POST', data).then(() => {
                        loadAllData();
                        showAlert('Data imported successfully!', 'success');
                    }).catch(err => showAlert(err.message, 'error'));
                } else {
                    Object.assign(schoolData, data);
                    saveToStorage();
                    location.reload();
                    showAlert('Data imported successfully!', 'success');
                }
            } catch (err) {
                showAlert('Invalid file format!', 'error');
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This cannot be undone!')) {
        if (USE_BACKEND) {
            apiRequest('/clear', 'POST').then(() => {
                authToken = null;
                location.reload();
                showAlert('All data cleared!', 'success');
            }).catch(err => showAlert(err.message, 'error'));
        } else {
            localStorage.removeItem('schoolData');
            location.reload();
        }
    }
}

function setupTeacherView() {
    const teacher = schoolData.currentTeacher;
    if (!teacher) return;

    document.getElementById('teacherClassDisplay').textContent = teacher.assignedClass || 'Not assigned';
    document.getElementById('teacherSubjectDisplay').textContent = teacher.assignedSubject || 'Not assigned';

    if (teacher.assignedClass) {
        document.getElementById('teacherScoreClass').value = teacher.assignedClass;
    }

    updateTeacherSubjectSelect();
}

function initTeacherViews() {
    const scoreClass = document.getElementById('teacherScoreClass');
    if (scoreClass) {
        scoreClass.addEventListener('change', updateTeacherSubjectSelect);
    }

    const scoreSubject = document.getElementById('teacherScoreSubject');
    if (scoreSubject) {
        scoreSubject.addEventListener('change', () => {
            renderScoreEntryTable('teacherScoreClass', 'teacherScoreSubject', 'teacherScoreEntryTable');
        });
    }

    const teacherScoreForm = document.getElementById('teacherScoreForm');
    if (teacherScoreForm) {
        teacherScoreForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveScores('teacherScoreClass', 'teacherScoreSubject', 'teacherScoreEntryTable');
        });
    }

    const teacherResultForm = document.getElementById('teacherResultForm');
    if (teacherResultForm) {
        teacherResultForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const className = document.getElementById('teacherResultClass').value;
            const term = document.getElementById('teacherResultTerm').value;
            if (className && term) {
                generateResults(className, term, 'teacherResultDisplay');
            }
        });
    }
}

function updateTeacherSubjectSelect() {
    const className = document.getElementById('teacherScoreClass')?.value;
    const subjectSelect = document.getElementById('teacherScoreSubject');
    const teacher = schoolData.currentTeacher;

    if (!subjectSelect) return;

    subjectSelect.innerHTML = '<option value="">Select subject</option>';

    const availableSubjects = schoolData.subjects.filter(s => 
        s.classes.includes(className) && 
        (!teacher?.assignedSubject || s.name === teacher.assignedSubject)
    );

    availableSubjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.name;
        option.textContent = subject.name;
        subjectSelect.appendChild(option);
    });

    if (teacher?.assignedSubject) {
        subjectSelect.value = teacher.assignedSubject;
    }
}

function updateDashboard() {
    document.getElementById('statStudents').textContent = schoolData.students.length;
    document.getElementById('statTeachers').textContent = schoolData.teachers.length;
    document.getElementById('statSubjects').textContent = schoolData.subjects.length;
    document.getElementById('statScores').textContent = schoolData.scores.length;
    renderActivityLog();
}

function renderActivityLog() {
    const container = document.getElementById('activityLog');
    if (!container) return;

    const icons = {
        login: '🔑',
        logout: '🚪',
        student: '👤',
        teacher: '👨‍🏫',
        subject: '📖',
        score: '📝',
        school: '🏫'
    };

    container.innerHTML = schoolData.activities.slice(0, 10).map(activity => `
        <div class="activity-item">
            <div class="activity-icon">${icons[activity.type] || '📌'}</div>
            <div class="activity-text">${activity.message}</div>
            <div class="activity-time">${activity.time}</div>
        </div>
    `).join('') || '<p style="text-align:center;color:var(--gray);">No recent activity</p>';
}

function generateId() {
    return 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#2563eb'};
        color: white;
        border-radius: 10px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    alert.textContent = message;
    document.body.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 3000);
}