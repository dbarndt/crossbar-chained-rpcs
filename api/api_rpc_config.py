URI_PREFIX = "com.lojack.rtu"

PROC_URI_PREFIX = ".".join([URI_PREFIX, "proc"])

PROCS = {
    "v1": [
        "create",
        "read",
        "update",
        "delete",
        "shutdown",
        "restart",
        "flush"
    ]
}


DATA_URI_PREFIX = ".".join([URI_PREFIX, "data"])

DATA_PROCS = {
    "v1": {
        "config": {
            "procs": {
                "v1": [
                    "read",
                    "update"
                ]
            }
        },
        "general": {
            "data": [
                "site_id",
                "site_description",
                "slot_length",
                "slots"
            ],
            "procs": {
                "v1": [
                    "read"
                ]
            }
        }
    }
}

