# SvelteKit 5 Development Standards

## Core Principles
- **Always use SvelteKit 5 syntax** - No legacy Svelte 4 patterns
- **TypeScript is mandatory** - Never write untyped JavaScript
- **Use runes for all reactivity** - `$state`, `$derived`, `$effect`, `$props`, `$bindable`
- **Skeleton UI by default** - Use Skeleton components and design system
- **Mobile-first responsive** - Design for mobile, enhance for desktop
- **File-based routing** - Follow SvelteKit's routing conventions
- **Server-first approach** - Leverage SSR and load functions
- **Validate all inputs** - Use Zod for schema validation
- **Semantic HTML** - Use proper HTML5 elements and ARIA attributes

## Project Structure
- `src/lib/components/` - Reusable components organized by feature
- `src/lib/stores/` - Global state management with runes
- `src/lib/types/` - TypeScript type definitions and interfaces
- `src/lib/utils/` - Utility functions and helpers
- `src/lib/services/` - API clients and external integrations
- `src/lib/server/` - Server-only utilities (database, auth)
- `src/routes/` - File-based routing with layout groups
- `src/routes/api/` - API endpoints with `+server.ts`
- `tests/unit/` - Unit tests with Vitest
- `tests/e2e/` - End-to-end tests with Playwright

## Naming Conventions
- **Components** - PascalCase files (`UserProfile.svelte`)
- **Routes** - kebab-case directories (`user-settings/`)
- **Utilities** - camelCase functions (`formatDate()`)
- **Types** - PascalCase interfaces (`interface UserData`)
- **Stores** - camelCase exports (`export const userStore`)
- **Constants** - UPPER_SNAKE_CASE (`MAX_RETRIES`)

## SvelteKit 5 Runes
- Use `$state()` for reactive state declarations
- Use `$derived()` for computed values (side-effect free)
- Use `$effect()` for side effects and lifecycle management
- Use `$props()` with TypeScript interfaces for component props
- Use `$bindable()` for two-way binding props
- Never use old reactive syntax (`$:`, `export let`)
- Always destructure props: `let { title, count = 0 } = $props<Props>()`
- Keep `$effect` usage minimal - prefer declarative patterns

## TypeScript Patterns
- Define interfaces for all component props
- Use strict TypeScript configuration (`strict: true`)
- Leverage `PageLoad` and `PageServerLoad` types
- Use Zod for runtime validation with type inference
- Define API response types explicitly
- Use type guards for runtime type checking
- Prefer `unknown` over `any` for untyped data
- Use utility types (`Partial`, `Pick`, `Omit`) effectively

## Component Architecture
- Single responsibility - one component, one purpose
- Composition over inheritance
- Props down, events up pattern
- Use slots and snippets for content projection
- Colocate component styles using `<style lang="postcss">`
- Include accessibility attributes by default
- Test components in isolation

## State Management
- Use runes-based class stores for global state
- Context API for component tree state
- URL state for shareable application state
- Form state with `enhance` and validation
- Avoid prop drilling - use context or stores
- Keep state as close to usage as possible
- Derive state instead of syncing

## Routing Best Practices
- Use layout groups `(app)` for shared layouts
- Implement `+page.server.ts` for server-side logic
- Use `+layout.ts` for shared data fetching
- Handle errors with `+error.svelte`
- Prerender static pages with `export const prerender = true`
- Use form actions for mutations
- Implement proper loading states with `$navigating`

## Skeleton UI Integration
- Configure theme in `tailwind.config.ts`
- Use Skeleton components over custom implementations
- Apply theme with `data-theme` attribute
- Use Skeleton's responsive utilities
- Leverage built-in dark mode support
- Use Skeleton's form components with validation
- Apply consistent spacing with theme tokens

## Responsive Design
- Mobile-first breakpoints: `sm:`, `md:`, `lg:`, `xl:`
- Use CSS Grid and Flexbox for layouts
- Responsive typography with clamp() or breakpoint classes
- Touch-friendly tap targets (min 44x44px)
- Viewport meta tag configured properly
- Test on actual devices, not just browser DevTools
- Use container queries where appropriate

## Performance Optimization
- Lazy load heavy components with dynamic imports
- Use `loading="lazy"` for images below the fold
- Implement virtual scrolling for long lists
- Preload critical data with `preloadData()`
- Use appropriate rendering strategies (SSR/CSR/SSG)
- Optimize bundle size with code splitting
- Minimize client-side JavaScript
- Use WebP/AVIF for images

## Security Practices
- Validate all user inputs server-side
- Use CSRF protection (built-in with SvelteKit)
- Sanitize HTML content with DOMPurify
- Secure cookies with httpOnly and secure flags
- Implement proper authentication flows
- Use environment variables for secrets
- Never expose sensitive data in client code
- Parameterize database queries

## Testing Strategy
- Unit test utilities and business logic
- Component test with Testing Library
- E2E test critical user flows
- Mock external dependencies
- Test accessibility with automated tools
- Maintain high test coverage (>80%)
- Run tests in CI/CD pipeline

## API Design
- RESTful endpoints in `routes/api/`
- Type-safe API clients with generics
- Consistent error response format
- Use proper HTTP status codes
- Implement rate limiting
- Version APIs when needed
- Document with OpenAPI/Swagger

## Form Handling
- Use form actions for server-side processing
- Client-side validation with Zod schemas
- Progressive enhancement with `use:enhance`
- Display field-level errors clearly
- Implement proper loading states
- Handle network errors gracefully
- Preserve form data on errors

## Error Handling
- Use `error()` helper for throwing HTTP errors
- Implement `+error.svelte` pages
- Log errors with structured logging
- Display user-friendly error messages
- Implement retry logic for transient failures
- Use try-catch blocks in async functions
- Handle edge cases explicitly

## Development Workflow
- Use `npm run dev` for development
- Run `npm run check` before committing
- Format with Prettier on save
- Lint with ESLint configured for Svelte
- Use conventional commits
- Document complex logic with comments
- Keep PRs focused and small

## Build & Deployment
- Build with `npm run build`
- Preview with `npm run preview`
- Use adapter-auto for platform detection
- Configure CSP headers properly
- Enable compression (gzip/brotli)
- Set appropriate cache headers
- Monitor Core Web Vitals
- Use CDN for static assets

## Key Dependencies
- **@sveltejs/kit** - Framework
- **typescript** - Type safety
- **@skeletonlabs/skeleton-svelte** - UI components
- **tailwindcss** - Utility-first CSS
- **zod** - Schema validation
- **vitest** - Unit testing
- **@playwright/test** - E2E testing
- **@sveltejs/adapter-auto** - Deployment adapter

## Common Patterns

### Load Function Pattern
```typescript
export const load: PageLoad = async ({ fetch, params }) => {
  const data = await fetch(`/api/resource/${params.id}`);
  return { resource: await data.json() };
};
```

### Form Action Pattern
```typescript
export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    // Validate and process
    return { success: true };
  }
};
```

### Global State Pattern
```typescript
class AppState {
  user = $state<User | null>(null);
  theme = $state<'light' | 'dark'>('light');
}
export const appState = new AppState();
```

### Component Props Pattern
```typescript
interface Props {
  title: string;
  items: Item[];
}
let { title, items } = $props<Props>();
```

## Environment Variables
- Use `$env/dynamic/private` for server-only secrets
- Use `$env/dynamic/public` for client-safe values
- Prefix public vars with `PUBLIC_`
- Validate env vars at startup
- Use `.env.example` for documentation
- Never commit `.env` files

## Accessibility Requirements
- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus management in SPAs
- Color contrast ratios (WCAG AA)
- Screen reader announcements
- Skip navigation links
- Alt text for images

## Performance Metrics
- Target Core Web Vitals:
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- Bundle size < 200KB (gzipped)
- Time to Interactive < 3s
- Lighthouse score > 90