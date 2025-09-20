# Common Scrypto Patterns Reference

Essential patterns and best practices for Scrypto development.

## 1. Blueprint Structure Pattern

```rust
use scrypto::prelude::*;

#[blueprint]
mod my_blueprint {
    struct MyStruct {
        // State variables
    }
    
    impl MyStruct {
        // Methods
    }
}
```

## 2. Component Instantiation Pattern

```rust
pub fn instantiate_component() -> Global<MyStruct> {
    Self {
        // Initialize fields
    }
    .instantiate()
    .prepare_to_globalize(OwnerRole::None)
    .globalize()
}
```

## 3. Resource Creation Pattern

```rust
// Fungible Token
let token = ResourceBuilder::new_fungible(OwnerRole::None)
    .metadata(metadata!(init { "name" => "My Token", locked; }))
    .mint_initial_supply(1000);

// NFT
let nft_resource = ResourceBuilder::new_integer_non_fungible::<u64>(OwnerRole::None)
    .metadata(metadata!(init { "name" => "My NFT", locked; }))
    .create_with_no_initial_supply();
```

## 4. Vault Management Pattern

```rust
struct MyComponent {
    vault: Vault,
}

impl MyComponent {
    pub fn deposit(&mut self, bucket: Bucket) {
        self.vault.put(bucket);
    }
    
    pub fn withdraw(&mut self, amount: Decimal) -> Bucket {
        self.vault.take(amount)
    }
}
```

## 5. Access Control Pattern

```rust
struct MyComponent {
    admin_badge: Vault,
}

impl MyComponent {
    pub fn admin_only_method(&mut self) {
        self.admin_badge.authorize(|| {
            // Admin-only logic here
        });
    }
}
```

## 6. Proof Validation Pattern

```rust
pub fn user_method(&self, user_proof: Proof) -> String {
    user_proof.validate_proof(
        ProofValidationMode::ValidateResourceAddress(self.user_badge_resource)
    ).expect("Invalid proof");
    
    // Method logic here
}
```

## 7. Error Handling Pattern

```rust
pub fn safe_method(&mut self) -> Result<String, String> {
    if self.some_condition() {
        Ok("Success".to_string())
    } else {
        Err("Failed condition".to_string())
    }
}
```

## 8. Event Emission Pattern

```rust
#[event]
struct MyEvent {
    message: String,
    value: Decimal,
}

impl MyComponent {
    pub fn emit_event(&self) {
        Runtime::emit_event(MyEvent {
            message: "Something happened".to_string(),
            value: dec!("100"),
        });
    }
}
```

## Common Imports

```rust
use scrypto::prelude::*;
```

This single import provides access to all commonly used Scrypto types and macros.

## Best Practices

1. **Always use `#[blueprint]` attribute** for blueprint modules
2. **Initialize components with `.instantiate().globalize()`** pattern
3. **Use Vaults for storing resources** within components
4. **Validate proofs** for access-controlled methods
5. **Handle errors gracefully** with Result types
6. **Use metadata** to make resources discoverable
7. **Follow naming conventions** for clarity
