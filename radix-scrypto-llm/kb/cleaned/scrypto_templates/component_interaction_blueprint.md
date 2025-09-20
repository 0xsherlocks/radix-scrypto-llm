# Component Interaction Blueprint Template

Blueprint showing how components interact with each other.

## Blueprint Code

```rust
use scrypto::prelude::*;

#[blueprint]
mod component_caller {
    struct ComponentCaller {
        /// Reference to another component
        target_component: Global<AnyComponent>,
        /// Our local state
        call_count: u32,
    }
    
    impl ComponentCaller {
        /// Creates a new component caller
        pub fn new(target_address: ComponentAddress) -> Global<ComponentCaller> {
            Self {
                target_component: Global::from(target_address),
                call_count: 0,
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize()
        }
        
        /// Calls a method on the target component
        pub fn call_target_method(&mut self, method_name: String, args: Vec<String>) -> String {
            self.call_count += 1;
            
            // Example of calling another component's method
            // This would be replaced with actual method calls
            format!("Called {} with args {:?} (call #{})", method_name, args, self.call_count)
        }
        
        /// Gets the call count
        pub fn get_call_count(&self) -> u32 {
            self.call_count
        }
        
        /// Gets target component address
        pub fn get_target_address(&self) -> ComponentAddress {
            self.target_component.address()
        }
    }
}

// Helper blueprint for demonstration
#[blueprint]  
mod target_component {
    struct TargetComponent {
        data: String,
    }
    
    impl TargetComponent {
        /// Creates a target component
        pub fn new(initial_data: String) -> Global<TargetComponent> {
            Self {
                data: initial_data,
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize()
        }
        
        /// A method that can be called by other components
        pub fn process_data(&mut self, input: String) -> String {
            self.data = format!("{}-{}", self.data, input);
            self.data.clone()
        }
        
        /// Gets current data
        pub fn get_data(&self) -> String {
            self.data.clone()
        }
    }
}
```

## Key Component Interaction Patterns

1. **Component References**: Use `Global<AnyComponent>` or specific types
2. **Address Conversion**: Convert addresses to globals with `Global::from()`
3. **Method Calls**: Call methods directly on component references
4. **State Management**: Each component manages its own state
5. **Cross-Component Logic**: Coordinate operations across components
