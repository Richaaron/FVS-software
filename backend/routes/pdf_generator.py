"""
PDF Generation Module for FVS Result Management System
Generates various PDF reports and documents
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class PDFGenerator:
    """Generate professional PDF reports for FVS system"""
    
    def __init__(self, school_name="Folusho Victory Schools"):
        self.school_name = school_name
        self.page_width, self.page_height = letter
        self.margin = 0.5 * inch
        
    def _create_document(self):
        """Create and return a new document"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=self.school_name
        )
        return doc, buffer
    
    def _get_styles(self):
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Custom title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0a1929'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # School name style
        styles.add(ParagraphStyle(
            name='SchoolName',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#1a3a52'),
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Section heading style
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0d47a1'),
            spaceAfter=6,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def _create_header(self, title, subtitle=""):
        """Create a document header"""
        styles = self._get_styles()
        elements = []
        
        elements.append(Paragraph(self.school_name, styles['SchoolName']))
        elements.append(Paragraph("🎓 Academic Excellence", styles['Subtitle']))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(title, styles['CustomTitle']))
        
        if subtitle:
            elements.append(Paragraph(subtitle, styles['Subtitle']))
        
        elements.append(Spacer(1, 0.15 * inch))
        return elements
    
    def _create_footer(self):
        """Create document footer"""
        styles = self._get_styles()
        footer_text = f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        footer_style = ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )
        return [Spacer(1, 0.3 * inch), Paragraph(footer_text, footer_style)]
    
    def generate_student_transcript(self, student, results):
        """
        Generate student transcript PDF
        Args:
            student: Student object with (id, full_name, admission_number, email, etc.)
            results: List of result dicts with (subject.name, ca1, ca2, exam, total_score, grade, remarks)
        """
        doc, buffer = self._create_document()
        elements = []
        styles = self._get_styles()
        
        # Header
        elements.extend(self._create_header("Student Academic Transcript", f"Admission #{student.admission_number}"))
        
        # Student Info
        student_info_data = [
            ['Student Name:', student.full_name],
            ['Admission Number:', student.admission_number],
            ['Email:', student.email or 'N/A'],
            ['Date Generated:', datetime.now().strftime('%Y-%m-%d')]
        ]
        
        student_info_table = Table(student_info_data, colWidths=[2*inch, 3.5*inch])
        student_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
        ]))
        
        elements.append(student_info_table)
        elements.append(Spacer(1, 0.25 * inch))
        
        # Results Table
        if results:
            elements.append(Paragraph("Academic Results", styles['SectionHeading']))
            
            # Calculate statistics
            total_subjects = len(results)
            total_score = sum(r['total_score'] for r in results)
            average_score = total_score / total_subjects if total_subjects > 0 else 0
            grade_counts = {}
            for r in results:
                grade = r['grade']
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            results_data = [['Subject', 'CA1', 'CA2', 'Exam', 'Total', 'Grade', 'Remarks']]
            for r in results:
                results_data.append([
                    r['subject_name'][:20],
                    str(r['ca1']),
                    str(r['ca2']),
                    str(r['exam']),
                    str(round(r['total_score'], 1)),
                    r['grade'],
                    r['remarks'][:15]
                ])
            
            results_table = Table(results_data, colWidths=[1.8*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.5*inch, 1.0*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(results_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Summary Statistics
            elements.append(Paragraph("Performance Summary", styles['SectionHeading']))
            summary_data = [
                ['Metric', 'Value'],
                ['Total Subjects', str(total_subjects)],
                ['Average Score', f"{average_score:.2f}"],
                ['Grade Distribution', ', '.join([f"{g}:{c}" for g, c in sorted(grade_counts.items())])]
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 3.0*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ecdc4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(summary_table)
        
        elements.append(Spacer(1, 0.3 * inch))
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_teacher_credentials(self, teacher, username, password, staff_id):
        """
        Generate teacher credentials card as PDF
        Args:
            teacher: Teacher object
            username: Auto-generated username
            password: Auto-generated password
            staff_id: Auto-generated staff ID
        """
        doc, buffer = self._create_document()
        elements = []
        styles = self._get_styles()
        
        # Header
        elements.extend(self._create_header("Teacher Account Credentials", "Secure Document"))
        
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("⚠️ CONFIDENTIAL - KEEP THIS DOCUMENT SECURE", styles['Subtitle']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Teacher Information
        teacher_info_data = [
            ['Full Name:', teacher.full_name],
            ['Email:', teacher.email or 'N/A'],
            ['Staff ID:', staff_id],
            ['Qualification:', teacher.qualification or 'N/A'],
            ['Specialization:', teacher.specialization or 'N/A']
        ]
        
        teacher_info_table = Table(teacher_info_data, colWidths=[1.8*inch, 3.7*inch])
        teacher_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbdefb'))
        ]))
        
        elements.append(teacher_info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Login Credentials (emphasized)
        elements.append(Paragraph("Login Credentials", styles['SectionHeading']))
        
        credentials_data = [
            ['Username:', username],
            ['Password:', password],
            ['Portal URL:', 'http://fvs.local/login.html']
        ]
        
        credentials_table = Table(credentials_data, colWidths=[1.8*inch, 3.7*inch])
        credentials_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8dc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#ffa500'))
        ]))
        
        elements.append(credentials_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Important Notes
        elements.append(Paragraph("Important Notes", styles['SectionHeading']))
        
        notes_style = ParagraphStyle(
            name='Notes',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#d32f2f'),
            alignment=TA_LEFT,
            spaceAfter=4
        )
        
        notes = [
            "• Change your password immediately upon first login",
            "• Do not share these credentials with anyone",
            "• Use only on secure networks",
            "• Contact admin if you suspect account compromise",
            f"• Document generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for note in notes:
            elements.append(Paragraph(note, notes_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_class_report(self, class_name, results_by_student):
        """
        Generate class performance report
        Args:
            class_name: Name of the class
            results_by_student: Dict of {student_name: [results]}
        """
        doc, buffer = self._create_document()
        elements = []
        styles = self._get_styles()
        
        # Header
        elements.extend(self._create_header("Class Performance Report", f"Class: {class_name}"))
        
        # Class Summary
        total_students = len(results_by_student)
        elements.append(Spacer(1, 0.15 * inch))
        
        if total_students > 0:
            elements.append(Paragraph("Class Summary", styles['SectionHeading']))
            
            # Calculate averages
            all_grades = {}
            all_totals = []
            
            for student_name, results in results_by_student.items():
                for r in results:
                    all_totals.append(r['total_score'])
                    grade = r['grade']
                    all_grades[grade] = all_grades.get(grade, 0) + 1
            
            avg_score = sum(all_totals) / len(all_totals) if all_totals else 0
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Students', str(total_students)],
                ['Total Results', str(len(all_totals))],
                ['Class Average', f"{avg_score:.2f}"],
                ['Highest Grade', max(all_grades.keys()) if all_grades else 'N/A'],
                ['Most Common Grade', max(all_grades, key=all_grades.get) if all_grades else 'N/A']
            ]
            
            summary_table = Table(summary_data, colWidths=[2.0*inch, 3.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ecdc4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Student list with averages
            elements.append(Paragraph("Student Performance", styles['SectionHeading']))
            
            student_data = [['Student Name', 'Avg Score', 'Total Results', 'Top Grade']]
            
            for student_name, results in sorted(results_by_student.items()):
                if results:
                    avg = sum(r['total_score'] for r in results) / len(results)
                    top_grade = max([r['grade'] for r in results], key=lambda g: ['F', 'E', 'D', 'C', 'B', 'A'].index(g))
                    student_data.append([
                        student_name[:30],
                        f"{avg:.1f}",
                        str(len(results)),
                        top_grade
                    ])
            
            student_table = Table(student_data, colWidths=[3.0*inch, 1.2*inch, 1.2*inch, 0.8*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(student_table)
        
        elements.append(Spacer(1, 0.3 * inch))
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_subject_report(self, subject_name, results):
        """
        Generate subject performance report
        Args:
            subject_name: Name of the subject
            results: List of result dicts
        """
        doc, buffer = self._create_document()
        elements = []
        styles = self._get_styles()
        
        # Header
        elements.extend(self._create_header("Subject Performance Report", f"Subject: {subject_name}"))
        
        if results:
            # Calculate statistics
            total_results = len(results)
            avg_total = sum(r['total_score'] for r in results) / total_results if total_results > 0 else 0
            avg_ca1 = sum(r['ca1'] for r in results) / total_results if total_results > 0 else 0
            avg_ca2 = sum(r['ca2'] for r in results) / total_results if total_results > 0 else 0
            avg_exam = sum(r['exam'] for r in results) / total_results if total_results > 0 else 0
            
            grade_dist = {}
            for r in results:
                grade = r['grade']
                grade_dist[grade] = grade_dist.get(grade, 0) + 1
            
            pass_count = sum(1 for r in results if r['grade'] in ['A', 'B', 'C', 'D', 'E'])
            fail_count = sum(1 for r in results if r['grade'] == 'F')
            pass_rate = (pass_count / total_results * 100) if total_results > 0 else 0
            
            # Statistics
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Paragraph("Performance Metrics", styles['SectionHeading']))
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Students', str(total_results)],
                ['Average CA1 Score', f"{avg_ca1:.2f}"],
                ['Average CA2 Score', f"{avg_ca2:.2f}"],
                ['Average Exam Score', f"{avg_exam:.2f}"],
                ['Average Total Score', f"{avg_total:.2f}"],
                ['Pass Rate', f"{pass_rate:.1f}%"],
                ['Students Passed', str(pass_count)],
                ['Students Failed', str(fail_count)]
            ]
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 2.0*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ecdc4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Grade Distribution
            elements.append(Paragraph("Grade Distribution", styles['SectionHeading']))
            
            grade_data = [['Grade', 'Count', 'Percentage']]
            for grade in sorted(grade_dist.keys(), key=lambda g: ['F', 'E', 'D', 'C', 'B', 'A'].index(g), reverse=True):
                count = grade_dist[grade]
                pct = (count / total_results * 100) if total_results > 0 else 0
                grade_data.append([grade, str(count), f"{pct:.1f}%"])
            
            grade_table = Table(grade_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
            grade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b6b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
            ]))
            
            elements.append(grade_table)
        
        elements.append(Spacer(1, 0.3 * inch))
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
