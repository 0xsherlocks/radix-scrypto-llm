[🏠](/)

![Scrypto \(Programming Language\)](https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/5ef750a8-fe8d-457c-802d-3f4b4c615f9e/Scrypto3/w=3840,quality=90,fit=scale-down)

![Scrypto \(Programming Language\)](https://images.spr.so/cdn-cgi/imagedelivery/j42No7y-dcokJuNgXeA0ig/0e4d1cac-cd97-47c5-a853-c1ab02b24ead/Scrypto/w=256,quality=90,fit=scale-down)

# Scrypto (Programming Language)

👾 Repos

[github.com/radixdlt/radixdlt-scrypto](https://github.com/radixdlt/radixdlt-scrypto)

**[Scrypto](https://github.com/radixdlt/radixdlt-scrypto)** [ /’skrɪptoʊ/ ] is an open-source, smart-contract programming language, designed specifically for the development of decentralized applications (dApps) on Radix.

* Overview
* Features
* Syntax and Tools
* Blueprints
* Packages
* Components
* Comparison to Other Languages
* Resources

| **DEVELOPMENT**
---|---
**Paradigm**| [Imperative](https://en.wikipedia.org/wiki/Imperative_programming) ([Procedural](https://en.wikipedia.org/wiki/Procedural_programming), [Object-Oriented](https://en.wikipedia.org/wiki/Object-oriented_programming)); Supports [Functional](https://en.wikipedia.org/wiki/Functional_programming) programming; [Structured](https://en.wikipedia.org/wiki/Structured_programming);
**Developer(s)**| [RDX Works](/ecosystem/rdx-works)
**Initial Release**| [2021-12-15](https://www.radixdlt.com/post/alexandria-scrypto-is-here)
**Latest Release**| [v1.3 (Cuttlefish)](https://github.com/radixdlt/radixdlt-scrypto/releases)
**Documentation**| [docs-babylon.radixdlt.com/main/scrypto/introduction.html](https://docs-babylon.radixdlt.com/main/scrypto/introduction.html)
**Github Repo**| [github.com/radixdlt/radixdlt-scrypto](https://github.com/radixdlt/radixdlt-scrypto)
**License**| [Radix License, v1](http://radixfoundation.org/licenses/license-v1)
**Community**| [t.me/RadixDevelopers](https://t.me/RadixDevelopers)

## Overview

Scrypto exists as a set of libraries and compiler extensions that add features, syntax and data types to the [Rust](https://www.rust-lang.org) programming language, allowing for an ‘asset-oriented’ style of programming that treats tokens, NFTs and other ‘resources’ as native objects.

## Features

Scrypto introduces several key features designed specifically for Radix development:

* Asset-oriented programming model: Unlike account-based models like Ethereum, Scrypto has native support for tokens, NFTs, and other digital assets as first-class primitives. Resources like tokens can be directly stored, transferred, and manipulated.
* Finite state machine model for tokens: Token behavior in Scrypto adheres to a predefined finite state machine. This provides predictable rules around things like minting, burning, transferring, and admin capabilities. The model improves security and avoids surprises.
* Access control using ‘badges': Instead of checking the message caller's address for authorization like Solidity, Scrypto uses "badges" - tokens or NFTs - to dictate access rules. This enables complex permissions not tied to accounts.
* Built-in royalty system: Smart contract developers can configure royalties to be automatically collected when their contracts are used. This incentivizes creation of reusable blueprints.
* Strong typing and compile-time checks: Scrypto leverages Rust's strong type system and compile-time checks to improve security and developer experience. Many common bugs are caught during compilation.
* Developer tooling: Scrypto includes a command line tool, simulator, testing framework, and other tooling to enable rapid smart contract development.

## Syntax and Tools

Scrypto adopts a syntax similar to the Rust programming language, as it is built on the Rust compiler toolchain. Like Rust, Scrypto utilizes:

* Statically typed variables
* Immutability by default
* Explicit variable ownership
* Pattern matching
* Trait-based generics
* Closure expressions

However, Scrypto extends Rust by adding:

* New primitive data types like tokens, NFTs, badges, etc.
* Attributes like #[blueprint] to denote smart contract blueprints
* Built-in functions for blockchain interaction
* Removal of non-deterministic features like floating point numbers

Scrypto code compiles to WebAssembly (WASM) to run on the Radix virtual machine. The key tools available in the Scrypto developer toolkit include:

* Scrypto CLI: Command line tool for building, testing, and deploying Scrypto packages. It wraps cargo for blockchain workflows.
* Radix Engine Simulator (Resim): Local simulator that emulates the Radix ledger and runtime. Useful for development testing.
* Testing Framework: Tools designed for unit testing Scrypto blueprints and components.
* Radix Dashboard: GUI for deploying and interacting with Scrypto packages and components.
* Wallet SDK: APIs for connecting Scrypto dApps with the Radix Wallet.
* ROLA: Off-ledger authentication system allowing server apps to connect with on-ledger identities.

The toolkit enables rapid development, testing, and deployment of end-to-end decentralized applications with Scrypto.

### **Blueprints**

Scrypto introduces a concept called ‘blueprints’ - similar to classes in object oriented programming - to build reusable, modular smart contract components.

Blueprints define the structure and logic for components, including:

* State variables to hold token supplies, user balances etc.
* Functions to instantiate new component instances
* Methods to modify state and execute business logic

Components are then live instances created from blueprints, like objects instantiated from classes.

This separation of blueprints and components enables:

* Reusable code: Components created from the same blueprint have shared logic but separate state. Similar to how classes define objects.
* Upgradability: Components can be instantiated from new blueprint versions to get upgrades. The blueprint system facilitates iterating code.
* Composability: Components can easily call other components to form complex decentralized apps, with clear interfaces between the parts.
* Developer incentives: Blueprint authors can charge royalties when others utilize their blueprints to build applications. This funds open source development.

Scrypto developers are encouraged to build small, modular blueprints that "do one thing well" - following Unix philosophy - rather than massive monolithic contracts.

### **Packages**

A Scrypto package is a bundle of one or more blueprints that is published to the Radix ledger.

Packages have a unique on-ledger package address once deployed. This allows them to be called and reused by other packages and applications.

Scrypto code is modularized into packages to promote reusability. Some benefits include:

* Code Organization: Logically grouping related blueprints and functionality into a package.
* Namespace Control: Packages manage identifier namespaces for state variables, functions etc inside them.
* Encapsulation: Packages can decide which blueprint functions/methods to expose publicly for calling.
* Versioning: Packages can publish updates while maintaining addresses and backwards compatibility.
* Royalties: Package creators can charge usage fees when downstream code calls package functions.
* Sharing: Packages enable discovering and importing reusable Scrypto code modules.

The Scrypto CLI provides commands for packaging, testing and deploying Scrypto code to the Radix ledger as ready to use packages.

There is growing developer momentum around publishing packages covering areas like token contracts, lending, identity, governance and more.

### Components

Components are a core building block in Scrypto for encapsulating logic and holding state. They are similar to smart contracts in other blockchain platforms, but have some key differences:

Components are defined by creating a Rust struct inside a blueprint module, like this:

Copy


# [blueprint]
mod my_component {

struct MyComponent {
my_field: Type,
}

}


The struct defines the fields that will be stored in the component's state when it is instantiated.

To instantiate a component from a blueprint, call the .instantiate() method on the struct:

Copy


let my_component = MyComponent {
my_field: value
}.instantiate();


This will create a new instance of the MyComponent struct and return a reference to it.

At this point, the component instance exists locally in the transaction. To make it accessible globally, it needs to be "globalized" using the .globalize() method:

Copy


my_component.instantiate()
.prepare_to_globalize(OwnerRole::None)
.globalize()


To call methods on a component, you reference the component instance and call the method:

Copy


my_component.some_method();


Components can also hold resources like tokens in vaults and buckets:

Copy


struct MyComponent {
my_vault: Vault
}

// Put tokens in vault
my_component.my_vault.put(some_bucket);

// Take tokens out
let bucket = my_component.my_vault.take(100);


* Components encapsulate state and logic
* Defined via Rust structs inside blueprints
* Instantiated from blueprint structs
* Need to be globalized to be publicly accessible
* Interact by calling methods and accessing state

## Comparison to Other Languages

Scrypto differs from other smart contract languages like Solidity and Move in several key aspects:

* Compared to Solidity, Scrypto code is more intuitive and easier to reason about due to its asset-oriented model. The finite state machine for assets also provides stronger security guarantees around token behavior.
* Unlike Move's account-based programming model, Scrypto was built from the ground up for asset-oriented development. Assets are primitive rather than secondary abstractions derived from accounts.
* Scrypto is the first smart contract language designed specifically for predictable and secure asset handling. Existing languages were retrofitted for blockchain use cases.
* Strong typing and compile-time checks give Scrypto better security properties out of the box compared to untyped languages like Solidity.
* Access control using badges rather than relying on caller addresses avoids issues like privilege escalation exploits seen in other platforms.
* Scrypto has native blockchain tooling for development, testing, and deployment lacking in general purpose languages used for smart contracts.

Overall, Scrypto aims to combine the performance and checkability of Rust with domain-driven design tailored specifically for decentralized applications and finance.

## Resources

Installation instructions, examples and resources are available on the [Radix Developer Resources](/contents/resources/radix-developer-resources) page.