# Step 8: The React frontend

- **Frontend / backend:** the backend (FastAPI) holds the data and the rules. The frontend (React) is what runs in the browser and what the coach clicks on. They talk over HTTP, just like the tests' `client.get(...)`.
- **Origin:** scheme + host + port, like `http://localhost:5173`. A different port counts as a different origin.
- **CORS:** browsers block a page from calling an API on a different origin unless the API says "this origin is allowed". `CORSMiddleware` in `main.py` says that for the React app only.
- **Preflight:** before some requests, the browser first sends an `OPTIONS` request to ask permission. `tests/test_cors.py` sends one.
- **Vite:** the dev tool that serves the React app and reloads the page the moment you save a file.
- **npm / `package.json` / `node_modules`:** the JavaScript versions of uv / `pyproject.toml` / `.venv`. `package-lock.json` is like `uv.lock`.
- **TypeScript:** JavaScript with types, like Python type hints. The `Drill` type in `api.ts` copies `DrillRead`, so a typo like `drill.nmae` is caught before you run anything.
- **Component:** a function that returns what to show (`DrillLibrary`, `NewDrillForm`). You use it like an HTML tag: `<DrillLibrary />`.
- **JSX:** the HTML-looking code inside components. `{drill.name}` puts a value in; `{error && <p>...</p>}` shows something only if `error` is set.
- **Props:** inputs passed to a component, like function arguments: `<NewDrillForm onCreated={reload} />`.
- **State (`useState`):** a value React remembers between redraws. Calling the setter (`setSearch`) redraws the component with the new value.
- **Controlled input:** `value={search}` plus `onChange={(e) => setSearch(e.target.value)}`. The input always shows what's in state.
- **Effect (`useEffect`):** "run this after drawing, and again whenever these values change". We use it to load drills when `search` or `includeArchived` changes.
- **`async` / `await` / Promise:** a network call takes time. `await` waits for the answer without freezing the page.
- **`key`:** `<li key={drill.id}>` tells React which list item is which, so it updates the right one.

My notes:
