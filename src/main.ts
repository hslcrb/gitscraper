import { getLanguage, translate } from './i18n.ts';
import * as Comlink from 'comlink';
import type { WorkerAPI } from './worker.ts';

declare let Chart: any;

// Global state
let analysisData: any = null;
let charts: { [key: string]: any } = {};

// Spawn Web Worker for offloading scraping computation
const worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
const api = Comlink.wrap<WorkerAPI>(worker);

// Initialize elements
const configPanel = document.getElementById('configPanel') as HTMLElement;
const statusPanel = document.getElementById('statusPanel') as HTMLElement;
const dashboard = document.getElementById('dashboard') as HTMLElement;
const form = document.getElementById('analyzerForm') as HTMLFormElement;
const tokenInput = document.getElementById('tokenInput') as HTMLInputElement;
const toggleTokenBtn = document.getElementById('toggleToken') as HTMLButtonElement;

// Steps indicators
const stepLoadPyodide = document.getElementById('stepLoadPyodide') as HTMLElement;
const stepInitPython = document.getElementById('stepInitPython') as HTMLElement;
const stepFetchRepos = document.getElementById('stepFetchRepos') as HTMLElement;
const stepAnalyze = document.getElementById('stepAnalyze') as HTMLElement;

const currentLang = getLanguage();

// Toggle token visibility
toggleTokenBtn.addEventListener('click', () => {
  const type = tokenInput.type === 'password' ? 'text' : 'password';
  tokenInput.type = type;
  toggleTokenBtn.innerHTML = type === 'password' 
    ? `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>`;
});

// Update steps UI helper
function setStepState(stepElement: HTMLElement, state: string, text: string | null = null) {
  stepElement.className = `step-item ${state}`;
  const icon = stepElement.querySelector('.step-icon') as HTMLElement;
  
  if (text) {
    const textEl = stepElement.querySelector('.step-text');
    if (textEl) textEl.textContent = text;
  }
  
  if (state === 'active') {
    icon.innerHTML = `<span class="spinner-outer" style="width: 14px; height: 14px; border-width: 2px; display: inline-block;"></span>`;
  } else if (state === 'completed') {
    icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 14px; height: 14px; color: var(--accent-green);"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>`;
  } else {
    icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 14px; height: 14px; color: var(--text-secondary);"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>`;
  }
}

// Translate all elements with data-i18n
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (!key) return;
    const text = translate(key, currentLang);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      (el as HTMLInputElement).placeholder = text;
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

// Main execution handler
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const usernameInput = (document.getElementById('usernameInput') as HTMLInputElement).value.trim();
  let username = usernameInput;
  if (username.includes('github.com')) {
    username = username.replace(/\/$/, '').split('/').pop() || '';
  }
  
  const token = tokenInput.value.trim();
  const checkedRadio = document.querySelector('input[name="repo_type"]:checked') as HTMLInputElement;
  const repoType = checkedRadio ? checkedRadio.value : 'all';
  
  if (!username) {
    alert(translate('alert_empty_username', currentLang));
    return;
  }
  
  configPanel.style.display = 'none';
  statusPanel.style.display = 'flex';
  dashboard.style.display = 'none';
  
  setStepState(stepLoadPyodide, 'active');
  setStepState(stepInitPython, 'pending');
  setStepState(stepFetchRepos, 'pending');
  setStepState(stepAnalyze, 'pending');
  
  const spinnerPercent = document.getElementById('spinnerPercent') as HTMLElement;
  spinnerPercent.textContent = '0%';
  
  let proxyCallback: any = null;
  try {
    let avatarUrl = 'https://github.com/identicons/github.png';
    let userBio = translate('default_bio', currentLang);
    let userFullName = username;
    
    try {
      const headers: HeadersInit = {};
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
    
    (document.getElementById('userAvatar') as HTMLImageElement).src = avatarUrl;
    (document.getElementById('userBio') as HTMLElement).textContent = userBio;
    (document.getElementById('userFullName') as HTMLElement).textContent = userFullName;
    
    spinnerPercent.textContent = '15%';
    setStepState(stepLoadPyodide, 'completed');
    
    spinnerPercent.textContent = '30%';
    setStepState(stepInitPython, 'completed');
    
    setStepState(stepFetchRepos, 'active');
    
    // Create Comlink proxy callback to allow progress tracking across Worker boundary
    proxyCallback = Comlink.proxy((current: number, total: number, repoName: string) => {
      const pct = Math.min(30 + Math.floor((current / total) * 65), 98);
      spinnerPercent.textContent = `${pct}%`;
      const progressText = translate('scraping_progress', currentLang)
        .replace('{repoName}', repoName)
        .replace('{current}', current.toString())
        .replace('{total}', total.toString());
      setStepState(stepFetchRepos, 'active', progressText);
    });

    setStepState(stepAnalyze, 'active');
    
    // Run analyzer inside Web Worker thread
    const result = await api.analyzeProfile(username, token, repoType, proxyCallback);
    analysisData = result;
    
    if (analysisData.error) {
      throw new Error(analysisData.error);
    }
    
    spinnerPercent.textContent = '100%';
    setStepState(stepFetchRepos, 'completed', translate('fetched_success', currentLang));
    setStepState(stepAnalyze, 'completed');
    
    renderDashboard(analysisData);
    
    statusPanel.style.display = 'none';
    dashboard.style.display = 'block';
    
  } catch (err: any) {
    console.error(err);
    alert(`Error: ${err.message || err}`);
    statusPanel.style.display = 'none';
    configPanel.style.display = 'block';
  } finally {
    // Release proxy memory reference to prevent leakage in Web Worker bridge
    if (proxyCallback) {
      proxyCallback[Comlink.releaseProxy]();
    }
  }
});

// Render Dashboard Data
function renderDashboard(data: any) {
  const stats = data.statistics;
  
  (document.getElementById('statTotalRepos') as HTMLElement).textContent = stats.total_repositories;
  (document.getElementById('statTotalCommits') as HTMLElement).textContent = Number(stats.total_commits).toLocaleString();
  (document.getElementById('statTotalStars') as HTMLElement).textContent = Number(stats.total_stars).toLocaleString();
  (document.getElementById('statTotalForks') as HTMLElement).textContent = Number(stats.total_forks).toLocaleString();
  (document.getElementById('statPrimaryLang') as HTMLElement).textContent = stats.primary_language;
  (document.getElementById('statCodeSize') as HTMLElement).textContent = `${stats.total_size_mb} MB`;
  
  renderCharts(data);
  renderTable(data.repositories);
}

// Chart Rendering with custom tooltips (adding 2 decimal percentage display)
function renderCharts(data: any) {
  const stats = data.statistics;
  const repos = data.repositories;
  
  Object.values(charts).forEach(chart => chart.destroy());
  charts = {};
  
  const colors = getChartColors();
  
  // 1. Language Distribution
  const langLabels = Object.keys(stats.language_distribution).slice(0, 10);
  const langData = Object.values(stats.language_distribution).slice(0, 10).map((bytes: any) => (bytes / (1024 * 1024)).toFixed(2)); // MB
  
  const langCtx = (document.getElementById('chartLanguage') as HTMLCanvasElement).getContext('2d');
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
            label: (context: any) => {
              const dataset = context.dataset;
              const total = dataset.data.reduce((acc: number, val: any) => acc + parseFloat(val), 0);
              const value = parseFloat(context.raw);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
              return ` ${context.label}: ${value} MB (${percentage}%)`;
            }
          }
        }
      }
    }
  });
  
  // 2. Commit Count per Repository (Top 10)
  const sortedRepos = [...repos].sort((a, b) => b.commit_count - a.commit_count).slice(0, 10);
  const repoNames = sortedRepos.map(r => r.name);
  const repoCommits = sortedRepos.map(r => r.commit_count);
  
  const commitsCtx = (document.getElementById('chartCommits') as HTMLCanvasElement).getContext('2d');
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
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const dataset = context.dataset;
              const total = dataset.data.reduce((acc: number, val: any) => acc + parseFloat(val), 0);
              const value = parseFloat(context.raw);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
              return ` ${context.label}: ${value} commits (${percentage}%)`;
            }
          }
        }
      }
    }
  });
  
  // 3. Stars and Forks (Top 10 by stars)
  const starSortedRepos = [...repos].sort((a, b) => b.stars - a.stars).slice(0, 10);
  const starRepoNames = starSortedRepos.map(r => r.name);
  const repoStars = starSortedRepos.map(r => r.stars);
  const repoForks = starSortedRepos.map(r => r.forks);
  
  const popularityCtx = (document.getElementById('chartPopularity') as HTMLCanvasElement).getContext('2d');
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
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const dataset = context.dataset;
              const total = dataset.data.reduce((acc: number, val: any) => acc + parseFloat(val), 0);
              const value = parseFloat(context.raw);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
              return ` ${context.dataset.label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
  
  // 4. Repo Type Distribution
  const typeCtx = (document.getElementById('chartRepoType') as HTMLCanvasElement).getContext('2d');
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
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const dataset = context.dataset;
              const total = dataset.data.reduce((acc: number, val: any) => acc + parseFloat(val), 0);
              const value = parseFloat(context.raw);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
              return ` ${context.label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// Render Repository List Table
function renderTable(repositories: any[]) {
  const tbody = document.getElementById('repoTableBody') as HTMLElement;
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
(document.getElementById('repoSearch') as HTMLInputElement).addEventListener('input', (e: Event) => {
  const query = (e.target as HTMLInputElement).value.toLowerCase().trim();
  if (!analysisData) return;
  
  const filtered = analysisData.repositories.filter((repo: any) => {
    return repo.name.toLowerCase().includes(query) || 
           (repo.language && repo.language.toLowerCase().includes(query));
  });
  
  renderTable(filtered);
});

// Export features
(document.getElementById('exportJson') as HTMLButtonElement).addEventListener('click', () => {
  if (!analysisData) return;
  
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysisData, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `${analysisData.username}_analysis_ts.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
});

(document.getElementById('exportPdf') as HTMLButtonElement).addEventListener('click', () => {
  window.print();
});

(document.getElementById('resetBtn') as HTMLButtonElement).addEventListener('click', () => {
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
