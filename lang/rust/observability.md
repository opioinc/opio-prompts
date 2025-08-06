This rule enforces best practices for logging, tracing, and metrics in Rust applications.

## Rule Details

- **Pattern**: `*.rs`
- **Severity**: Warning
- **Category**: Observability

## Checks

1. **Structured Logging**
   - Use `tracing` instead of `log`
   - Include contextual information
   - Use appropriate log levels
   - Add structured fields to events

2. **Span Usage**
   - Create spans for significant operations
   - Use `#[instrument]` for function tracing
   - Record important events within spans
   - Use span relationships appropriately

3. **Metrics Collection**
   - Use `metrics` crate for metrics
   - Record meaningful metrics
   - Use appropriate metric types
   - Include relevant labels

4. **Error Tracking**
   - Record errors with context
   - Use error spans for debugging
   - Include error details in events
   - Track error frequencies

## Examples

### Good
```rust
use tracing::{info, error, instrument, Level};
use metrics::{counter, gauge};

#[instrument(level = Level::INFO, skip(input))]
pub async fn process_data(input: &[u8]) -> Result<(), Error> {
    // Record metric for input size
    gauge!("data.input.size", input.len() as f64);
    
    // Create a span for the processing operation
    let span = tracing::info_span!("processing_data");
    let _guard = span.enter();
    
    // Record structured event
    info!(
        input_size = input.len(),
        "Starting data processing"
    );
    
    match process(input).await {
        Ok(result) => {
            // Record success metric
            counter!("data.process.success", 1);
            info!(
                result_size = result.len(),
                "Data processing completed"
            );
            Ok(())
        }
        Err(e) => {
            // Record error metric
            counter!("data.process.error", 1);
            error!(
                error = %e,
                error_type = std::any::type_name_of_val(&e),
                "Data processing failed"
            );
            Err(e)
        }
    }
}

/// A service that uses tracing for observability
#[derive(Debug)]
pub struct Service {
    name: String,
}

impl Service {
    #[instrument(level = Level::DEBUG)]
    pub fn new(name: String) -> Self {
        info!(name = %name, "Creating new service");
        Self { name }
    }

    #[instrument(level = Level::INFO, skip(self))]
    pub async fn handle_request(&self, request: Request) -> Result<Response, Error> {
        // Record request metric
        counter!("service.requests", 1, "service" => self.name.clone());
        
        let span = tracing::info_span!(
            "handle_request",
            service = %self.name,
            request_id = %request.id
        );
        
        let _guard = span.enter();
        
        info!(
            method = %request.method,
            path = %request.path,
            "Processing request"
        );
        
        // Implementation
    }
}
```

### Bad
```rust
// Bad: Using println! instead of structured logging
fn process_data(data: &[u8]) {
    println!("Processing data of size {}", data.len());
}

// Bad: Missing context in error logging
fn handle_error(e: Error) {
    error!("Error occurred: {}", e);
}

// Bad: Not using spans for operation tracking
async fn process_request(req: Request) -> Result<Response, Error> {
    // No span tracking
    let result = process(req).await;
    // No metrics
    result
}
```

## Rationale

Proper observability practices ensure:
- Effective debugging and troubleshooting
- Performance monitoring
- Error tracking and analysis
- System health monitoring

## References

- [tracing Documentation](https:/docs.rs/tracing/latest/tracing)
- [metrics Documentation](https:/docs.rs/metrics/latest/metrics)
- [OpenTelemetry Rust](https:/opentelemetry.io/docs/instrumentation/rust) 