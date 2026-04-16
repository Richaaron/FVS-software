# Email Authentication System - FVS Software

## Overview

The FVS Software Email Authentication System provides automated email notifications for:
- **Teachers**: Auto-generated login credentials
- **Parents**: Student result notifications

## Setup Instructions

### 1. Configure Email Settings

Create a `.env` file in the root directory based on `.env.example`:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
APP_URL=http://localhost:5000
```

### 2. Gmail Setup (Recommended)

1. Enable 2-Factor Authentication on your Google Account
2. Visit https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Generate an App Password (16 characters)
5. Use this password as `SENDER_PASSWORD` in `.env`

### 3. Alternative Email Providers

#### Outlook/Microsoft 365
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

#### SendGrid
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SENDER_EMAIL=your-ses-email@example.com
SENDER_PASSWORD=your-ses-password
```

---

## Email Features

### A. Teacher Login Credentials

#### When Teacher is Created

Teachers can receive their login credentials automatically when you add `"send_email": true` to the teacher creation request:

```javascript
// Create teacher with auto-send credentials
const response = await fetch('http://127.0.0.1:5000/api/teachers', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: JSON.stringify({
        school_id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '08012345678',
        qualification: 'BSc',
        specialization: 'Mathematics',
        send_email: true  // ← Add this to send credentials
    })
});
```

#### Resend Credentials Later

You can resend credentials to a teacher anytime using the dedicated endpoint:

**Endpoint:** `POST /api/email/send-teacher-credentials/<teacher_id>`

```bash
curl -X POST http://127.0.0.1:5000/api/email/send-teacher-credentials/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe_001",
    "password": "GeneratedPassword123"
  }'
```

**Response:**
```json
{
    "success": true,
    "message": "Teacher credentials sent to john@example.com",
    "teacher_id": 1,
    "email": "john@example.com"
}
```

#### Bulk Send Credentials

Send credentials to multiple teachers at once:

**Endpoint:** `POST /api/email/send-teacher-credentials-bulk`

```bash
curl -X POST http://127.0.0.1:5000/api/email/send-teacher-credentials-bulk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_ids": [1, 2, 3],
    "school_id": 1
  }'
```

**Response:**
```json
{
    "success": true,
    "message": "Sent 3 of 3 teacher credential emails",
    "sent_count": 3,
    "total_count": 3,
    "failed_teachers": [],
    "note": "Passwords should be provided separately for security"
}
```

---

### B. Student Result Notifications

#### Send Result to Parent

When you post a student result, include `"send_email": true` to automatically notify the parent:

```javascript
// Create result and send to parent
const response = await fetch('http://127.0.0.1:5000/api/results', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: JSON.stringify({
        student_id: 1,
        subject_id: 2,
        term_id: 1,
        ca1: 8,      // 1st Continuous Assessment (0-10)
        ca2: 9,      // 2nd Continuous Assessment (0-10)
        exam: 75,    // Exam score (0-80)
        send_email: true  // ← Add this to notify parent
    })
});
```

**Response includes:**
```json
{
    "id": 1,
    "student_name": "Jane Smith",
    "subject_name": "Mathematics",
    "ca1": 8,
    "ca2": 9,
    "exam": 75,
    "total_score": 92,
    "grade": "A",
    "remarks": "Excellent",
    "email_sent": true,
    "email_message": "Result notification sent to parent@example.com"
}
```

#### Send Result Later

Send result notification to parent anytime after posting:

**Endpoint:** `POST /api/email/send-result-to-parent/<result_id>`

```bash
curl -X POST http://127.0.0.1:5000/api/email/send-result-to-parent/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "success": true,
    "message": "Result notification sent to parent@example.com",
    "result_id": 1,
    "student": "Jane Smith",
    "subject": "Mathematics",
    "grade": "A",
    "recipient_email": "parent@example.com"
}
```

#### Bulk Send Results

Send results to all parents for a specific term:

**Endpoint:** `POST /api/email/send-results-bulk`

```bash
curl -X POST http://127.0.0.1:5000/api/email/send-results-bulk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "term_id": 1
  }'
```

Or send specific results:

```bash
curl -X POST http://127.0.0.1:5000/api/email/send-results-bulk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "result_ids": [1, 2, 3, 4, 5]
  }'
```

**Response:**
```json
{
    "success": true,
    "message": "Sent 25 of 30 result notifications",
    "sent_count": 25,
    "total_count": 30,
    "failed_results": [
        {
            "result_id": 5,
            "reason": "Missing student, parent, or subject"
        }
    ]
}
```

---

## Email Management Endpoints

### Check Email Configuration

**Endpoint:** `GET /api/email/config`

Check if email is properly configured:

```bash
curl -X GET http://127.0.0.1:5000/api/email/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email_masked": "you***@gmail.com",
    "is_configured": true,
    "app_url": "http://localhost:5000"
}
```

### Test Email Configuration

**Endpoint:** `POST /api/email/test-send`

Send a test email to verify configuration:

```bash
curl -X POST http://127.0.0.1:5000/api/email/test-send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

**Response:**
```json
{
    "success": true,
    "message": "Test email sent successfully to test@example.com"
}
```

---

## Email Templates

### Teacher Credentials Email
- **Recipient:** Teacher
- **Content:** Username, Password, Login Instructions
- **Security Notes:** Warning to change password on first login
- **Styling:** Professional blue theme matching FVS branding

### Student Result Email
- **Recipient:** Parent
- **Content:** Student name, Subject, Score, Grade (color-coded)
- **Details:** Total points, percentage
- **Link:** Instructions to log in to parent portal
- **Styling:** Professional design with grade color coding (Green for A/B, Orange for C, Red for D/E/F)

---

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Email sent successfully |
| 201 | Result created, email status included |
| 400 | Missing required fields or invalid data |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found (teacher/result/parent) |
| 500 | SMTP configuration error or server error |

---

## Troubleshooting

### "Failed to send email" Error

**Check these:**

1. **SMTP Configuration**
   ```bash
   curl -X GET http://127.0.0.1:5000/api/email/config
   ```

2. **Test Email Sending**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/email/test-send \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"email": "your-email@example.com"}'
   ```

3. **Check .env File**
   - Ensure `.env` is in the backend directory
   - Verify SENDER_EMAIL and SENDER_PASSWORD are correct
   - Restart Flask server: `python app.py`

### Gmail App Password Issues

- Make sure you have **2-Factor Authentication enabled**
- App Password must be **16 characters**
- Some Gmail accounts may need an additional app permissions check
- Try setting a specific app password for Mail only

### Email Not in Spam/Promotions Folder

- Add your SENDER_EMAIL to contacts
- Check email authentication settings (SPF, DKIM records)
- For production, consider using dedicated email services (SendGrid, AWS SES)

---

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use App Passwords** - Not regular account passwords
3. **Rotate credentials regularly** - Especially in production
4. **Use environment variables** - Never hardcode credentials in code
5. **HTTPS only** - Email credentials should only transmit over HTTPS
6. **Limit email frequency** - Implement rate limiting for bulk emails
7. **Audit logs** - Track who sent what emails and when

---

## Integration Example

### Frontend: Sending Teacher Credentials Email

```javascript
// In teacher creation form (index.html)
async function createTeacher() {
    const formData = {
        school_id: schoolSelect.value,
        first_name: firstNameInput.value,
        last_name: lastNameInput.value,
        email: emailInput.value,
        phone: phoneInput.value,
        qualification: qualificationInput.value,
        specialization: specializationInput.value,
        send_email: document.getElementById('sendEmailCheckbox').checked  // ← New option
    };
    
    const response = await fetch('http://127.0.0.1:5000/api/teachers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
        if (result.email_sent) {
            alert(`✓ Teacher created and credentials sent to ${result.auto_generated_credentials.email}`);
        } else {
            alert(`✓ Teacher created. Note: ${result.email_message}`);
        }
    } else {
        alert('Error: ' + result.error);
    }
}
```

### Frontend: Sending Result to Parent

```javascript
// In result entry form (index.html)
async function addResult() {
    const formData = {
        student_id: studentSelect.value,
        subject_id: subjectSelect.value,
        term_id: termSelect.value,
        ca1: parseFloat(ca1Input.value),
        ca2: parseFloat(ca2Input.value),
        exam: parseFloat(examInput.value),
        send_email: document.getElementById('notifyParentCheckbox').checked  // ← New option
    };
    
    const response = await fetch('http://127.0.0.1:5000/api/results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
        alert(`✓ Result: ${result.grade} (${result.total_score}/100)`);
        if (result.email_sent) {
            alert(`📧 Notification sent to parent: ${result.email_message}`);
        }
    } else {
        alert('Error: ' + result.error);
    }
}
```

---

## Support & Documentation

For issues or feature requests, check the FVS Software documentation or contact support.

**GitHub Repository:** https://github.com/Richaaron/FVS-software.git
