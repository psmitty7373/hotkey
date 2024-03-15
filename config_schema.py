config_schema = {
    "type": "object",
    "properties": {
        "current_layout": {"type": "string"},
        "layouts": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z0-9_]{0,31}$": {
                    "type": "object",
                    "properties": {
                        "buttons": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "size": {"type": "integer", "enum": [1, 4, 9]},
                                    "macro": {"type": "string"}
                                },
                                "required": ["size"]
                            }
                        }
                    },
                    "required": ["buttons"]
                }
            },
            "additionalProperties": False
        },
        "macros": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z0-9_]{0,31}$": {
                    "type": "object",
                    "properties": {
                        "image": {"type": "string", "maxLength": 256},
                        "action": {"type": "string", "maxLength": 256}
                    },
                    "required": ["image", "action"]
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["current_layout", "layouts", "macros"]
}