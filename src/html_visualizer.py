#!/usr/bin/env python3
"""
HTML Visualizer
Chart.js 기반 라이트 테마 시각화 with Export 기능
"""

import json
from typing import Dict, Any
from datetime import datetime


def generate_html_visualization(data: Dict[str, Any], output_file: str) -> str:
    """
    Chart.js 기반 HTML 시각화 생성
    
    Args:
        data: 분석 결과 데이터
        output_file: 출력 파일 경로
        
    Returns:
        생성된 파일 경로
    """
    username = data.get('username', 'Unknown')
    stats = data.get('statistics', {})
    repos = data.get('repositories', [])
    
    # 언어 분포 데이터
    lang_dist = stats.get('language_distribution', {})
    top_10_languages = list(lang_dist.items())[:10]
    lang_labels = [lang for lang, _ in top_10_languages]
    lang_data = [bytes_count / (1024 * 1024) for _, bytes_count in top_10_languages]  # MB
    
    # 리포지토리 커밋 데이터 (상위 15개)
    sorted_repos = sorted(repos, key=lambda x: x.get('commit_count', 0), reverse=True)[:15]
    repo_names = [r['name'] for r in sorted_repos]
    repo_commits = [r.get('commit_count', 0) for r in sorted_repos]
    
    # 스타/포크 데이터
    repo_stars = [r.get('stars', 0) for r in sorted_repos]
    repo_forks = [r.get('forks', 0) for r in sorted_repos]
    
    # 활동성 데이터
    activity_labels = ['최근 업데이트\n(30일 이내)', '활동 중\n(90일 이내)', '비활성']
    activity_data = [
        stats.get('recently_updated_count', 0),
        stats.get('active_repos_count', 0) - stats.get('recently_updated_count', 0),
        stats.get('inactive_repos_count', 0)
    ]
    
    # Public vs Private
    repo_type_labels = ['Public', 'Private']
    repo_type_data = [
        stats.get('public_repositories', 0),
        stats.get('private_repositories', 0)
    ]
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Profile Analysis - {username}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        
        .header-info {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        
        .header-info p {{
            margin: 8px 0;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            font-weight: normal;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .chart-container {{
            position: relative;
            margin-bottom: 50px;
            padding: 30px;
            background: #fafafa;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        
        .export-buttons {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .export-buttons button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 0 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }}
        
        .export-buttons button:hover {{
            background: #2980b9;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .export-buttons {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container" id="reportContent">
        <h1>GitHub Profile Analysis Report</h1>
        
        <div class="header-info">
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Analysis Type:</strong> {data.get('repo_type', 'all').upper()}</p>
            <p><strong>Generated:</strong> {stats.get('analysis_date', 'N/A')}</p>
        </div>
        
        <h2>Overview Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Repositories</h3>
                <div class="value">{stats.get('total_repositories', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Total Commits</h3>
                <div class="value">{stats.get('total_commits', 0):,}</div>
            </div>
            <div class="stat-card">
                <h3>Total Stars</h3>
                <div class="value">{stats.get('total_stars', 0):,}</div>
            </div>
            <div class="stat-card">
                <h3>Total Forks</h3>
                <div class="value">{stats.get('total_forks', 0):,}</div>
            </div>
            <div class="stat-card">
                <h3>Code Size</h3>
                <div class="value">{stats.get('total_size_mb', 0):.1f} MB</div>
            </div>
            <div class="stat-card">
                <h3>Languages Used</h3>
                <div class="value">{stats.get('total_languages', 0)}</div>
            </div>
        </div>
        
        <div class="export-buttons">
            <button onclick="exportAsImage()">Export as Image</button>
            <button onclick="exportTable()">Export Table as Image</button>
            <button onclick="window.print()">Print / Save as PDF</button>
        </div>
        
        <h2>Language Distribution</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="languageChart"></canvas>
            </div>
        </div>
        
        <h2>Repository Activity</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="commitsChart"></canvas>
            </div>
        </div>
        
        <h2>Repository Popularity</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="popularityChart"></canvas>
            </div>
        </div>
        
        <h2>Repository Type Distribution</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="repoTypeChart"></canvas>
            </div>
        </div>
        
        <h2>Activity Status</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="activityChart"></canvas>
            </div>
        </div>
        
        <h2>Detailed Repository List</h2>
        <div id="tableContainer">
            <table>
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Type</th>
                        <th>Commits</th>
                        <th>Stars</th>
                        <th>Forks</th>
                        <th>Language</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # 리포지토리 테이블 데이터
    for repo in sorted(repos, key=lambda x: x.get('stars', 0), reverse=True)[:30]:
        repo_type = 'Private' if repo.get('private') else 'Public'
        html_content += f'''
                    <tr>
                        <td><a href="{repo['url']}" target="_blank">{repo['name']}</a></td>
                        <td>{repo_type}</td>
                        <td>{repo.get('commit_count', 0):,}</td>
                        <td>{repo.get('stars', 0):,}</td>
                        <td>{repo.get('forks', 0):,}</td>
                        <td>{repo.get('language', 'N/A')}</td>
                        <td>{repo.get('updated_date', 'N/A')}</td>
                    </tr>
'''
    
    html_content += f'''
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by GitHub Profile Analyzer</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // Chart.js 기본 설정
        Chart.defaults.color = '#2c3e50';
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
        
        // 언어 분포 차트
        const langCtx = document.getElementById('languageChart');
        new Chart(langCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps(lang_labels)},
                datasets: [{{
                    data: {json.dumps(lang_data)},
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 12
                            }}
                        }}
                    }},
                    title: {{
                        display: true,
                        text: 'Code Distribution by Language (MB)',
                        font: {{
                            size: 16
                        }}
                    }}
                }}
            }}
        }});
        
        // 커밋 수 차트
        const commitsCtx = document.getElementById('commitsChart');
        new Chart(commitsCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(repo_names)},
                datasets: [{{
                    label: 'Commits',
                    data: {json.dumps(repo_commits)},
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    title: {{
                        display: true,
                        text: 'Commits per Repository (Top 15)',
                        font: {{
                            size: 16
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }},
                    x: {{
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 45,
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // 인기도 차트 (스타 vs 포크)
        const popularityCtx = document.getElementById('popularityChart');
        new Chart(popularityCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(repo_names)},
                datasets: [
                    {{
                        label: 'Stars',
                        data: {json.dumps(repo_stars)},
                        backgroundColor: 'rgba(255, 193, 7, 0.8)',
                        borderColor: 'rgba(255, 193, 7, 1)',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Forks',
                        data: {json.dumps(repo_forks)},
                        backgroundColor: 'rgba(76, 175, 80, 0.8)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Repository Popularity (Stars & Forks)',
                        font: {{
                            size: 16
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }},
                    x: {{
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 45,
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // 리포지토리 타입 차트
        const repoTypeCtx = document.getElementById('repoTypeChart');
        new Chart(repoTypeCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(repo_type_labels)},
                datasets: [{{
                    data: {json.dumps(repo_type_data)},
                    backgroundColor: ['#3498db', '#e74c3c'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    title: {{
                        display: true,
                        text: 'Public vs Private Repositories',
                        font: {{
                            size: 16
                        }}
                    }}
                }}
            }}
        }});
        
        // 활동성 차트
        const activityCtx = document.getElementById('activityChart');
        new Chart(activityCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(activity_labels)},
                datasets: [{{
                    label: 'Repositories',
                    data: {json.dumps(activity_data)},
                    backgroundColor: [
                        'rgba(46, 204, 113, 0.8)',
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(149, 165, 166, 0.8)'
                    ],
                    borderColor: [
                        'rgba(46, 204, 113, 1)',
                        'rgba(52, 152, 219, 1)',
                        'rgba(149, 165, 166, 1)'
                    ],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    title: {{
                        display: true,
                        text: 'Repository Activity Status',
                        font: {{
                            size: 16
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Export 기능
        function exportAsImage() {{
            const element = document.getElementById('reportContent');
            html2canvas(element, {{
                scale: 2,
                backgroundColor: '#ffffff'
            }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '{username}_analysis.png';
                link.href = canvas.toDataURL();
                link.click();
            }});
        }}
        
        function exportTable() {{
            const element = document.getElementById('tableContainer');
            html2canvas(element, {{
                scale: 2,
                backgroundColor: '#ffffff'
            }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '{username}_table.png';
                link.href = canvas.toDataURL();
                link.click();
            }});
        }}
    </script>
</body>
</html>
'''
    
    # 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file
