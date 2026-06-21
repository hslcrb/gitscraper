import json
from datetime import datetime
from collections import defaultdict

async def analyze_profile_wasm(username, token=None, repo_type="all", progress_callback=None):
    from pyodide.http import pyfetch
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token and token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
        
    async def api_fetch(url):
        response = await pyfetch(url, headers=headers)
        if response.status == 401:
            raise Exception("Invalid GitHub Token (401 Unauthorized)")
        elif response.status == 403:
            raise Exception("API rate limit exceeded or forbidden (403)")
        elif response.status == 404:
            raise Exception("Resource not found (404)")
        elif response.status != 200:
            raise Exception(f"HTTP error {response.status}")
        return response

    # 1. Determine base user details and endpoint
    # Check if we should fetch authenticated user repos
    is_auth_user = False
    if token and token.strip():
        try:
            user_res = await api_fetch("https://api.github.com/user")
            user_data = await user_res.json()
            if user_data.get("login", "").lower() == username.lower():
                is_auth_user = True
        except Exception as e:
            # Fallback to public fetch if /user fails
            pass

    repos_url = "https://api.github.com/user/repos?per_page=100" if is_auth_user else f"https://api.github.com/users/{username}/repos?per_page=100"
    
    # 2. Fetch all repositories (handling pagination)
    repos = []
    page = 1
    while True:
        url = f"{repos_url}&page={page}"
        try:
            res = await api_fetch(url)
            page_repos = await res.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            if len(page_repos) < 100:
                break
            page += 1
        except Exception as e:
            if page == 1:
                raise Exception(f"Failed to fetch repositories: {str(e)}")
            break

    # 3. Filter repositories (ignore forks, match repo_type)
    filtered_repos = []
    for r in repos:
        # Exclude forks
        if r.get("fork", False):
            continue
            
        is_private = r.get("private", False)
        if repo_type == "public" and is_private:
            continue
        elif repo_type == "private" and not is_private:
            continue
            
        filtered_repos.append(r)

    if not filtered_repos:
        return {
            "username": username,
            "repo_type": repo_type,
            "error": "No repositories found matching criteria.",
            "repositories": [],
            "statistics": {}
        }

    # 4. Analyze each repository
    repos_data = []
    total_repos_count = len(filtered_repos)
    
    for idx, r in enumerate(filtered_repos, 1):
        repo_name = r.get("name")
        owner_login = r.get("owner", {}).get("login", username)
        
        if progress_callback:
            try:
                progress_callback(idx, total_repos_count, repo_name)
            except Exception:
                pass
                
        # Fetch commit count
        commit_count = 0
        try:
            commits_url = f"https://api.github.com/repos/{owner_login}/{repo_name}/commits?per_page=1"
            c_res = await api_fetch(commits_url)
            # Check Link header for paging
            link_header = c_res.headers.get("Link") or c_res.headers.get("link")
            if link_header:
                # E.g. <...page=123>; rel="last"
                parts = link_header.split(",")
                for p in parts:
                    if 'rel="last"' in p:
                        # Extract page number
                        import re
                        match = re.search(r"[?&]page=(\d+)", p)
                        if match:
                            commit_count = int(match.group(1))
                            break
            if commit_count == 0:
                c_data = await c_res.json()
                commit_count = len(c_data)
        except Exception:
            commit_count = 0

        # Fetch languages
        languages = {}
        try:
            lang_url = r.get("languages_url")
            if lang_url:
                l_res = await api_fetch(lang_url)
                languages = await l_res.json()
        except Exception:
            pass

        # Parse date strings
        def parse_date(date_str):
            if not date_str:
                return None
            return date_str.replace("Z", "").split("T")[0]

        created_date = parse_date(r.get("created_at"))
        updated_date = parse_date(r.get("updated_at"))
        pushed_date = parse_date(r.get("pushed_at"))

        repo_info = {
            "name": repo_name,
            "full_name": r.get("full_name"),
            "url": r.get("html_url"),
            "description": r.get("description") or "No description",
            "private": r.get("private", False),
            "fork": False,
            "stars": r.get("stargazers_count", 0),
            "watchers": r.get("watchers_count", 0),
            "forks": r.get("forks_count", 0),
            "open_issues": r.get("open_issues_count", 0),
            "size": r.get("size", 0), # KB
            "language": r.get("language") or "N/A",
            "languages": languages,
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
            "pushed_at": r.get("pushed_at"),
            "created_date": created_date,
            "updated_date": updated_date,
            "pushed_date": pushed_date,
            "license": r.get("license", {}).get("name") if r.get("license") else None,
            "default_branch": r.get("default_branch", "main"),
            "commit_count": commit_count
        }
        repos_data.append(repo_info)

    # 5. Generate statistics
    total_commits = sum(repo["commit_count"] for repo in repos_data)
    total_stars = sum(repo["stars"] for repo in repos_data)
    total_watchers = sum(repo["watchers"] for repo in repos_data)
    total_forks = sum(repo["forks"] for repo in repos_data)
    total_issues = sum(repo["open_issues"] for repo in repos_data)
    total_size = sum(repo["size"] for repo in repos_data)
    
    public_repos_count = sum(1 for r in repos_data if not r["private"])
    private_repos_count = sum(1 for r in repos_data if r["private"])
    
    language_stats = defaultdict(int)
    language_repo_count = defaultdict(int)
    for repo in repos_data:
        for lang, bytes_count in repo["languages"].items():
            language_stats[lang] += bytes_count
            language_repo_count[lang] += 1
            
    sorted_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate update recency
    # In JS/WASM python, we parse iso format
    recently_updated_count = 0
    active_repos_count = 0
    now = datetime.now()
    
    for repo in repos_data:
        up_at = repo.get("updated_at")
        if up_at:
            try:
                # parse '2023-08-11T12:00:00Z'
                dt = datetime.fromisoformat(up_at.replace("Z", "+00:00"))
                days = (now.astimezone(dt.tzinfo) - dt).days
                if days <= 30:
                    recently_updated_count += 1
                if days <= 90:
                    active_repos_count += 1
            except Exception:
                pass

    licenses = defaultdict(int)
    for repo in repos_data:
        lic = repo.get("license") or "No License"
        licenses[lic] += 1

    stats = {
        "total_repositories": len(repos_data),
        "public_repositories": public_repos_count,
        "private_repositories": private_repos_count,
        "total_commits": total_commits,
        "total_stars": total_stars,
        "total_watchers": total_watchers,
        "total_forks": total_forks,
        "total_open_issues": total_issues,
        "total_size_kb": total_size,
        "total_size_mb": round(total_size / 1024, 2),
        "avg_commits_per_repo": round(total_commits / len(repos_data), 2) if repos_data else 0,
        "avg_stars_per_repo": round(total_stars / len(repos_data), 2) if repos_data else 0,
        "avg_forks_per_repo": round(total_forks / len(repos_data), 2) if repos_data else 0,
        "language_distribution": dict(sorted_languages),
        "language_repo_count": dict(sorted(language_repo_count.items(), key=lambda x: x[1], reverse=True)),
        "total_languages": len(language_stats),
        "primary_language": sorted_languages[0][0] if sorted_languages else "N/A",
        "recently_updated_count": recently_updated_count,
        "active_repos_count": active_repos_count,
        "inactive_repos_count": len(repos_data) - active_repos_count,
        "license_distribution": dict(licenses),
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = {
        "username": username,
        "repo_type": repo_type,
        "repositories": repos_data,
        "statistics": stats
    }
    
    return json.dumps(result)
