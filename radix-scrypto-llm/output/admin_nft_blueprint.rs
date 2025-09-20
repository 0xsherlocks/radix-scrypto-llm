#[blueprint]
mod admin_nft {
    struct NFT {
        /// This is the vault to store the NFTs
        nft_vault: Vault,
        /// Resource address for the NFT
        nft_resource_address: ResourceAddress,
        /// A counter for ID generation
        nft_id_counter: u64,
        /// A vault that collects all XRD payments to mint the NFT
        xrd_vault: Vault,
        /// Admin address
        admin_address: Address,
    }

    impl NFT {
        pub fn instantiate(admin_address: Address) -> ComponentAddress {
            // Create the NFT resource
            let nft_resource = ResourceBuilder::new_non_fungible()
                .metadata("name", "Admin NFT")
                .metadata("description", "An NFT controlled by the admin")
                .divisibility(DIVISIBILITY_NONE)
                .mint_initial_supply(0);

            // Create the vault to store the NFTs
            let nft_vault = Vault::with_resource(nft_resource);

            // Create a counter for ID generation
            let nft_id_counter = 0;

            // Create a vault that collects all XRD payments to mint the NFT
            let xrd_vault = Vault::new();

            // Create the admin address
            let admin_address = admin_address;

            // Return the component address
            ComponentAddress::from(nft_vault)
        }

        pub fn mint(&mut self, owner: Address, metadata: String) -> Decimal {
            // Check if the caller is the admin
            if self.admin_address != env::get_caller() {
                panic!("Only the admin can mint NFTs");
            }

            // Increment the ID counter
            self.nft_id_counter += 1;

            // Mint a new NFT
            self.nft_vault.put(self.nft_id_counter, metadata);

            // Return the minted NFT's ID
            Decimal::from(self.nft_id_counter)
        }

        pub fn burn(&mut self, nft_id: u64) -> Decimal {
            // Check if the caller is the admin
            if self.admin_address != env::get_caller() {
                panic!("Only the admin can burn NFTs");
            }

            // Check if the NFT exists
            if !self.nft_vault.contains(nft_id) {
                panic!("NFT does not exist");
            }

            // Burn the NFT
            self.nft_vault.remove(nft_id);

            // Return the burned NFT's ID
            Decimal::from(nft_id)
        }
    }
}