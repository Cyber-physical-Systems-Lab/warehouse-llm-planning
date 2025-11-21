ACTIONS = {
    "base.goto": {
        "pre":  [("is_pose", "target")],
        "eff":  [("set_at", "target")]
    },
    "arm.pick": {
        "pre":  [("at_reach", "from"),
                 ("slot_has", "from", "object"),
                 ("holding_is", None)],
        "eff":  [("slot_set", "from", None),
                 ("holding_set", "object")]
    },
    "arm.place": {
        "pre":  [("at_reach", "to"),
                 ("holding_is", "object"),
                 ("slot_free", "to")],
        "eff":  [("slot_set", "to", "object"),
                 ("holding_set", None)]
    }
}

ACTION_SCHEMA = {
    "base.goto": {
        "required": ["action", "target"],
        "allowed":  ["action", "target"]
    },
    "arm.pick": {
        "required": ["action", "object", "from"],
        "allowed":  ["action", "object", "from"]
    },
    "arm.place": {
        "required": ["action", "object", "to"],
        "allowed":  ["action", "object", "to"]
    }
}
