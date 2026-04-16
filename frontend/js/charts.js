/**
 * Charts Manager - Handles Chart.js visualizations for analytics
 * Features: Grade distribution, subject performance, class analysis, trend analysis
 */

class ChartsManager {
    constructor() {
        this.charts = {};
        this.chartColors = {
            gradeA: '#22c55e',      // Green
            gradeB: '#3b82f6',      // Blue
            gradeC: '#f59e0b',      // Amber
            gradeD: '#ef4444',      // Red
            gradeE: '#ec4899',      // Pink
            gradeF: '#6b7280',      // Gray
            primary: '#4ecdc4',     // Cyan
            secondary: '#667eea',   // Purple
            success: '#48bb78',     // Green
            warning: '#ed8936',     // Orange
            danger: '#f56565'       // Red
        };
    }

    /**
     * Create grade distribution chart (Doughnut/Pie)
     */
    createGradeDistributionChart(containerId, results) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        // Count grades
        const gradeCounts = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0
        };

        results.forEach(result => {
            const grade = result.grade || 'F';
            if (gradeCounts.hasOwnProperty(grade)) {
                gradeCounts[grade]++;
            }
        });

        const totalResults = results.length;
        const data = {
            labels: [
                `A - Excellent (${gradeCounts['A']})`,
                `B - Very Good (${gradeCounts['B']})`,
                `C - Good (${gradeCounts['C']})`,
                `D - Fair (${gradeCounts['D']})`,
                `E - Pass (${gradeCounts['E']})`,
                `F - Fail (${gradeCounts['F']})`
            ],
            datasets: [{
                data: [gradeCounts['A'], gradeCounts['B'], gradeCounts['C'], gradeCounts['D'], gradeCounts['E'], gradeCounts['F']],
                backgroundColor: [
                    this.chartColors.gradeA,
                    this.chartColors.gradeB,
                    this.chartColors.gradeC,
                    this.chartColors.gradeD,
                    this.chartColors.gradeE,
                    this.chartColors.gradeF
                ],
                borderColor: '#fff',
                borderWidth: 3,
                hoverOffset: 8,
                borderRadius: 8
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 12, weight: 'bold' },
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const percentage = ((context.parsed / totalResults) * 100).toFixed(1);
                                return `${context.label.split(' -')[0]}: ${context.parsed} (${percentage}%)`;
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        font: { size: 12 }
                    }
                }
            }
        });
    }

    /**
     * Create subject performance chart (Horizontal Bar)
     */
    createSubjectPerformanceChart(containerId, results) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        // Calculate average scores by subject
        const subjectData = {};
        results.forEach(result => {
            const subject = result.subject_name || 'Unknown';
            if (!subjectData[subject]) {
                subjectData[subject] = { total: 0, count: 0 };
            }
            subjectData[subject].total += result.total_score || 0;
            subjectData[subject].count++;
        });

        const labels = Object.keys(subjectData).sort();
        const averages = labels.map(subject => (subjectData[subject].total / subjectData[subject].count).toFixed(1));

        const data = {
            labels: labels,
            datasets: [{
                label: 'Average Score (0-100)',
                data: averages,
                backgroundColor: this.chartColors.primary,
                borderColor: this.chartColors.secondary,
                borderWidth: 2,
                borderRadius: 6,
                barThickness: 20,
                hoverBackgroundColor: this.chartColors.secondary
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: 12, weight: 'bold' }, padding: 15 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Avg: ${context.parsed.x.toFixed(1)}/100`;
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 10,
                        font: { size: 11 }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { font: { size: 11 } }
                    },
                    y: {
                        ticks: { font: { size: 11 } }
                    }
                }
            }
        });
    }

    /**
     * Create class performance chart (Line/Bar combo)
     */
    createClassPerformanceChart(containerId, results) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        // Calculate statistics by class
        const classData = {};
        results.forEach(result => {
            const className = result.class_name || 'Unknown';
            if (!classData[className]) {
                classData[className] = { total: 0, count: 0, passing: 0 };
            }
            classData[className].total += result.total_score || 0;
            classData[className].count++;
            if ((result.total_score || 0) >= 50) {
                classData[className].passing++;
            }
        });

        const labels = Object.keys(classData).sort();
        const averages = labels.map(cls => (classData[cls].total / classData[cls].count).toFixed(1));
        const passingRates = labels.map(cls => ((classData[cls].passing / classData[cls].count) * 100).toFixed(1));

        const data = {
            labels: labels,
            datasets: [
                {
                    label: 'Average Score',
                    data: averages,
                    borderColor: this.chartColors.primary,
                    backgroundColor: `${this.chartColors.primary}22`,
                    borderWidth: 3,
                    type: 'line',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    yAxisID: 'y'
                },
                {
                    label: 'Passing Rate (%)',
                    data: passingRates,
                    backgroundColor: this.chartColors.success,
                    borderColor: this.chartColors.success,
                    borderWidth: 2,
                    borderRadius: 4,
                    type: 'bar',
                    yAxisID: 'y1'
                }
            ]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: 12, weight: 'bold' }, padding: 15 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        font: { size: 11 }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        max: 100,
                        ticks: { font: { size: 11 } },
                        title: { display: true, text: 'Average Score (0-100)', font: { size: 11, weight: 'bold' } }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        max: 100,
                        ticks: { font: { size: 11 } },
                        title: { display: true, text: 'Passing Rate (%)', font: { size: 11, weight: 'bold' } },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    /**
     * Create student performance trend chart
     */
    createStudentTrendChart(containerId, studentResults) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        // Get top performers
        const studentScores = {};
        studentResults.forEach(result => {
            const student = result.student_name || 'Unknown';
            if (!studentScores[student]) {
                studentScores[student] = { total: 0, count: 0 };
            }
            studentScores[student].total += result.total_score || 0;
            studentScores[student].count++;
        });

        const topStudents = Object.entries(studentScores)
            .map(([name, data]) => ({ name, average: (data.total / data.count).toFixed(1) }))
            .sort((a, b) => b.average - a.average)
            .slice(0, 10);

        const data = {
            labels: topStudents.map(s => s.name),
            datasets: [{
                label: 'Average Score',
                data: topStudents.map(s => s.average),
                backgroundColor: [
                    this.chartColors.gradeA,
                    this.chartColors.gradeB,
                    this.chartColors.gradeC,
                    this.chartColors.primary,
                    this.chartColors.secondary,
                    this.chartColors.success,
                    this.chartColors.warning,
                    this.chartColors.danger,
                    '#06b6d4',
                    '#8b5cf6'
                ],
                borderRadius: 6,
                borderSkipped: false
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.x.toFixed(1)}/100`;
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 10,
                        font: { size: 11 }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { font: { size: 10 } }
                    },
                    y: {
                        ticks: { font: { size: 10 } }
                    }
                }
            }
        });
    }

    /**
     * Create overall statistics cards
     */
    createStatisticsCards(containerId, results) {
        if (results.length === 0) {
            return;
        }

        const totalResults = results.length;
        const totalScore = results.reduce((sum, r) => sum + (r.total_score || 0), 0);
        const averageScore = (totalScore / totalResults).toFixed(1);
        
        const passingCount = results.filter(r => (r.total_score || 0) >= 50).length;
        const passingRate = ((passingCount / totalResults) * 100).toFixed(1);

        const gradeA = results.filter(r => r.grade === 'A').length;
        const gradeF = results.filter(r => r.grade === 'F').length;

        const html = `
            <div class="statistics-grid">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-content">
                        <h4>Total Results</h4>
                        <p class="stat-value">${totalResults}</p>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">📈</div>
                    <div class="stat-content">
                        <h4>Average Score</h4>
                        <p class="stat-value">${averageScore}/100</p>
                    </div>
                </div>

                <div class="stat-card success">
                    <div class="stat-icon">✅</div>
                    <div class="stat-content">
                        <h4>Passing Rate</h4>
                        <p class="stat-value">${passingRate}%</p>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-content">
                        <h4>Grade A Count</h4>
                        <p class="stat-value">${gradeA}</p>
                    </div>
                </div>

                <div class="stat-card danger">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-content">
                        <h4>Grade F Count</h4>
                        <p class="stat-value">${gradeF}</p>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <h4>Failing Count</h4>
                        <p class="stat-value">${totalResults - passingCount}</p>
                    </div>
                </div>
            </div>
        `;

        document.getElementById(containerId).innerHTML = html;
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(containerId) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
            delete this.charts[containerId];
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(key => {
            this.charts[key].destroy();
        });
        this.charts = {};
    }
}

// Global charts manager instance
const chartsManager = new ChartsManager();

/**
 * Add CSS styles for charts and statistics
 */
function initChartsStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .charts-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-top: 2rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(78, 205, 196, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%);
            border-radius: 12px;
            border: 1px solid rgba(78, 205, 196, 0.2);
        }

        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            position: relative;
            min-height: 400px;
        }

        .chart-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .chart-title::before {
            content: '';
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #4ecdc4 0%, #667eea 100%);
            border-radius: 2px;
        }

        canvas {
            max-height: 350px !important;
        }

        .statistics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .stat-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            border-color: #4ecdc4;
        }

        .stat-card.success {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-color: #86efac;
        }

        .stat-card.danger {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-color: #fca5a5;
        }

        .stat-icon {
            font-size: 2.5rem;
            min-width: 60px;
            text-align: center;
        }

        .stat-content h4 {
            margin: 0;
            font-size: 0.9rem;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-value {
            margin: 0.5rem 0 0 0;
            font-size: 1.8rem;
            font-weight: 700;
            color: #1f2937;
            background: linear-gradient(135deg, #4ecdc4 0%, #667eea 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-card.success .stat-value {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-card.danger .stat-value {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Responsive design */
        @media (max-width: 1024px) {
            .charts-section {
                grid-template-columns: 1fr;
            }

            .chart-container {
                min-height: 350px;
            }
        }

        @media (max-width: 768px) {
            .charts-section {
                padding: 1rem;
                gap: 1rem;
                margin-top: 1rem;
            }

            .chart-container {
                padding: 1rem;
                min-height: 300px;
            }

            .chart-title {
                font-size: 1rem;
            }

            canvas {
                max-height: 300px !important;
            }

            .statistics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 0.75rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
            }

            .stat-card {
                padding: 1rem;
                flex-direction: column;
                text-align: center;
            }

            .stat-icon {
                min-width: auto;
                font-size: 2rem;
            }

            .stat-value {
                font-size: 1.4rem;
            }
        }

        @media (max-width: 480px) {
            .statistics-grid {
                grid-template-columns: 1fr;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize charts styles when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChartsStyles);
} else {
    initChartsStyles();
}
