import json
from typing import Optional, Dict, Any
from app.core.db import get_connection

def log_action(
    user_id: str,
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    approved_by_user: bool = True
) -> int:
    """Records an action in the audit log ensuring transparency and responsible AI compliance."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO audit_log (user_id, action, entity, entity_id, payload, approved_by_user)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            entity,
            entity_id,
            json.dumps(payload or {}),
            1 if approved_by_user else 0
        )
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_user_audit_logs(user_id: str, limit: int = 50):
    """Fetches recent audit records for transparency."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, action, entity, entity_id, payload, approved_by_user, created_at
        FROM audit_log
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "action": r["action"],
            "entity": r["entity"],
            "entity_id": r["entity_id"],
            "payload": json.loads(r["payload"]) if r["payload"] else {},
            "approved_by_user": bool(r["approved_by_user"]),
            "created_at": r["created_at"]
        })
    return result
