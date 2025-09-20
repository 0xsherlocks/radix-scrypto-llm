// src/blueprint.rs
use scrypto::prelude::*;

declare_contracts! {
    contract Greeting {
        data {
            message: String,
        }

        func init() -> DecodedMsg {
            DecodedMsg::ok()
        }

        func set_message(new_message: String) -> DecodedMsg {
            message = new_message;
            DecodedMsg::ok()
        }

        func get_message() -> DecodedMsg {
            DecodedMsg::ok(message)
        }
    }
}