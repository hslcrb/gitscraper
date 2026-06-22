# Goal: Migrate WASM (Pyodide) Scraper to TypeScript, Add Responsive Design, and selection styling

We will replace the browser-based Pyodide WASM Python analysis engine with a pure TypeScript implementation. The core scraping logic, pagination, commit headers parsing, language accumulation, and statistical aggregation will remain identical to the original CLI/Python model. Additionally, we will implement custom text selection styles and refine responsive layouts for screens ranging from small mobiles to high-resolution displays.

---

## User Review Required

> [!IMPORTANT]
> - Pyodide WASM CDNs will be removed from [index.html](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/index.html) as python in browser is no longer required.
> - The application will load faster and consume significantly less memory.
> - Typescript compilation will be configured in the project.

---

## Proposed Changes

### 1. Build & Dependencies

#### [MODIFY] [package.json](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/package.json)
- Add `"typescript": "^5.0.0"` and `"tsc"` compiler scripts to devDependencies.

#### [NEW] [tsconfig.json](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/tsconfig.json)
- Create a TypeScript configuration file to support ESM, target ESNext, and support Vite paths.

---

### 2. Frontend Structure

#### [MODIFY] [index.html](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/index.html)
- Remove Pyodide script tag: `<script src="https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js"></script>`.
- Change entry point script from `src/main.js` to `src/main.ts`.
- Retain the progress step list, but adapt translation keys to match TypeScript connections.

---

### 3. Localization (i18n)

#### [MODIFY] [i18n.js](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/i18n.js) (Rename to [i18n.ts](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/i18n.ts))
- Rename to TypeScript.
- Update loading step translation strings across all languages to reflect TypeScript-native initialization rather than Pyodide/Python.
  - `step_load_pyodide` -> e.g. "Initializing API Connection..." / "API 연결 초기화 중..."
  - `step_init_python` -> e.g. "Preparing profile metadata..." / "프로필 메타데이터 준비 중..."
  - `step_analyze` -> e.g. "Running statistical engine..." / "통계 분석 엔진 실행 중..."

---

### 4. Logic & Scraper Engine

#### [NEW] [analyzer.ts](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/analyzer.ts)
- Implement `analyzeProfile` function in TypeScript replicating `wasm_analyzer.py` exactly.
- Fetch user details, handle pagination, parse commits using the HTTP `Link` header, gather language bytes, and produce the identical statistics JSON payload.

#### [MODIFY] [main.js](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/main.js) (Rename to [main.ts](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/main.ts))
- Import `analyzeProfile` from `./analyzer.ts` instead of loading Pyodide.
- Remove pyodide load/Python code registration.
- Maintain form submission, progress bars, chart rendering, table loading, search filter, and print/export features.

---

### 5. Styling & Responsiveness

#### [MODIFY] [index.css](file:///home/rheehoselenovo2/개발프로젝트/gitscraper/src/index.css)
- Implement theme-aligned selection highlighting:
  ```css
  ::selection {
    background: var(--accent-green-light);
  }
  ```
- Refine container layouts, grid gap values, table layouts, and chart dimensions with flexible max/min bounds to optimize responsive styling across device breakpoints (from 320px mobile to ultra-wide desktop monitors).

---

## Verification Plan

### Automated Verification
- Verify Vite production build:
  ```bash
  npm run build
  ```
- Run Python unit tests:
  ```bash
  venv/bin/python test_basic.py
  ```

### Manual Verification
- Verify the analyzer runs smoothly and fetches repos in the browser.
- Verify selection highlights match the light/dark green tint and keep text colors readable.
- Test resizing the window to verify layout responsiveness.
