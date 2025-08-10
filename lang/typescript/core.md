## TypeScript Development Standards

### Type System Configuration
- **Always enable `"strict": true`** in tsconfig.json - this is non-negotiable
- Enable additional strict checks: `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitReturns`
- **Never use `any`** - use `unknown` for truly unknown types and narrow them with type guards
- Add **explicit return types** for all public API functions and methods
- Prefer **type inference** for local variables where TypeScript can infer correctly
- Use **discriminated unions** with literal type discriminators for complex state management
- Apply **const assertions** (`as const`) for literal values that shouldn't change
- Enable **`verbatimModuleSyntax`: true** to preserve import/export syntax exactly as written and avoid interop pitfalls
- For libraries, enable **`isolatedDeclarations`: true** (with `declaration` or `composite`) to force explicit exported types and unlock fast `.d.ts` generation
- Prefer **`moduleDetection`: "force"** so every file is a module; avoid implicit script files
- Consider **`noUncheckedSideEffectImports`: true** to surface accidental side-effect-only imports (requires TS ≥ 5.9)

### Code Organization
- Place **one logical component per file** - avoid mixing unrelated exports
- Create dedicated `types.ts` files for shared type definitions
- Use **named exports** exclusively - avoid default exports for better refactoring
- Never export types or functions unless needed by other modules
- Organize imports: external libraries first, then internal modules, then types
- Use **barrel exports** (index.ts) sparingly - they can hurt tree-shaking

### Naming Conventions
- Use **PascalCase** for type names, interfaces, and enums
- Use **single-letter uppercase** for simple generic type parameters (`T`, `K`, `V`); use **descriptive PascalCase** for complex ones (e.g., `TItem`, `TResult`)
- Use **camelCase** for functions, methods, properties, and variables
- Use **CONSTANT_CASE** for true constants (not const variables)
- **Never prefix interfaces with `I`** - this is outdated Hungarian notation
- **Never use `_` prefix** for private properties - use TypeScript's `private` keyword
- Use descriptive names with auxiliary verbs (e.g., `isValid`, `hasData`, `canExecute`)

### Type Design Principles
- **Design types from usage** - write the consuming code first, then define types
- Use **branded types** for domain primitives that shouldn't be interchangeable
- Implement **Result<T, E>** types for operations that can fail instead of throwing
- Define **exhaustive switch statements** with `never` type for completeness checking
- Create **type predicates** (`is` functions) for runtime type narrowing
- Use **template literal types** for string patterns and validation

### Error Handling and Validation
- **Type all boundaries** - user input, API responses, file I/O, database queries
- Use **Zod or similar** for runtime validation at system boundaries
- Create **custom error classes** extending Error with typed properties
- Implement **type guards** with proper type predicates for narrowing
- Handle **null/undefined explicitly** - never assume values exist
- Use **assertion functions** (`asserts` keyword) for invariant checking

### Generic Type Best Practices
- **Constrain generic parameters** with extends clauses for type safety
- Provide **sensible defaults** for generic parameters when possible
- Use **conditional types** sparingly - they impact compilation performance
- Be mindful of **variance**; prefer separate input/output type parameters when needed. TypeScript does not support declaration-site `in`/`out` variance.
- Prefer **generic functions over generic classes** when state isn't needed

### Module and Import Patterns
- Use **type-only imports** (`import type`) for types to improve bundling and eliminate unintended side effects
- Enable **`isolatedModules`** for better compatibility with build tools
- Avoid **circular dependencies** - they cause maintenance nightmares
- Use **project references** for monorepo structures
- Configure **path aliases** in tsconfig.json for cleaner imports
- Enable **`verbatimModuleSyntax`: true** to preserve import/export syntax and ensure correct elision
- Prefer **explicit file extensions** in ESM when targeting Node (`"module"`: `nodenext`/`node18`) to match Node resolution rules
- Prefer **named exports**; avoid default exports for libraries (interop, tree-shaking, and API clarity)
- Prefer **explicit re-exports** over `export *` to keep public APIs intentional and tree-shakable
- Enforce **consistent type imports/exports** in linting to keep type-only traffic out of runtime bundles

### Performance Optimization
- **Interfaces vs type aliases**: use interfaces for object shapes you plan to extend/augment; use type aliases for unions, intersections, conditional/mapped and function types. Performance is comparable in modern TS.
- **Name complex types** instead of inlining them (improves caching)
- Avoid **deeply nested type operations** that exponentially increase complexity
- Use **`readonly` arrays and tuples** to prevent accidental mutations
- Enable **incremental compilation** for faster rebuilds

### Async and Promise Handling
- Always use **`async/await`** over raw promises for readability
- Type **async functions explicitly** with Promise<T> return types
- Handle **promise rejections** - unhandled rejections crash Node.js
- Use **`Promise.allSettled()`** when you need all results regardless of failures
- Implement **async error boundaries** with proper error types
- **No floating promises**: either `await` or explicitly `void` them after handling errors
- Use **AbortController** (or equivalent) for cancellable async operations

### Testing Practices
- Write **tests with full type checking** - no `@ts-ignore` in tests
- Test **type behavior** using type-level testing utilities
- Create **type-safe test fixtures** with proper interfaces
- Use **type-safe mocking libraries** that respect interfaces
- Ensure **test coverage includes edge cases** for type guards
- Consider **type assertion tests** with tools like `tsd` or `expectTypeOf`
- For libraries, add **publish-time checks** like `are-the-types-wrong` and `publint` to validate exports/types across environments

### Configuration Standards
- Required tsconfig.json settings:
  - `"strict": true`
  - `"noUncheckedIndexedAccess": true`
  - `"noImplicitReturns": true`
  - `"noFallthroughCasesInSwitch": true`
  - `"noImplicitOverride": true`
  - `"forceConsistentCasingInFileNames": true`
  - `"skipLibCheck": true`
  - `"esModuleInterop": true`
  - `"verbatimModuleSyntax": true`
  - `"useUnknownInCatchVariables": true`
  - `"noPropertyAccessFromIndexSignature": true`
  - Prefer `"moduleResolution": "bundler"` for app projects using modern bundlers; use `"node18"/"nodenext"` for Node runtime checks and library builds

### Code Quality Rules
- **No implicit any** - all parameters must have types
- **No non-null assertions (`!`)** without runtime validation
- **No type assertions (`as`)** except when narrowing from `unknown`
- **No `@ts-ignore`** or `@ts-expect-error` without documented justification
- **No namespace declarations** - use ES modules instead
- **Avoid `enum`**; prefer union types with const objects (`as const`). If interop requires runtime enums, prefer string enums. Avoid `const enum` unless you fully control compilation and emit.
- Keep **type-only imports/exports** type-qualified to prevent side effects in isolated transpilers

### Documentation Requirements
- Document **complex type logic** with comments explaining the "why"
- Add **JSDoc comments** for public APIs with examples
- Include **type parameter descriptions** in generic functions
- Document **invariants and preconditions** for functions
- Explain **non-obvious type narrowing** with inline comments

### Advanced TypeScript Features
- Use **mapped types** for transforming existing types
- Apply **utility types** (`Partial`, `Required`, `Pick`, `Omit`, `Record`)
- Leverage **conditional types** for type-level programming (use judiciously)
- Implement **variadic tuple types** for flexible function signatures
- Prefer **discriminated unions with exhaustive `switch`** for pattern matching semantics
- Use the **`satisfies`** operator to validate object literal shapes without widening
- Use **const type parameters** to preserve literal inference in generic APIs
- Prefer **standard decorators (TS ≥ 5)** over legacy `experimentalDecorators`; avoid `emitDecoratorMetadata` in libraries

### Security Considerations
- **Never trust external data** - validate all inputs at runtime
- Use **readonly modifiers** to prevent unintended mutations
- Apply **principle of least privilege** to type permissions
- Validate **environment variables** with typed schemas
- Implement **secure defaults** in type definitions

### Debugging and Development
- Enable **source maps** for debugging TypeScript in production
- Use **declaration maps** for "Go to Definition" in libraries
- Configure **watch mode** for development with incremental builds
- Enable **strict null checks** to catch common runtime errors
- Use **type checking in CI/CD** pipelines

### Building & Publishing Libraries (2025 baseline)
- **Default to ESM-only** when possible. Node 18+ and modern bundlers handle ESM natively; interop from CJS is increasingly supported. If you must support both, ship a dual package intentionally (see below).
- For dual packages, use an **`exports` map** with explicit conditions and type entries:
  - Provide `"import"` → ESM (`.mjs`) and `"require"` → CJS (`.cjs`/`.js`)
  - Provide `"types"` under each condition: `d.mts` for ESM and `d.ts` for CJS
  - Prefer **subpath exports** for multiple entry points (e.g., `"./orders"`)
- Prefer **named exports** and **explicit re-exports**; avoid `export *` and default exports in libraries
- tsconfig for libraries (baseline):
  - `"module": "node18"` (or `"nodenext"`), `"target": "es2020"`
  - `"verbatimModuleSyntax": true`, `"declaration": true`, `"declarationMap": true`, `"sourceMap": true`
  - `"isolatedDeclarations": true` (with `"declaration"` or `"composite"`)
- Ensure **extensionful ESM imports** in emitted code when targeting Node (e.g., `./utils.js`) to satisfy Node resolution
- If supporting older TS consumers, consider **`typesVersions`** and/or **downleveling `.d.ts`** (e.g., `downlevel-dts`), keeping your main types modern
- Validate packages before publishing with **arethetypeswrong** and **publint**; add these to release scripts
- Use a modern, zero-config library bundler when needed (**tsup**, **unbuild**, **tsdown**); do not bundle `.d.ts` manually unless the tool supports it or you provide proper `typesVersions`
- Prefer **explicit public API surfaces** (index files with named re-exports) to aid tree-shaking and avoid accidental surface area

### Linting (2025)
- Use **typescript-eslint v8** with flat config. Enable rules like `consistent-type-imports/exports` and disable rules that conflict with Prettier.
- Treat `no-floating-promises`, `no-misused-promises`, and type safety rules as **errors** in libraries; allow scoped overrides for tests/examples.

### Key Anti-Patterns to Avoid
- Using `any` type anywhere in production code
- Disabling strict mode or type checking
- Excessive type assertions that bypass safety
- Complex inheritance hierarchies over composition
- Mutable shared state without proper typing
- Circular module dependencies
- Global type augmentation without clear need
- Over-engineering with excessive abstraction
- Ignoring compiler warnings
- Missing error boundaries at system edges