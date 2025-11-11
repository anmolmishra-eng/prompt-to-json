from sqlalchemy.orm import Session
from sqlalchemy import text

def build_preferences_from_db(db: Session, min_delta: float = 0.5):
    """
    Produce (prompt, before_spec, after_spec, preferred) tuples
    using iterations + evaluations. preferred == "B" if rating improved.
    """
    pairs = []
    rows = db.execute(text("""
      SELECT i.spec_id, i.before_spec, i.after_spec, e.score AS new_score, e.ts AS ets
      FROM iterations i
      JOIN evaluations e ON e.spec_id = i.spec_id
      ORDER BY e.ts DESC
    """)).fetchall()

    for spec_id, before, after, new_score, ets in rows:
        prev = db.execute(text("""
           SELECT score FROM evaluations
           WHERE spec_id=:sid AND ts < :ets
           ORDER BY ts DESC LIMIT 1
        """), {"sid": spec_id, "ets": ets}).fetchone()
        if not prev:
            continue
        prev_score = float(prev[0])
        delta = float(new_score) - prev_score
        if abs(delta) < min_delta:
            continue
        preferred = "B" if delta > 0 else "A"
        pairs.append(("Improve design", before, after, preferred))
    return pairs