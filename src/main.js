import wasmAnalyzerCode from './wasm_analyzer.py?raw';
import { getLanguage, translate } from './i18n.js';

// Global state
let analysisData = null;
let charts = {};
let pyodideInstance = null;
const currentLang = getLanguage();

// Translate all elements with data-i18n
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = translate(key, currentLang);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = text;
    } else {
      el.textContent = text;
    }
  });
  document.title = translate('meta_title', currentLang);
}
applyTranslations();

// Get theme colors for Chart.js based on current prefers-color-scheme
function getChartColors() {
  const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return {
    grid: isDark ? '#30363d' : '#e1e4e8',
    text: isDark ? '#c9d1d9' : '#24292f',
    textSecondary: isDark ? '#8b949e' : '#57606a',
    border: isDark ? '#161b22' : '#ffffff'
  };
}

// Initialize elements
const configPanel = document.getElementById('configPanel');
const statusPanel = document.getElementById('statusPanel');
const dashboard = document.getElementById('dashboard');
const form = document.getElementById('analyzerForm');
const tokenInput = document.getElementById('tokenInput');
const toggleTokenBtn = document.getElementById('toggleToken');

// Steps indicators
const stepLoadPyodide = document.getElementById('stepLoadPyodide');
const stepInitPython = document.getElementById('stepInitPython');
const stepFetchRepos = document.getElementById('stepFetchRepos');
const stepAnalyze = document.getElementById('stepAnalyze');

// Toggle token visibility
toggleTokenBtn.addEventListener('click', () => {
  const type = tokenInput.type === 'password' ? 'text' : 'password';
  tokenInput.type = type;
  toggleTokenBtn.innerHTML = type === 'password' 
    ? `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>`;
});

// Update steps UI helper
function setStepState(stepElement, state, text = null) {
  stepElement.className = `step-item ${state}`;
  const icon = stepElement.querySelector('.step-icon');
  
  if (text) {
    stepElement.querySelector('.step-text').textContent = text;
  }
  
  if (state === 'active') {
    icon.innerHTML = `<span class="spinner-outer" style="width: 14px; height: 14px; border-width: 2px; display: inline-block;"></span>`;
  } else if (state === 'completed') {
    icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 14px; height: 14px; color: var(--accent-green);"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>`;
  } else {
    icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 14px; height: 14px; color: var(--text-secondary);"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>`;
  }
}

// Main execution handler
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const usernameInput = document.getElementById('usernameInput').value.trim();
  let username = usernameInput;
  // Extract username if URL is pasted
  if (username.includes('github.com')) {
    username = username.replace(/\/$/, '').split('/').pop();
  }
  
  const token = tokenInput.value.trim();
  const repoType = document.querySelector('input[name="repo_type"]:checked').value;
  
  if (!username) {
    alert(translate('alert_empty_username', currentLang));
    return;
  }
  
  // Show loading panel
  configPanel.style.display = 'none';
  statusPanel.style.display = 'flex';
  dashboard.style.display = 'none';
  
  // Reset steps
  setStepState(stepLoadPyodide, 'active');
  setStepState(stepInitPython, 'pending');
  setStepState(stepFetchRepos, 'pending');
  setStepState(stepAnalyze, 'pending');
  
  const spinnerPercent = document.getElementById('spinnerPercent');
  spinnerPercent.textContent = '0%';
  
  try {
    // 1. Fetch user avatar/details from GitHub API directly (to show immediate preview)
    let avatarUrl = 'https://github.com/identicons/github.png';
    let userBio = translate('default_bio', currentLang);
    let userFullName = username;
    
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const uRes = await fetch(`https://api.github.com/users/${username}`, { headers });
      if (uRes.ok) {
        const uData = await uRes.json();
        avatarUrl = uData.avatar_url;
        userBio = uData.bio || translate('default_bio', currentLang);
        userFullName = uData.name || username;
      }
    } catch (e) {
      console.warn('Failed to fetch user preview avatar', e);
    }
    
    // Set preview details
    document.getElementById('userAvatar').src = avatarUrl;
    document.getElementById('userBio').textContent = userBio;
    document.getElementById('userFullName').textContent = userFullName;
    
    // 2. Load Pyodide WASM Runtime
    spinnerPercent.textContent = '10%';
    if (!pyodideInstance) {
      pyodideInstance = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/"
      });
    }
    
    setStepState(stepLoadPyodide, 'completed');
    setStepState(stepInitPython, 'active');
    spinnerPercent.textContent = '40%';
    
    // 3. Load and register Python code in Pyodide
    pyodideInstance.runPython(wasmAnalyzerCode);
    
    setStepState(stepInitPython, 'completed');
    setStepState(stepFetchRepos, 'active');
    spinnerPercent.textContent = '50%';
    
    // 4. Run Python Analysis with progress callback
    const progressCallback = (current, total, repoName) => {
      const pct = Math.min(50 + Math.floor((current / total) * 45), 95);
      spinnerPercent.textContent = `${pct}%`;
      const progressText = translate('scraping_progress', currentLang)
        .replace('{repoName}', repoName)
        .replace('{current}', current)
        .replace('{total}', total);
      setStepState(stepFetchRepos, 'active', progressText);
    };
    
    // Expose Javascript function to Pyodide
    pyodideInstance.registerJsModule("js_callbacks", { progressCallback });
    
    setStepState(stepAnalyze, 'active');
    
    // Prepare variables for run
    const pyExpression = `
import js_callbacks
import asyncio
from wasm_analyzer import analyze_profile_wasm

# Execute and get JSON string
json_res = asyncio.get_event_loop().run_until_complete(
    analyze_profile_wasm(
        "${username}", 
        "${token}", 
        "${repoType}", 
        js_callbacks.progressCallback
    )
)
json_res
`;
    
    const pyResultJsonStr = await pyodideInstance.runPythonAsync(pyExpression);
    analysisData = JSON.parse(pyResultJsonStr);
    
    if (analysisData.error) {
      throw new Error(analysisData.error);
    }
    
    // Completed successfully
    spinnerPercent.textContent = '100%';
    setStepState(stepFetchRepos, 'completed', translate('fetched_success', currentLang));
    setStepState(stepAnalyze, 'completed');
    
    // Render Dashboard
    renderDashboard(analysisData);
    
    // Display dashboard
    statusPanel.style.display = 'none';
    dashboard.style.display = 'block';
    
  } catch (err) {
    console.error(err);
    alert(`Error: ${err.message || err}`);
    // Return to config panel
    statusPanel.style.display = 'none';
    configPanel.style.display = 'block';
  }
});

// Render Dashboard Data
function renderDashboard(data) {
  const stats = data.statistics;
  
  // Set stats counters
  document.getElementById('statTotalRepos').textContent = stats.total_repositories;
  document.getElementById('statTotalCommits').textContent = Number(stats.total_commits).toLocaleString();
  document.getElementById('statTotalStars').textContent = Number(stats.total_stars).toLocaleString();
  document.getElementById('statTotalForks').textContent = Number(stats.total_forks).toLocaleString();
  document.getElementById('statPrimaryLang').textContent = stats.primary_language;
  document.getElementById('statCodeSize').textContent = `${stats.total_size_mb} MB`;
  
  // Render charts
  renderCharts(data);
  
  // Render table
  renderTable(data.repositories);
}

// Chart Rendering
function renderCharts(data) {
  const stats = data.statistics;
  const repos = data.repositories;
  
  // Destroy old charts if they exist
  Object.values(charts).forEach(chart => chart.destroy());
  charts = {};
  
  const colors = getChartColors();
  
  // 1. Language Distribution
  const langLabels = Object.keys(stats.language_distribution).slice(0, 10);
  const langData = Object.values(stats.language_distribution).slice(0, 10).map(bytes => (bytes / (1024 * 1024)).toFixed(2)); // MB
  
  const langCtx = document.getElementById('chartLanguage').getContext('2d');
  charts.language = new Chart(langCtx, {
    type: 'doughnut',
    data: {
      labels: langLabels,
      datasets: [{
        data: langData,
        backgroundColor: [
          '#2ea44f', '#0969da', '#1a7f37', '#54aeff', '#85ea9d', 
          '#ffe066', '#8c959f', '#d0d7de', '#afb8c1', '#24292f'
        ],
        borderWidth: 1,
        borderColor: colors.border
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { 
            color: colors.text, 
            font: { 
              family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' 
            } 
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => ` ${context.label}: ${context.raw} MB`
          }
        }
      }
    }
  });
  
  // 2. Commit Count per Repository (Top 10)
  const sortedRepos = [...repos].sort((a, b) => b.commit_count - a.commit_count).slice(0, 10);
  const repoNames = sortedRepos.map(r => r.name);
  const repoCommits = sortedRepos.map(r => r.commit_count);
  
  const commitsCtx = document.getElementById('chartCommits').getContext('2d');
  charts.commits = new Chart(commitsCtx, {
    type: 'bar',
    data: {
      labels: repoNames,
      datasets: [{
        label: translate('chart_label_commits', currentLang),
        data: repoCommits,
        backgroundColor: 'rgba(46, 164, 79, 0.7)',
        borderColor: '#2ea44f',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { 
          grid: { color: colors.grid }, 
          ticks: { 
            color: colors.textSecondary,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          } 
        },
        x: { 
          grid: { display: false }, 
          ticks: { 
            color: colors.textSecondary, 
            maxRotation: 45, 
            minRotation: 45,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          } 
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
  
  // 3. Stars and Forks (Top 10 by stars)
  const starSortedRepos = [...repos].sort((a, b) => b.stars - a.stars).slice(0, 10);
  const starRepoNames = starSortedRepos.map(r => r.name);
  const repoStars = starSortedRepos.map(r => r.stars);
  const repoForks = starSortedRepos.map(r => r.forks);
  
  const popularityCtx = document.getElementById('chartPopularity').getContext('2d');
  charts.popularity = new Chart(popularityCtx, {
    type: 'bar',
    data: {
      labels: starRepoNames,
      datasets: [
        {
          label: translate('chart_label_stars', currentLang),
          data: repoStars,
          backgroundColor: 'rgba(9, 105, 218, 0.7)',
          borderColor: '#0969da',
          borderWidth: 1
        },
        {
          label: translate('chart_label_forks', currentLang),
          data: repoForks,
          backgroundColor: 'rgba(46, 164, 79, 0.7)',
          borderColor: '#2ea44f',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { 
          grid: { color: colors.grid }, 
          ticks: { 
            color: colors.textSecondary,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          } 
        },
        x: { 
          grid: { display: false }, 
          ticks: { 
            color: colors.textSecondary, 
            maxRotation: 45, 
            minRotation: 45,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          } 
        }
      },
      plugins: {
        legend: { 
          labels: { 
            color: colors.text,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          } 
        }
      }
    }
  });
  
  // 4. Repo Type Distribution
  const typeCtx = document.getElementById('chartRepoType').getContext('2d');
  charts.repoType = new Chart(typeCtx, {
    type: 'doughnut',
    data: {
      labels: [translate('badge_public', currentLang), translate('badge_private', currentLang)],
      datasets: [{
        data: [stats.public_repositories, stats.private_repositories],
        backgroundColor: ['#2ea44f', '#cf222e'],
        borderWidth: 1,
        borderColor: colors.border
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { 
            color: colors.text,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif' }
          }
        }
      }
    }
  });
}

// Render Repository List Table
function renderTable(repositories) {
  const tbody = document.getElementById('repoTableBody');
  tbody.innerHTML = '';
  
  repositories.forEach(repo => {
    const tr = document.createElement('tr');
    
    const typeBadge = repo.private 
      ? `<span class="badge private">${translate('badge_private', currentLang)}</span>` 
      : `<span class="badge public">${translate('badge_public', currentLang)}</span>`;
      
    const langBadge = repo.language && repo.language !== 'N/A'
      ? `<span class="badge lang">${repo.language}</span>`
      : `<span class="badge" style="color: var(--text-secondary)">-</span>`;
      
    tr.innerHTML = `
      <td><a href="${repo.url}" target="_blank">${repo.name}</a></td>
      <td>${typeBadge}</td>
      <td style="font-weight: 600;">${repo.commit_count.toLocaleString()}</td>
      <td>${repo.stars.toLocaleString()}</td>
      <td>${repo.forks.toLocaleString()}</td>
      <td>${langBadge}</td>
      <td style="color: var(--text-secondary);">${repo.updated_date || 'N/A'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Search and filtering of repos table
document.getElementById('repoSearch').addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase().trim();
  if (!analysisData) return;
  
  const filtered = analysisData.repositories.filter(repo => {
    return repo.name.toLowerCase().includes(query) || 
           (repo.language && repo.language.toLowerCase().includes(query));
  });
  
  renderTable(filtered);
});

// Export features
document.getElementById('exportJson').addEventListener('click', () => {
  if (!analysisData) return;
  
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysisData, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `${analysisData.username}_analysis_wasm.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
});

document.getElementById('exportPdf').addEventListener('click', () => {
  window.print();
});

document.getElementById('resetBtn').addEventListener('click', () => {
  analysisData = null;
  dashboard.style.display = 'none';
  configPanel.style.display = 'block';
  form.reset();
});

// Watch prefers-color-scheme dynamically to update charts color schemes in real-time
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (analysisData) {
    renderCharts(analysisData);
  }
});
