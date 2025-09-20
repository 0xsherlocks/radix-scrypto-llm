#  Blueprints and Components __

* Updated on Feb 11, 2025
* Published on Sep 8, 2023

* __4 minute(s) read

__

__Export PDF

[ Prev ](/docs/resim-radix-engine-simulator "resim \(Radix Engine Simulator\)")[ Next ](/docs/resources "Resources")

Scrypto splits the concept of "smart contract" into two parts: blueprints and components.

Blueprints define the logic and the type of data your component holds. On the other hand, components are live instantiation of your blueprint. Therefore, components are more akin to how a smart contract are conventionally understood where users on the network can interact with.

Blueprints in Scrypto are similar to classes in object-oriented programming. Each blueprint contains declarations of state structure, functions, and methods a component can have. This way, blueprints can be considered templates for components.

A function on the blueprint is expected to perform the instantiation of the blueprint into an active component, typically including configuration parameters for that instance. As templates, blueprints contain no internal state and can hold no resources. As a result, multiple components can be instantiated from the same blueprint.

For example, if we have blueprint which defines the structure and logic of a liquidity pool, we can instantiate multiple components which facilitate token swaps across many different token pairs. While each component may facilitate different token pairs, all components instantiated from the same blueprint behave the same.

Scrypto code starts its lifecycle as a blueprint package. Each package contain one or more blueprints and are deployed to the network. Once deployed, components can be instantiated from blueprints where users can interact with.

A simple example of a blueprint can look like this:


use scrypto::prelude::*;

# [blueprint]
mod hello {
   struct Hello {
       // Define what resources and data will be managed by Hello components
       sample_vault: Vault,
   }

   impl Hello {
       // Implement the functions and methods which will manage those resources and data
       // This is a function, and can be called directly on the blueprint once deployed
       pub fn instantiate_hello() -> Global<Hello> {
           // Create a new token called "HelloToken," with a fixed supply of 1000, and put that supply into a bucket
           let my_bucket: Bucket = ResourceBuilder::new_fungible(OwnerRole::None)
               .metadata(metadata!(
                   init {
                       "name" => "Hello Token", locked;
                       "symbol" => "HT", locked;
                   }
               ))
               .mint_initial_supply(1000);

           // Instantiate a Hello component, populating its vault with our supply of 1000 HelloToken
           Self {
               sample_vault: Vault::with_bucket(my_bucket),
           }
           .instantiate()
           .prepare_to_globalize(OwnerRole::None)
           .globalize()
       }

       // This is a method, because it needs a reference to self.  Methods can only be called on components
       pub fn free_token(&mut self) -> Bucket {
           info!(
               "My balance is: {} HelloToken. Now giving away a token!",
               self.sample_vault.amount()
           );
           // If the semi-colon is omitted on the last line, the last value seen is automatically returned
           // In this case, a bucket containing 1 HelloToken is returned
           self.sample_vault.take(1)
       }
   }
}

## The `use` Declaration

The very first part of a blueprint is the use declaration to import symbols from the Scrypto standard library and/or other libraries. It creates local name bindings with items defined in an external path.

The example `scrypto::prelude::*` is the list of things that are commonly used in Scrypto. Importing Scrypto prelude saves you from manually importing everything that you need individually.

## The #[blueprint] Macro

The `#[blueprint]` macro allows you to define a blueprint using items defined in Rust grammar. It groups a pair of struct and impl within a mod.

A mod is used to define a module in Rust, and it is a way to organize everything that encapsulates a blueprint in Scrypto. The mod is followed by a name, which can be anything so long as it is a snake_case identifier.

The struct is all the fields that each component instantiated from will have. It is followed by the name you would like to call your blueprint. Blueprint names unlike mod use a CamelCase identifier and are used to instantiate components. In this example, our blueprint name is Hello. The fields within a struct can be of any data type supported by SBOR, including but not limited to integers, strings, tuples, vectors and maps. Additionally, the struct field can also define the resources the component will have and/or interact with.

Finally, within the impl (implementation) block, is where all the functions and methods can be defined. It is also followed the blueprint name specified in the struct.

## The `.instantiate()` Method

The `.instantiate()` method transforms Rust value within the blueprint into a component.

From there, a component may now be `globalized`, meaning that the component is addressable and can be interacted with by any user on the network. Otherwise, _components not globalized_ can be `owned` by other `components` and _only callable by components which own them_.

Was this article helpful?

__Yes __No