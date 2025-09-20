# Access Control Blueprint Template

Blueprint demonstrating badge-based access control patterns.

## Blueprint Code

```rust
use scrypto::prelude::*;

#[blueprint]
mod access_controlled {
    struct AccessControlled {
        /// Admin badge vault
        admin_badge: Vault,
        /// User badge resource
        user_badge_resource: ResourceAddress,
        /// Protected data
        protected_data: String,
        /// User count
        user_count: u32,
    }
    
    impl AccessControlled {
        /// Creates a new access-controlled component
        pub fn new(initial_data: String) -> (Global<AccessControlled>, Bucket) {
            // Create admin badge
            let admin_badge = ResourceBuilder::new_fungible(OwnerRole::None)
                .metadata(metadata!(
                    init {
                        "name" => "Admin Badge", locked;
                        "description" => "Badge for administrative access", locked;
                    }
                ))
                .mint_initial_supply(1);
            
            // Create user badge resource (initially no supply)
            let user_badge_resource = ResourceBuilder::new_fungible(OwnerRole::None)
                .metadata(metadata!(
                    init {
                        "name" => "User Badge", locked;
                        "description" => "Badge for user access", locked;
                    }
                ))
                .mint_roles(mint_roles!(
                    minter => rule!(require(admin_badge.resource_address()));
                    minter_updater => rule!(deny_all);
                ))
                .create_with_no_initial_supply();
            
            let component = Self {
                admin_badge: Vault::with_bucket(admin_badge.take(dec!("0.1"))),
                user_badge_resource,
                protected_data: initial_data,
                user_count: 0,
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize();
            
            (component, admin_badge)
        }
        
        /// Admin-only: Create user badges
        pub fn create_user_badge(&mut self) -> Bucket {
            self.admin_badge.authorize(|| {
                self.user_count += 1;
                borrow_resource_manager!(self.user_badge_resource).mint(1)
            })
        }
        
        /// Admin-only: Update protected data
        pub fn update_data(&mut self, new_data: String) {
            self.admin_badge.authorize(|| {
                self.protected_data = new_data;
            });
        }
        
        /// User access: Read protected data (requires user badge)
        pub fn read_data(&self, _user_badge: Proof) -> String {
            _user_badge.validate_proof(
                ProofValidationMode::ValidateResourceAddress(self.user_badge_resource)
            ).expect("Invalid user badge");
            
            self.protected_data.clone()
        }
        
        /// Public: Get user count
        pub fn get_user_count(&self) -> u32 {
            self.user_count
        }
        
        /// Public: Check if address has admin access
        pub fn is_admin(&self, proof: Proof) -> bool {
            proof.validate_proof(
                ProofValidationMode::ValidateResourceAddress(self.admin_badge.resource_address())
            ).is_ok()
        }
    }
}
```

## Key Access Control Patterns

1. **Badge Creation**: Use separate resources for different access levels
2. **Authorization**: Use `.authorize()` with badge vaults
3. **Proof Validation**: Validate proofs in public methods
4. **Role-Based Access**: Different methods for different roles
5. **Mint Roles**: Control who can create new badges
