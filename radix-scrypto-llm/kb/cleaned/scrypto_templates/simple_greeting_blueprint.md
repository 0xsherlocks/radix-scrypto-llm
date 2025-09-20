# Simple Greeting Blueprint Template

This is a working example of a simple Scrypto blueprint that stores and retrieves a greeting message.

## Blueprint Code

```rust
use scrypto::prelude::*;

#[blueprint]
mod greeting {
    struct Greeting {
        message: String,
    }
    
    impl Greeting {
        /// Creates a new greeting component with the given message
        pub fn instantiate_greeting(message: String) -> Global<Greeting> {
            Self {
                message,
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize()
        }
        
        /// Returns the stored greeting message
        pub fn get_greeting(&self) -> String {
            self.message.clone()
        }
        
        /// Updates the greeting message
        pub fn set_greeting(&mut self, new_message: String) {
            self.message = new_message;
        }
    }
}
```

## Key Patterns

1. **Blueprint Declaration**: Use `#[blueprint]` attribute
2. **Module Structure**: Wrap in `mod` block
3. **Struct Definition**: Simple struct with data fields
4. **Implementation Block**: `impl` block with methods
5. **Instantiation**: Use `.instantiate()` and `.globalize()` pattern
6. **Method Types**: `&self` for read, `&mut self` for write

## Usage Example

```rust
// Instantiate the component
let greeting_component = Greeting::instantiate_greeting("Hello, Radix!".to_string());

// Get the greeting
let message = greeting_component.get_greeting();

// Update the greeting
greeting_component.set_greeting("Hello, World!".to_string());
```
