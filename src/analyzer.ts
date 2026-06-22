export interface RepoInfo {
  name: string;
  full_name: string;
  url: string;
  description: string;
  private: boolean;
  fork: boolean;
  stars: number;
  watchers: number;
  forks: number;
  open_issues: number;
  size: number;
  language: string;
  languages: { [lang: string]: number };
  created_at: string;
  updated_at: string;
  pushed_at: string;
  created_date: string | null;
  updated_date: string | null;
  pushed_date: string | null;
  license: string | null;
  default_branch: string;
  commit_count: number;
}

export interface ScraperStats {
  total_repositories: number;
  public_repositories: number;
  private_repositories: number;
  total_commits: number;
  total_stars: number;
  total_watchers: number;
  total_forks: number;
  total_open_issues: number;
  total_size_kb: number;
  total_size_mb: number;
  avg_commits_per_repo: number;
  avg_stars_per_repo: number;
  avg_forks_per_repo: number;
  language_distribution: { [lang: string]: number };
  language_repo_count: { [lang: string]: number };
  total_languages: number;
  primary_language: string;
  recently_updated_count: number;
  active_repos_count: number;
  inactive_repos_count: number;
  license_distribution: { [lic: string]: number };
  analysis_date: string;
}

export interface AnalysisResult {
  username: string;
  repo_type: string;
  repositories: RepoInfo[];
  statistics?: ScraperStats;
  error?: string;
}

export async function analyzeProfile(
  username: string,
  token: string = "",
  repoType: string = "all",
  progressCallback?: (current: number, total: number, repoName: string) => void
): Promise<AnalysisResult> {
  const headers: HeadersInit = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
  };

  if (token && token.trim()) {
    headers["Authorization"] = `Bearer ${token.trim()}`;
  }

  async function apiFetch(url: string): Promise<Response> {
    const response = await fetch(url, { headers });
    if (response.status === 401) {
      throw new Error("Invalid GitHub Token (401 Unauthorized)");
    } else if (response.status === 403) {
      throw new Error("API rate limit exceeded or forbidden (403)");
    } else if (response.status === 404) {
      throw new Error("Resource not found (404)");
    } else if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return response;
  }

  // 1. Determine if fetching authenticated user repos
  let isAuthUser = false;
  if (token && token.trim()) {
    try {
      const userRes = await apiFetch("https://api.github.com/user");
      const userData = await userRes.json();
      if (userData?.login?.toLowerCase() === username.toLowerCase()) {
        isAuthUser = true;
      }
    } catch (e) {
      // Fallback
    }
  }

  const baseReposUrl = isAuthUser
    ? "https://api.github.com/user/repos?per_page=100"
    : `https://api.github.com/users/${username}/repos?per_page=100`;

  // 2. Fetch all repositories (handling pagination)
  const repos: any[] = [];
  let page = 1;
  while (true) {
    const url = `${baseReposUrl}&page=${page}`;
    try {
      const res = await apiFetch(url);
      const pageRepos = await res.json();
      if (!Array.isArray(pageRepos) || pageRepos.length === 0) {
        break;
      }
      repos.push(...pageRepos);
      if (pageRepos.length < 100) {
        break;
      }
      page++;
    } catch (e: any) {
      if (page === 1) {
        throw new Error(`Failed to fetch repositories: ${e.message || e}`);
      }
      break;
    }
  }

  // 3. Filter repositories (ignore forks, match repoType)
  const filteredRepos = repos.filter((r) => {
    if (r.fork) return false;
    const isPrivate = r.private || false;
    if (repoType === "public" && isPrivate) return false;
    if (repoType === "private" && !isPrivate) return false;
    return true;
  });

  if (filteredRepos.length === 0) {
    return {
      username,
      repo_type: repoType,
      error: "No repositories found matching criteria.",
      repositories: []
    };
  }

  // 4. Analyze each repository
  const reposData: RepoInfo[] = [];
  const totalReposCount = filteredRepos.length;

  for (let idx = 0; idx < totalReposCount; idx++) {
    const r = filteredRepos[idx];
    const repoName = r.name;
    const ownerLogin = r.owner?.login || username;

    if (progressCallback) {
      try {
        progressCallback(idx + 1, totalReposCount, repoName);
      } catch (e) {
        // ignore callback exceptions
      }
    }

    // Fetch commit count
    let commitCount = 0;
    try {
      const commitsUrl = `https://api.github.com/repos/${ownerLogin}/${repoName}/commits?per_page=1`;
      const cRes = await apiFetch(commitsUrl);
      const linkHeader = cRes.headers.get("Link") || cRes.headers.get("link");
      if (linkHeader) {
        const parts = linkHeader.split(",");
        for (const p of parts) {
          if (p.includes('rel="last"')) {
            const match = p.match(/[?&]page=(\d+)/);
            if (match) {
              commitCount = parseInt(match[1], 10);
              break;
            }
          }
        }
      }
      if (commitCount === 0) {
        const cData = await cRes.json();
        if (Array.isArray(cData)) {
          commitCount = cData.length;
        }
      }
    } catch (e) {
      commitCount = 0;
    }

    // Fetch languages
    let languages: { [lang: string]: number } = {};
    try {
      const langUrl = r.languages_url;
      if (langUrl) {
        const lRes = await apiFetch(langUrl);
        languages = await lRes.json();
      }
    } catch (e) {
      // ignore language exceptions
    }

    // Parse date helper
    const parseDate = (dateStr: string | null): string | null => {
      if (!dateStr) return null;
      return dateStr.replace("Z", "").split("T")[0];
    };

    reposData.push({
      name: repoName,
      full_name: r.full_name,
      url: r.html_url,
      description: r.description || "No description",
      private: r.private || false,
      fork: false,
      stars: r.stargazers_count || 0,
      watchers: r.watchers_count || 0,
      forks: r.forks_count || 0,
      open_issues: r.open_issues_count || 0,
      size: r.size || 0, // KB
      language: r.language || "N/A",
      languages,
      created_at: r.created_at,
      updated_at: r.updated_at,
      pushed_at: r.pushed_at,
      created_date: parseDate(r.created_at),
      updated_date: parseDate(r.updated_at),
      pushed_date: parseDate(r.pushed_at),
      license: r.license?.name || null,
      default_branch: r.default_branch || "main",
      commit_count: commitCount
    });
  }

  // 5. Generate statistics
  const totalCommits = reposData.reduce((acc, r) => acc + r.commit_count, 0);
  const totalStars = reposData.reduce((acc, r) => acc + r.stars, 0);
  const totalWatchers = reposData.reduce((acc, r) => acc + r.watchers, 0);
  const totalForks = reposData.reduce((acc, r) => acc + r.forks, 0);
  const totalIssues = reposData.reduce((acc, r) => acc + r.open_issues, 0);
  const totalSize = reposData.reduce((acc, r) => acc + r.size, 0);

  const publicReposCount = reposData.filter((r) => !r.private).length;
  const privateReposCount = reposData.filter((r) => r.private).length;

  const languageStats: { [lang: string]: number } = {};
  const languageRepoCount: { [lang: string]: number } = {};

  reposData.forEach((repo) => {
    Object.entries(repo.languages).forEach(([lang, bytes]) => {
      languageStats[lang] = (languageStats[lang] || 0) + bytes;
      languageRepoCount[lang] = (languageRepoCount[lang] || 0) + 1;
    });
  });

  const sortedLanguages = Object.entries(languageStats).sort((a, b) => b[1] - a[1]);

  // Calculate update recency
  let recentlyUpdatedCount = 0;
  let activeReposCount = 0;
  const now = new Date();

  reposData.forEach((repo) => {
    if (repo.updated_at) {
      try {
        const dt = new Date(repo.updated_at);
        const diffTime = Math.abs(now.getTime() - dt.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (diffDays <= 30) {
          recentlyUpdatedCount++;
        }
        if (diffDays <= 90) {
          activeReposCount++;
        }
      } catch (e) {
        // ignore
      }
    }
  });

  const licenseDistribution: { [lic: string]: number } = {};
  reposData.forEach((repo) => {
    const lic = repo.license || "No License";
    licenseDistribution[lic] = (licenseDistribution[lic] || 0) + 1;
  });

  const formatDateTime = (d: Date): string => {
    const pad = (n: number) => n.toString().padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  };

  const stats: ScraperStats = {
    total_repositories: reposData.length,
    public_repositories: publicReposCount,
    private_repositories: privateReposCount,
    total_commits: totalCommits,
    total_stars: totalStars,
    total_watchers: totalWatchers,
    total_forks: totalForks,
    total_open_issues: totalIssues,
    total_size_kb: totalSize,
    total_size_mb: parseFloat((totalSize / 1024).toFixed(2)),
    avg_commits_per_repo: parseFloat((totalCommits / reposData.length).toFixed(2)),
    avg_stars_per_repo: parseFloat((totalStars / reposData.length).toFixed(2)),
    avg_forks_per_repo: parseFloat((totalForks / reposData.length).toFixed(2)),
    language_distribution: Object.fromEntries(sortedLanguages),
    language_repo_count: Object.fromEntries(
      Object.entries(languageRepoCount).sort((a, b) => b[1] - a[1])
    ),
    total_languages: Object.keys(languageStats).length,
    primary_language: sortedLanguages.length > 0 ? sortedLanguages[0][0] : "N/A",
    recently_updated_count: recentlyUpdatedCount,
    active_repos_count: activeReposCount,
    inactive_repos_count: reposData.length - activeReposCount,
    license_distribution: licenseDistribution,
    analysis_date: formatDateTime(now)
  };

  return {
    username,
    repo_type: repoType,
    repositories: reposData,
    statistics: stats
  };
}
