# IntelliERP frontend

React + TypeScript + Vite client for IntelliERP. See the [project README](../README.md) for
scope, credentials and the roadmap.

```bash
npm install
npm run dev         # http://localhost:5173 (the backend must be running on :8000)
npm run build       # type-check and production build
```

The API base URL comes from `VITE_API_BASE_URL` (see `.env.example`) and defaults to
`http://localhost:8000/api/v1`.

## Routes

`/login`, `/dashboard`, `/sales`, `/sales/:id`, `/inventory`, `/inventory/:id`, `/procurement`,
`/procurement/:id`, `/suppliers`, `/suppliers/:id`, `/products`, `/products/:id`, `/analytics`,
`/analytics/products/:id`, `/approvals`,
`/audit-logs`, `/ai-assistant`, `/settings` (`/profile` redirects to `/settings`).

## Conventions

- Components never call Axios directly. They use `src/services/*Service.ts`, which share the client in
  `src/services/api.ts` (adds the token, signs the user out on a 401).
- Data loading goes through the `useApi` hook and the `QueryBoundary` component, which render the
  loading and error states; `DataTable` renders the empty state and pagination.
- Types in `src/types/` mirror the backend schemas in `Backend/app/schemas/`. Update both together.
- Permissions come from the backend (`/auth/me`). `hasPermission` and `RequirePermission` only tailor
  the UI; the API is what enforces access.
- The AI Assistant page is the only AI-generated content; it shows which data each answer used.
  Analytics pages and dashboard risk alerts come from fixed rules, not from the model.
