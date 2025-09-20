# NFT Blueprint Template

Complete NFT creation and management blueprint.

## Blueprint Code

```rust
use scrypto::prelude::*;

#[blueprint]
mod nft_creator {
    struct NFTCreator {
        /// Vault to store NFTs
        nft_vault: Vault,
        /// Resource address of the NFT collection
        nft_resource: ResourceAddress,
        /// Counter for NFT IDs
        next_id: u64,
        /// Admin badge for minting
        admin_badge: Vault,
    }
    
    impl NFTCreator {
        /// Creates a new NFT collection
        pub fn create_nft_collection(
            name: String,
            description: String,
        ) -> (Global<NFTCreator>, Bucket) {
            // Create admin badge
            let admin_badge = ResourceBuilder::new_fungible(OwnerRole::None)
                .metadata(metadata!(
                    init {
                        "name" => "Admin Badge", locked;
                    }
                ))
                .mint_initial_supply(1);
            
            // Create NFT resource
            let nft_resource = ResourceBuilder::new_integer_non_fungible::<u64>(OwnerRole::None)
                .metadata(metadata!(
                    init {
                        "name" => name, locked;
                        "description" => description, locked;
                    }
                ))
                .mint_roles(mint_roles!(
                    minter => rule!(require(admin_badge.resource_address()));
                    minter_updater => rule!(deny_all);
                ))
                .create_with_no_initial_supply();
            
            let component = Self {
                nft_vault: Vault::new(nft_resource),
                nft_resource,
                next_id: 1,
                admin_badge: Vault::with_bucket(admin_badge.take(dec!("0.1"))),
            }
            .instantiate()
            .prepare_to_globalize(OwnerRole::None)
            .globalize();
            
            (component, admin_badge)
        }
        
        /// Mints a new NFT
        pub fn mint_nft(&mut self, metadata: HashMap<String, String>) -> Bucket {
            let nft_data = metadata;
            
            // Create NFT
            let nft = self.admin_badge.authorize(|| {
                borrow_resource_manager!(self.nft_resource)
                    .mint_non_fungible(&NonFungibleLocalId::Integer(self.next_id.into()), nft_data)
            });
            
            self.next_id += 1;
            nft
        }
        
        /// Burns an NFT
        pub fn burn_nft(&mut self, nft: Bucket) {
            self.admin_badge.authorize(|| {
                nft.burn();
            });
        }
        
        /// Gets NFT resource address
        pub fn get_nft_resource(&self) -> ResourceAddress {
            self.nft_resource
        }
    }
}
```

## Key NFT Patterns

1. **Non-Fungible Resource**: Use `ResourceBuilder::new_integer_non_fungible()`
2. **Access Control**: Use admin badges for mint/burn permissions
3. **Metadata**: Store NFT-specific data
4. **Authorization**: Use `.authorize()` for protected operations
5. **Local IDs**: Use `NonFungibleLocalId::Integer()` for unique IDs
