# Svelte 5 + SvelteKit Library Standards (SOTA)

This guidance is for building reusable Svelte libraries (components, utilities, runes/stores) that work across modern SvelteKit apps. It assumes Svelte 5 and current SvelteKit tooling.

## Core principles
- **ESM-only**: publish ESM, no CommonJS. Do not bundle `svelte` or SvelteKit.
- **Svelte 5 first**: write components and helpers with runes. Keep APIs simple and stable.
- **SSR-safe by default**: no unconditional `window`/`document`/`localStorage`; avoid leaking state across requests.
- **Type-safe**: ship `.d.ts` declarations for everything. Keep runtime and type contracts aligned.
- **Zero (or declared) side effects**: enable tree-shaking; declare CSS as side-effectful.
- **Accessible**: semantic markup, ARIA where needed, keyboard-first behavior.

## Project structure
- `src/lib/` is your public surface. Everything else is tooling/tests/docs.
- Prefer small, focused entry points rather than a giant index when appropriate (see Exports).
- Keep internal helpers private (not exported from `src/lib`).

## Packaging with SvelteKit
- Use `@sveltejs/package` and the `svelte-package` CLI. Author in `src/lib`, output to `dist`.
- Do not publish SvelteKit routes; use them only for local docs/sandboxes.
- Keep relative imports fully specified with extensions. In TypeScript, import `.ts` files with a `.js` extension.

```json
// package.json (key library fields)
{
  "name": "your-library",
  "type": "module",
  "files": [
    "dist",
    "!dist/**/*.test.*",
    "!dist/**/*.spec.*"
  ],
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "svelte": "./dist/index.js"
    }
  },
  "svelte": "./dist/index.js",
  "sideEffects": ["**/*.css"],
  "peerDependencies": {
    "svelte": "^5.0.0"
  }
}
```

- If you expose many components, consider subpath exports for direct imports and faster builds:

```json
{
  "exports": {
    ".": { "types": "./dist/index.d.ts", "svelte": "./dist/index.js" },
    "./Button.svelte": { "types": "./dist/Button.svelte.d.ts", "svelte": "./dist/Button.svelte" },
    "./Modal.svelte":  { "types": "./dist/Modal.svelte.d.ts",  "svelte": "./dist/Modal.svelte" }
  }
}
```

TypeScript resolution for subpath types:
- Prefer consumers using `"moduleResolution": "bundler"` (TS ≥ 5). Alternatively support older setups with `typesVersions` mapping.

```json
{
  "typesVersions": {
    ">4.0": {
      "Button.svelte": ["./dist/Button.svelte.d.ts"],
      "Modal.svelte":  ["./dist/Modal.svelte.d.ts"],
      "index.d.ts":    ["./dist/index.d.ts"]
    }
  }
}
```

Optional: publish declaration maps for better “Go to definition” by adding `"declarationMap": true` and including `src/lib` in `files`, excluding tests.

## Svelte 5 runes in libraries
- You can use runes in `.svelte` and `.svelte.ts` sources. Prefer object `$state` shapes for shareability and fewer pitfalls.
- Avoid forcing consumers to adopt specific global state patterns. Keep state local to components unless you explicitly export helpers.
- Do not depend on `$app/*` modules; prefer generic primitives, or take values (like current URL) via props/parameters.

## SSR and browser safety
- Never touch browser globals on import. Guard with `BROWSER` from `esm-env` or `browser` from `$app/environment`, and use `onMount` for DOM work.
- Avoid global singletons that hold mutable state. If you must share state, prefer per-tree Context patterns initialized by a parent.
- Do not rely on SvelteKit-specific runtime in library code. If you provide server-only helpers, document them clearly and isolate them in separate modules.

## Styling guidance
- Prefer component-scoped styles. Avoid global resets or un-namespaced globals.
- If shipping global CSS, keep it opt-in and namespaced; declare CSS side effects in `package.json`.
- Avoid compiling external CSS frameworks into your package. Let consumers choose their styling system.

## Accessibility (always)
- Keyboard operability, focus management and ARIA roles where applicable.
- Respect reduced motion and color contrast. Provide sensible defaults with overrides via props/slots.

## Testing
- Unit/component tests with Vitest + `@testing-library/svelte` on `jsdom`.
- Add the Svelte Testing Vite plugin for better ergonomics.

```ts
// vite.config.ts (library dev/tests)
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { svelteTesting } from '@testing-library/svelte/vite';

export default defineConfig({
  plugins: [svelte(), svelteTesting()],
  test: { environment: 'jsdom' }
});
```

- Run `svelte-check`, type checks and `publint` in CI to catch packaging issues before publish.

## Versioning, CI, and release
- Follow SemVer. Removing exports or changing export conditions is breaking.
- Keep `svelte` as a peer dependency; do not pin it as a dependency.
- Provide `package` and `publish` scripts. For scoped packages, publish with `--access public`.

```json
{
  "scripts": {
    "build": "svelte-package",
    "package": "svelte-package",
    "prepublishOnly": "npm run package && npm run test && npm run typecheck"
  }
}
```

## Common pitfalls to avoid
- Importing from `$app/*` or SvelteKit-only modules in distributed code.
- Accessing `window`/`document` at module top level (will crash SSR).
- Shipping un-declared side effects (breaks tree-shaking).
- Bundling `svelte` or bundling consumer dependencies.
- Missing file extensions in relative imports.

## Minimal consumer expectations
- Consumers import components either from the root or subpaths.
- Consumers should not need extra preprocessors beyond Svelte defaults.
- Library must work in SSR and CSR contexts without code changes.

## Checklist (before publish)
- `@sveltejs/package` build to `dist` is green; types emitted.
- `exports` and `svelte` fields resolve correctly; subpaths (if any) tested.
- `sideEffects` lists CSS; no unintended side effects.
- `peerDependencies` includes `svelte` (and only what’s truly peer).
- Tests pass in `jsdom`; `svelte-check` and `publint` are clean.
- README documents install, usage, SSR caveats (if any), and subpath imports.