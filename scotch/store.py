import sqlite3, hashlib, os, json
from pathlib import Path
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parents[1]
DB=Path(os.getenv("SCOTCH_DB_PATH",str(BASE/"scotch.db")))

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    c=connect(); c.executescript("""
    create table if not exists opportunities(
      id text primary key, company text, role text, url text unique, location text, compensation text, domain text,
      source text, discovery_reason text, snippet text, page_text text,
      ownership integer, transfer integer, step_up integer, optionality integer, venture_upside integer, risk integer,
      signal integer, why_this text, what_you_own text, what_carries text, stretch text,
      critique text, recommendation text, evidence_json text,
      state text default 'New', first_seen text, last_seen text, posted_hint text
    );
    create table if not exists runs(id integer primary key autoincrement, ran_at text, lens_label text, found integer);
    """)
    existing={r[1] for r in c.execute("pragma table_info(opportunities)")}
    additions={"signal":"integer","why_this":"text","what_you_own":"text","what_carries":"text","stretch":"text","evidence_json":"text","posted_hint":"text"}
    for name,typ in additions.items():
        if name not in existing: c.execute(f"alter table opportunities add column {name} {typ}")
    if "trajectory_score" in existing and "signal" not in existing: c.execute("update opportunities set signal=trajectory_score where signal is null")
    c.commit(); c.close()

def save(candidate,assessment):
    now=datetime.now(timezone.utc).isoformat(); oid=hashlib.sha1(candidate.url.encode()).hexdigest()[:18]; c=connect(); old=c.execute("select first_seen,state from opportunities where id=?",(oid,)).fetchone(); first=old["first_seen"] if old else now; state=old["state"] if old else "New"; a=assessment
    c.execute("""insert or replace into opportunities (id,company,role,url,location,compensation,domain,source,discovery_reason,snippet,page_text,ownership,transfer,step_up,optionality,venture_upside,risk,signal,why_this,what_you_own,what_carries,stretch,critique,recommendation,evidence_json,state,first_seen,last_seen,posted_hint) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(oid,candidate.company,candidate.role,candidate.url,candidate.location,candidate.compensation,candidate.domain,candidate.source,candidate.discovery_reason,candidate.snippet,candidate.page_text,a.ownership,a.transfer,a.step_up,a.optionality,a.venture_upside,a.risk,a.signal,a.why_this,a.what_you_own,a.what_carries,a.stretch,a.critique,a.recommendation,json.dumps(a.evidence),state,first,now,candidate.posted_hint)); c.commit(); c.close()
def record_run(lens_label,found):
    c=connect(); c.execute("insert into runs(ran_at,lens_label,found) values(?,?,?)",(datetime.now(timezone.utc).isoformat(),lens_label,found)); c.commit(); c.close()
def list_all(min_score=0,state=""):
    c=connect(); q="select * from opportunities where coalesce(signal,0)>=?"; args=[min_score]
    if state: q+=" and state=?"; args.append(state)
    rows=[dict(x) for x in c.execute(q+" order by signal desc, ownership desc",args)]; c.close(); return rows
def update_state(oid,state):
    c=connect(); c.execute("update opportunities set state=? where id=?",(state,oid)); c.commit(); c.close()
