from a.third_party import cockroachdb as db, session_storage


def _get_gate_value(feature_name):
    row = (
        db.sql_query_single(
            f"""
        SELECT value
        FROM gating
        WHERE 
            uid = '{session_storage.get_identifier()}' AND
            feature_name = '{feature_name}'
        """
        )
        or {}
    )
    return row.get("value")


def is_feature_enabled(feature_name):
    value = _get_gate_value(feature_name)
    return value == "on"


def enable_feature(feature_name, value="on"):
    db.sql_update(
        f"""
    INSERT INTO gating (uid, feature_name, value)
    VALUES (
        '{session_storage.get_identifier()}', 
        '{feature_name}',
        '{value}'
    )
    """
    )
