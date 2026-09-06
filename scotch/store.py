import sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parents[1]
DB=BASE/"scotch.db"

def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    c=connect(); c.executescript("""
    create table if not exists opportunities(
      id text primary key, company text, role text, url text unique, location text, compensation text, domain text,
      source text, discovery_reason text, snippet text, page_text text,
      ownership integer, transfer integer, step_up integer, optionality integer, venture_upside integer, risk integer,
      scotch_score integer, interpretation text, critique text, recommendation text,
      state text default 'New', first_seen text, last_seen text
    );
    """); c.commit(); c.close()

def save(candidate, assessment):
    now=datetime.now(timezone.utc).isoformat(); oid=hashlib.sha1(candidate.url.encode()).hexdigest()[:18]; c=connect()
    old=c.execute("select first_seen,state from opportunities where id=?",(oid,)).fetchone()
    first=old["first_seen"] if old else now; state=old["state"] if old else "New"; a=assessment
    c.execute("""insert or replace into opportunities values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
    (oid,candidate.company,candidate.role,candidate.url,candidate.location,candidate.compensation,candidate.domain,candidate.source,candidate.discovery_reason,candidate.snippet,candidate.page_text,a.ownership,a.transfer,a.step_up,a.optionality,a.venture_upside,a.risk,a.scotch_score,a.interpretation,a.critique,a.recommendation,state,first,now))
    c.commit(); c.close()

def list_all(min_score=0,state=""):
    c=connect(); q="select * from opportunities where scotch_score>=?"; args=[min_score]
    if state: q+=" and state=?"; args.append(state)
    rows=[dict(x) for x in c.execute(q+" order by scotch_score desc, ownership desc",args)]; c.close(); return rows

def update_state(oid,state):
    c=connect(); c.execute("update opportunities set state=? where id=?",(state,oid)); c.commit(); c.close()
