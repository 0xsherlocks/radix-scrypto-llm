# Token Creation Blueprint Template

Complete example of creating and managing tokens in Scrypto.

## Blueprint Code

```rust
use scrypto::prelude::*;

#[blueprint]
mod token_creator {
    struct TokenCreator {
        /// Vault to store created tokens
        token_vault: Vault,
        /// Resource address of the created token
        token_resource: ResourceAddress,
    }
    
    impl TokenCreator {
        /// Creates a new token with specified supply
        pub fn create_token(
            name: String,
            symbol: String,
            initial_supply: Decimal,
        ) -> Global<TokenCreator> {
            // Create a new token resource
            let token_bucket = ResourceBuilder::new_fungible(OwnerRole::None)
                .metadata(metadata!(
                    init {
                        "name" => name, locked;
                        "symbol" => symbol, locked;
                    }
                ))
                .mint_initial_supply(initial_supply);
            
            // Store the token resource address
            let token_resource = token_bucket.resource_address();
            
            // Create component with the tokens
            Self {
                token_vault: Vault::with_bucket(token_bucket),
                token_resource,
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize()
        }
        
        /// Returns the token resource address
        pub fn get_token_address(&self) -> ResourceAddress {
            self.token_resource
        }
        
        /// Returns current token balance in vault
        pub fn get_balance(&self) -> Decimal {
            self.token_vault.amount()
        }
        
        /// Withdraws tokens from the vault
        pub fn withdraw_tokens(&mut self, amount: Decimal) -> Bucket {
            self.token_vault.take(amount)
        }
        
        /// Deposits tokens into the vault
        pub fn deposit_tokens(&mut self, tokens: Bucket) {
            self.token_vault.put(tokens);
        }
    }
}
```

## Key Token Patterns

1. **ResourceBuilder**: Use `ResourceBuilder::new_fungible()`
2. **Metadata**: Set name, symbol, and other metadata
3. **Initial Supply**: Use `mint_initial_supply()` for initial tokens
4. **Vault Management**: Store tokens in `Vault`
5. **Bucket Operations**: Use `take()` and `put()` for transfers
