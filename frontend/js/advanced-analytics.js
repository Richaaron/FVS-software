/**
 * Advanced Analytics Manager - Enhanced statistical analysis and visualizations
 * Features: Advanced statistics, additional charts, comparisons, exports
 */

class AdvancedAnalyticsManager {
    constructor() {
        this.currentData = [];
        this.comparableData = null;
        this.charts = {};
    }

    /**
     * Calculate advanced statistics
     */
    calculateAdvancedStats(results) {
        if (!results || results.length === 0) {
            return null;
        }

        const scores = results.map(r => r.total_score).sort((a, b) => a - b);
        const n = scores.length;

        // Basic calculations
        const sum = scores.reduce((a, b) => a + b, 0);
        const mean = sum / n;
        const min = scores[0];
        const max = scores[n - 1];
        const range = max - min;

        // Median
        const median = n % 2 === 0 
            ? (scores[n / 2 - 1] + scores[n / 2]) / 2 
            : scores[Math.floor(n / 2)];

        // Mode (most frequent score)
        const freqMap = {};
        scores.forEach(score => {
            freqMap[score] = (freqMap[score] || 0) + 1;
        });
        const mode = Object.keys(freqMap).reduce((a, b) => 
            freqMap[a] > freqMap[b] ? a : b
        );

        // Standard deviation
        const variance = scores.reduce((sum, score) => 
            sum + Math.pow(score - mean, 2), 0
        ) / n;
        const stdDev = Math.sqrt(variance);

        // Quartiles
        const q1Index = Math.floor(n * 0.25);
        const q3Index = Math.floor(n * 0.75);
        const q1 = scores[q1Index];
        const q3 = scores[q3Index];

        // Percentiles
        const p10Index = Math.floor(n * 0.10);
        const p90Index = Math.floor(n * 0.90);
        const p10 = scores[p10Index];
        const p90 = scores[p90Index];

        // Grade distribution
        const gradeDistribution = this.getGradeDistribution(results);

        // Pass rate
        const passingResults = results.filter(r => r.grade !== 'F');
        const passRate = (passingResults.length / n) * 100;

        // Average by class
        const avgByClass = this.getAverageByClass(results);

        // Average by subject
        const avgBySubject = this.getAverageBySubject(results);

        return {
            count: n,
            mean: mean.toFixed(2),
            median: median.toFixed(2),
            mode: mode,
            min: min,
            max: max,
            range: range,
            stdDev: stdDev.toFixed(2),
            q1: q1.toFixed(2),
            q3: q3.toFixed(2),
            iqr: (q3 - q1).toFixed(2),
            p10: p10.toFixed(2),
            p90: p90.toFixed(2),
            passRate: passRate.toFixed(1),
            gradeDistribution: gradeDistribution,
            avgByClass: avgByClass,
            avgBySubject: avgBySubject
        };
    }

    /**
     * Get grade distribution
     */
    getGradeDistribution(results) {
        const distribution = {
            A: 0, B: 0, C: 0, D: 0, E: 0, F: 0
        };

        results.forEach(result => {
            if (distribution.hasOwnProperty(result.grade)) {
                distribution[result.grade]++;
            }
        });

        return distribution;
    }

    /**
     * Get average score by class
     */
    getAverageByClass(results) {
        const byClass = {};

        results.forEach(result => {
            if (!byClass[result.class_id]) {
                byClass[result.class_id] = { total: 0, count: 0, name: result.class_name };
            }
            byClass[result.class_id].total += result.total_score;
            byClass[result.class_id].count++;
        });

        const averages = {};
        Object.keys(byClass).forEach(classId => {
            const data = byClass[classId];
            averages[data.name] = (data.total / data.count).toFixed(2);
        });

        return averages;
    }

    /**
     * Get average score by subject
     */
    getAverageBySubject(results) {
        const bySubject = {};

        results.forEach(result => {
            if (!bySubject[result.subject_id]) {
                bySubject[result.subject_id] = { 
                    total: 0, 
                    count: 0, 
                    name: result.subject_name 
                };
            }
            bySubject[result.subject_id].total += result.total_score;
            bySubject[result.subject_id].count++;
        });

        const averages = {};
        Object.keys(bySubject).forEach(subjectId => {
            const data = bySubject[subjectId];
            averages[data.name] = (data.total / data.count).toFixed(2);
        });

        return averages;
    }

    /**
     * Generate performance trend chart data
     */
    getPerformanceTrend(results, termHistory) {
        const trends = {};

        results.forEach(result => {
            const term = result.term_id || 'Unknown';
            if (!trends[term]) {
                trends[term] = { scores: [], count: 0 };
            }
            trends[term].scores.push(result.total_score);
            trends[term].count++;
        });

        const chartData = {
            labels: Object.keys(trends),
            averages: Object.keys(trends).map(term => 
                (trends[term].scores.reduce((a, b) => a + b, 0) / trends[term].count).toFixed(2)
            ),
            highestAverage: Object.keys(trends).map(term => 
                Math.max(...trends[term].scores)
            ),
            lowestAverage: Object.keys(trends).map(term => 
                Math.min(...trends[term].scores)
            )
        };

        return chartData;
    }

    /**
     * Create performance by gender chart
     */
    createGenderPerformanceChart(containerId, results) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const genderData = {};
        results.forEach(result => {
            const gender = result.student_gender || 'Unknown';
            if (!genderData[gender]) {
                genderData[gender] = { scores: [], count: 0 };
            }
            genderData[gender].scores.push(result.total_score);
            genderData[gender].count++;
        });

        const labels = Object.keys(genderData);
        const avgScores = labels.map(gender => 
            (genderData[gender].scores.reduce((a, b) => a + b, 0) / genderData[gender].count).toFixed(2)
        );
        const passRates = labels.map(gender => {
            const passing = results.filter(r => (r.student_gender || 'Unknown') === gender && r.grade !== 'F').length;
            const total = results.filter(r => (r.student_gender || 'Unknown') === gender).length;
            return ((passing / total) * 100).toFixed(1);
        });

        const canvas = document.getElementById(containerId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Average Score',
                        data: avgScores,
                        backgroundColor: '#4ecdc4',
                        borderColor: '#44b0a8',
                        borderWidth: 2
                    },
                    {
                        label: 'Pass Rate (%)',
                        data: passRates,
                        backgroundColor: '#95e1d3',
                        borderColor: '#7dd4c3',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Performance by Gender' }
                },
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });
    }

    /**
     * Create subject difficulty chart
     */
    createSubjectDifficultyChart(containerId, results) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const subjectData = {};
        results.forEach(result => {
            const subject = result.subject_name || 'Unknown';
            if (!subjectData[subject]) {
                subjectData[subject] = { scores: [], failing: 0 };
            }
            subjectData[subject].scores.push(result.total_score);
            if (result.grade === 'F') {
                subjectData[subject].failing++;
            }
        });

        const subjects = Object.keys(subjectData).sort();
        const avgScores = subjects.map(subject => 
            (subjectData[subject].scores.reduce((a, b) => a + b, 0) / subjectData[subject].scores.length).toFixed(2)
        );
        const failureRates = subjects.map(subject => {
            const failRate = (subjectData[subject].failing / subjectData[subject].scores.length) * 100;
            return failRate.toFixed(1);
        });

        const canvas = document.getElementById(containerId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.charts[containerId] = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Subject Difficulty (Avg Score vs Failure Rate)',
                        data: subjects.map((subject, i) => ({
                            x: avgScores[i],
                            y: failureRates[i],
                            label: subject
                        })),
                        backgroundColor: 'rgba(255, 107, 107, 0.6)',
                        borderColor: 'rgba(255, 107, 107, 1)',
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const index = context.dataIndex;
                                return subjects[index] + ': Avg ' + context.raw.x + ', Fail Rate ' + context.raw.y + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Average Score' },
                        min: 0,
                        max: 100
                    },
                    y: {
                        title: { display: true, text: 'Failure Rate (%)' },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    /**
     * Create performance trend over terms
     */
    createPerformanceTrendChart(containerId, results) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const termData = {};
        results.forEach(result => {
            const term = result.term_name || `Term ${result.term_id}`;
            if (!termData[term]) {
                termData[term] = { scores: [], grades: {} };
            }
            termData[term].scores.push(result.total_score);
            termData[term].grades[result.grade] = (termData[term].grades[result.grade] || 0) + 1;
        });

        const terms = Object.keys(termData).sort();
        const avgScores = terms.map(term =>
            (termData[term].scores.reduce((a, b) => a + b, 0) / termData[term].scores.length).toFixed(2)
        );

        const canvas = document.getElementById(containerId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: terms,
                datasets: [
                    {
                        label: 'Average Performance',
                        data: avgScores,
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#4ecdc4',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Performance Trend Over Terms' }
                },
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
            }
        });
        this.charts = {};
    }
}

// Global advanced analytics instance
const advancedAnalyticsManager = new AdvancedAnalyticsManager();

/**
 * Export data to CSV
 */
function exportToCSV(results, filename = 'analytics-export.csv') {
    if (!results || results.length === 0) {
        toast.warning('No data to export');
        return;
    }

    const headers = ['Student Name', 'Admission #', 'Subject', 'Class', '1st CA', '2nd CA', 'Exam', 'Total', 'Grade', 'Remarks'];
    const rows = results.map(r => [
        r.student_name,
        r.admission_number,
        r.subject_name,
        r.class_name,
        r.ca1,
        r.ca2,
        r.exam,
        r.total_score.toFixed(2),
        r.grade,
        r.remarks
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    toast.success('Data exported successfully');
}

/**
 * Generate statistics report HTML
 */
function generateStatisticsReport(stats) {
    if (!stats) return '';

    return `
        <div class="statistics-report">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Count</div>
                    <div class="stat-value">${stats.count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Mean</div>
                    <div class="stat-value">${stats.mean}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Median</div>
                    <div class="stat-value">${stats.median}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Mode</div>
                    <div class="stat-value">${stats.mode}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Std Dev</div>
                    <div class="stat-value">${stats.stdDev}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Min</div>
                    <div class="stat-value">${stats.min}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max</div>
                    <div class="stat-value">${stats.max}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Range</div>
                    <div class="stat-value">${stats.range}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Q1</div>
                    <div class="stat-value">${stats.q1}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Q3</div>
                    <div class="stat-value">${stats.q3}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">IQR</div>
                    <div class="stat-value">${stats.iqr}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pass Rate</div>
                    <div class="stat-value">${stats.passRate}%</div>
                </div>
            </div>

            <div class="distribution-section">
                <h4>📊 Grade Distribution</h4>
                <div class="grade-distribution">
                    ${Object.keys(stats.gradeDistribution).map(grade => `
                        <div class="grade-item">
                            <span class="grade-label">Grade ${grade}</span>
                            <div class="grade-bar">
                                <div class="grade-fill grade-${grade.toLowerCase()}" style="width: ${(stats.gradeDistribution[grade] / stats.count) * 100}%"></div>
                            </div>
                            <span class="grade-count">${stats.gradeDistribution[grade]}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="averages-section">
                <h4>📈 Average by Class</h4>
                <div class="averages-grid">
                    ${Object.entries(stats.avgByClass).map(([className, avg]) => `
                        <div class="average-item">
                            <span class="average-label">${className}</span>
                            <span class="average-value">${avg}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="averages-section">
                <h4>📚 Average by Subject</h4>
                <div class="averages-grid">
                    ${Object.entries(stats.avgBySubject).map(([subjectName, avg]) => `
                        <div class="average-item">
                            <span class="average-label">${subjectName}</span>
                            <span class="average-value">${avg}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

/**
 * Add CSS styles for advanced analytics
 */
function initAdvancedAnalyticsStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .statistics-report {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.2);
        }

        .stat-label {
            font-size: 0.85rem;
            color: #666;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 1.8rem;
            color: #4ecdc4;
            font-weight: bold;
        }

        .distribution-section,
        .averages-section {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .distribution-section h4,
        .averages-section h4 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1rem;
        }

        .grade-distribution {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .grade-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .grade-label {
            min-width: 70px;
            font-weight: 600;
            color: #333;
        }

        .grade-bar {
            flex: 1;
            height: 24px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }

        .grade-fill {
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .grade-A { background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%); }
        .grade-B { background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%); }
        .grade-C { background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); }
        .grade-D { background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); }
        .grade-E { background: linear-gradient(90deg, #ec4899 0%, #be185d 100%); }
        .grade-F { background: linear-gradient(90deg, #6b7280 0%, #4b5563 100%); }

        .grade-count {
            min-width: 50px;
            text-align: right;
            font-weight: 600;
            color: #666;
        }

        .averages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }

        .average-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: #f5f5f5;
            border-radius: 6px;
            border-left: 4px solid #4ecdc4;
        }

        .average-label {
            font-weight: 600;
            color: #333;
        }

        .average-value {
            font-weight: bold;
            color: #4ecdc4;
            font-size: 1.1rem;
        }

        .advanced-filters {
            background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #00d4ff;
        }

        .advanced-filters h4 {
            margin: 0 0 12px 0;
            color: #0c4a6e;
            font-weight: 600;
        }

        .filter-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 12px;
        }

        .filter-group label {
            font-size: 0.9rem;
            color: #0c4a6e;
            font-weight: 600;
            display: block;
            margin-bottom: 6px;
        }

        .filter-group input,
        .filter-group select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #0d9488;
            border-radius: 6px;
            font-size: 0.9rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 10px;
            }

            .stat-value {
                font-size: 1.3rem;
            }

            .averages-grid {
                grid-template-columns: 1fr;
            }

            .filter-group {
                grid-template-columns: 1fr;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize styles when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdvancedAnalyticsStyles);
} else {
    initAdvancedAnalyticsStyles();
}
