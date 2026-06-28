import json

def metadata_to_json(metadata: dict) -> str:

    return json.dumps(
        metadata,
        separators=(",", ":"),
        ensure_ascii=False
    )


def json_to_metadata(json_string: str) -> dict:

    return json.loads(json_string)