This rule enforces best practices for performance optimization in Rust code.

## Rule Details

- **Pattern**: `*.rs`
- **Severity**: Warning
- **Category**: Performance

## Checks

1. **Memory Management**
   - Use stack allocation when possible
   - Avoid unnecessary heap allocations
   - Use appropriate collection types (e.g., `Vec` vs `LinkedList`)
   - Implement proper memory reuse

2. **Zero-Cost Abstractions**
   - Leverage compile-time optimizations
   - Use generics for zero-cost abstractions
   - Avoid runtime overhead in hot paths
   - Use const generics where appropriate

3. **Iterator Usage**
   - Use iterator combinators instead of loops
   - Chain iterator operations efficiently
   - Avoid collecting into intermediate collections
   - Use appropriate iterator adapters

4. **Benchmarking**
   - Use `criterion` for benchmarking
   - Profile code with `perf` or `flamegraph`
   - Measure before optimizing
   - Track performance regressions

## Examples

### Good
```rust
// Efficient iterator usage
let sum: i32 = numbers
    .iter()
    .filter(|&x| x > &0)
    .map(|x| x * x)
    .sum();

// Zero-cost abstraction
fn process<T: AsRef<str>>(input: T) {
    // Generic function with no runtime overhead
    let s = input.as_ref();
}

// Efficient memory usage
struct EfficientBuffer {
    data: Vec<u8>,
    capacity: usize,
}

impl EfficientBuffer {
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            data: Vec::with_capacity(capacity),
            capacity,
        }
    }

    pub fn reuse(&mut self) {
        // Reuse the buffer instead of reallocating
        self.data.clear();
    }
}
```

### Bad
```rust
// Inefficient memory usage
let mut vec = Vec::new();
for i in 0..1000 {
    vec.push(i.to_string()); // Unnecessary heap allocations
}

// Inefficient iterator usage
let result: Vec<_> = numbers
    .iter()
    .filter(|&x| x > &0)
    .collect(); // Unnecessary intermediate collection
let sum: i32 = result.iter().sum();

// Runtime overhead in hot path
fn process_dynamic(input: &dyn AsRef<str>) {
    // Dynamic dispatch in hot path
    let s = input.as_ref();
}
```

## Rationale

Performance optimization practices ensure:
- Efficient resource utilization
- Minimal runtime overhead
- Scalable applications
- Better user experience

## References

- [Rust Performance Book](https:/nnethercote.github.io/perf-book)
- [Criterion Documentation](https:/docs.rs/criterion/latest/criterion)
- [Rust Iterator Documentation](https:/doc.rust-lang.org/std/iter/trait.Iterator.html) 