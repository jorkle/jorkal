def get_schema():
    schema = {
        "sources": {
            "required": True,
            "type": "dict",
            "schema": {
                "linkedin": {"required": True, "type": "boolean"},
                "indeed": {"required": True, "type": "boolean"},
            },
        },
        "destinations": {
            "required": True,
            "type": "dict",
            "schema": {
                "discrd": {"required": True, "type": "boolean"},
            },
        },
        "check_interval": {"required": True, "type": "integer"},
        "database_file": {"required": True, "type": "string"},
        "queries": {
            "required": True,
            "type": "list",
            "schema": {
                "type": "string",
            },
        },
        "job_title_expressions": {
            "required": True,
            "type": "list",
            "schema": {
                "type": "string",
            },
        },
        "chrome_data_dir": {"required": True, "type": "string"},
        "discord_channel_id": {"required": True, "type": "string"},
        "discord_token": {"required": True, "type": "string"},
    }
    return schema
