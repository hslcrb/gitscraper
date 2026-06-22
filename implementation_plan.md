# Goal: Support Dark Mode and Auto-detected Multi-language (Ko, Ja, Zh-CN, Zh-TW, Ru, Es, En)

We will implement automatic Dark Mode support using CSS custom properties combined with the `@media (prefers-color-scheme: dark)` media query, and client-side localization (i18n) for Korean, Japanese, Chinese (Simplified), Chinese (Traditional), Russian, and Spanish based on browser/system language preferences. There will be no toggles or UI selectors; theme and language will be entirely auto-detected.

## Proposed Changes

### Configuration & Theme

#### [MODIFY] [index.css](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/index.css)
- Define a full dark theme palette inside `@media (prefers-color-scheme: dark)`.
- Replace hardcoded color references (such as `#ffffff`, `#f6f8fa`, and text colors) in the styles with semantic CSS custom properties to ensure seamless dark mode transitions.
- Adapt the `.logo-container` green background tint and the `.logo-icon` CSS filter drop-shadow to look beautiful on dark background.

#### [MODIFY] [index.html](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/index.html)
- Wrap plain text nodes in `<span>` tags with `data-i18n` attributes to avoid destroying SVG icons when translating.
- Add `data-i18n` placeholder attributes or update inputs to use `data-i18n` attributes.

#### [NEW] [i18n.js](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/i18n.js)
- Define a dictionary of UI translations for:
  - `en` (English - default)
  - `ko` (Korean)
  - `ja` (Japanese)
  - `zh` (Chinese - Simplified)
  - `zh-TW` (Chinese - Traditional/Taiwan)
  - `ru` (Russian)
  - `es` (Spanish)
- Export the translations and translation helper methods.

#### [MODIFY] [main.js](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/main.js)
- Import translations from `i18n.js`.
- Detect system language at page load and apply translations dynamically.
- Update dynamic UI text (alerts, loader status steps, table badges) using translated keys.
- Detect system dark mode preferences dynamically in JavaScript to apply correct theme colors (grid lines, legends, text) for Chart.js.
- Add a media query listener `window.matchMedia('(prefers-color-scheme: dark)')` to dynamically re-render the charts if the user changes their system color scheme.

---

## Translation Catalog Details

Below is the list of keys we will define in `src/i18n.js`:
- `meta_title`: Page title
- `header_title`: Logo title
- `header_subtitle`: Logo subtitle
- `badge_wasm`: WASM badge
- `github_username`: Username label
- `username_placeholder`: Input placeholder
- `repo_scope`: Repository Scope label
- `scope_all`: Scope All Option card
- `scope_public`: Scope Public Option card
- `scope_private`: Scope Private Option card
- `token_label`: GITHUB_TOKEN label
- `token_placeholder`: Token placeholder
- `btn_submit`: Start analysis button
- `security_title`: Security notice title
- `security_desc`: Security notice description
- `status_title`: Overlay status title
- `status_init`: Overlay status description
- `step_load_pyodide`: Step 1 text
- `step_init_python`: Step 2 text
- `step_fetch_repos`: Step 3 text
- `step_analyze`: Step 4 text
- `btn_export_json`: Export JSON
- `btn_save_pdf`: Save PDF
- `btn_analyze_another`: Analyze another profile
- `stat_repos`: Repositories count label
- `stat_commits`: Total commits label
- `stat_stars`: Total stars label
- `stat_forks`: Total forks label
- `stat_lang`: Primary language label
- `stat_size`: Code size label
- `chart_lang_title`: Language chart card title
- `chart_commits_title`: Commits chart card title
- `chart_popularity_title`: Popularity chart card title
- `chart_visibility_title`: Visibility chart card title
- `table_title`: Repository list table title
- `table_search_placeholder`: Table search input placeholder
- `table_col_repo`: Table repo column header
- `table_col_scope`: Table scope column header
- `table_col_commits`: Table commits column header
- `table_col_stars`: Table stars column header
- `table_col_forks`: Table forks column header
- `table_col_lang`: Table language column header
- `table_col_updated`: Table updated column header
- `footer_text`: Footer copyright text
- `alert_empty_username`: Username is required alert
- `default_bio`: Default bio text
- `scraping_progress`: Scraping: {repoName} ({current}/{total})
- `fetched_success`: Fetched repositories successfully
- `badge_private`: Badge for private scope
- `badge_public`: Badge for public scope
- `chart_label_commits`: Chart commits dataset label
- `chart_label_stars`: Chart stars dataset label
- `chart_label_forks`: Chart forks dataset label

---

## Verification Plan

### Automated Verification
- Verify code compiles and passes tests:
  ```bash
  venv/bin/python test_basic.py
  npm run build
  ```

### Manual Verification
- Test language detection by mocking `navigator.language` or setting browser language settings.
- Test dark mode detection by toggling system/browser dark mode and checking if CSS styles and Chart.js colors change automatically.
- Check build production files in `dist-web`.
