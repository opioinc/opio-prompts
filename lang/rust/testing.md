This rule enforces best practices for testing in Rust code.

## Rule Details

- **Pattern**: `*.rs`
- **Severity**: Error
- **Category**: Testing

## Checks

1. **Test Organization**
   - Place unit tests in the same file as the code being tested
   - Use integration tests for testing public APIs
   - Follow the AAA (Arrange-Act-Assert) pattern

2. **Test Coverage**
   - Test both success and error cases
   - Include edge cases and boundary conditions
   - Use property-based testing where appropriate

3. **Test Isolation**
   - Use test-specific types and mocks
   - Avoid shared mutable state between tests
   - Clean up resources after tests

4. **Async Testing**
   - Use `tokio::test` for async tests
   - Test cancellation scenarios
   - Use proper timeouts in async tests

## Examples

### Good
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_success_case() {
        // Arrange
        let input = "test";
        
        // Act
        let result = process(input);
        
        // Assert
        assert_eq!(result, expected);
    }

    #[tokio::test]
    async fn test_async_operation() {
        // Arrange
        let service = TestService::new();
        
        // Act
        let result = service.process().await;
        
        // Assert
        assert!(result.is_ok());
    }
}
```

### Bad
```rust
#[test]
fn test_with_shared_state() {
    // Bad: Using shared mutable state
    static mut COUNTER: i32 = 0;
    unsafe { COUNTER += 1; }
}

#[test]
fn test_without_cleanup() {
    // Bad: Not cleaning up resources
    let file = File::create("test.txt").unwrap();
    // No cleanup after test

    // avoid unwrap()
    let first_list = value1_lists.get(0).unwrap().i32()?;
    let second_list = value1_lists.get(1).unwrap().i32()?;

}

```

## Rationale

Proper testing practices ensure:
- Code reliability and correctness
- Easy maintenance and refactoring
- Clear documentation through examples
- Confidence in code changes

## References

- [Rust Book - Testing](https:/doc.rust-lang.org/book/ch11-00-testing.html)
- [Rust Testing Guide](https:/rust-lang.github.io/book/ch11-00-testing.html)
- [tokio-test Documentation](https:/docs.rs/tokio-test/latest/tokio_test) 