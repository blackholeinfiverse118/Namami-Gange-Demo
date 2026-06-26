import time
import hashlib
import json
from db import get_db_connection

# In-memory states for the tick engine
_current_block = 1250
_validation_breach = False
_corr_counter = 500

def get_replay_status():
    """
    Returns current block, breach flag, and recent ledger entries.
    """
    global _current_block, _validation_breach
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_ledger ORDER BY timestamp DESC LIMIT 15")
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for r in rows:
        evt = dict(r)
        evt["payload"] = json.loads(evt["payload"])
        logs.append(evt)
        
    return {
        "current_block": _current_block,
        "validation_breach": _validation_breach,
        "logs": logs
    }

def toggle_breach():
    """
    Toggles the schema breach simulation flag.
    """
    global _validation_breach
    _validation_breach = not _validation_breach
    return _validation_breach

def increment_tick():
    """
    Increments the simulation tick (block), updates dynamic metrics, and logs an event.
    """
    global _current_block, _validation_breach, _corr_counter
    _current_block += 1
    _corr_counter += 1
    
    corr_id = f"CORR-2026-0626-{_corr_counter}{'ERR' if _validation_breach else 'X'}"
    trace_id = f"TRC-REPLAY-{_current_block}"
    timestamp = time.strftime("%H:%M:%S")
    
    event_type = "SCHEMA_FALLBACK" if _validation_breach else "DETERMINISTIC_REPLAY"
    
    payload = {
        "block": _current_block,
        "status": "BREACH" if _validation_breach else "VERIFIED",
        "message": (
            f"CRITICAL: Contract schema breach detected on VARANASI telemetry node."
            if _validation_breach else
            f"Deterministic replay validated successfully for block #{_current_block}."
        )
    }
    
    # Generate cryptographic audit hash (Sprint 6 Audit Hash)
    payload_str = json.dumps(payload, sort_keys=True)
    hash_input = f"{corr_id}|{trace_id}|{timestamp}|{event_type}|{payload_str}"
    audit_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO event_ledger (event_id, correlation_id, trace_id, timestamp, event_type, payload, audit_hash)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"EVT-{_current_block}", corr_id, trace_id, timestamp, event_type, payload_str, audit_hash
    ))
    conn.commit()
    conn.close()
    
    return {
        "block": _current_block,
        "correlation_id": corr_id,
        "trace_id": trace_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "payload": payload,
        "audit_hash": audit_hash
    }
