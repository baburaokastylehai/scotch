import os, json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from scotch.lens import active_lens, private_available, verify_code
from scotch.scouts import run_scouts
from scotch.evidence import enrich
from scotch.reasoner import assess
from scotch.store import init, save, list_all, update_state, record_run, connect

app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","scotch-local-dev")
init()

# Remove known low-quality artifacts produced by older discovery builds.
def cleanup_old_noise():
    c=connect()
    c.execute("delete from opportunities where lower(role) like 'job application for %' or lower(url) like '%/apply'")
    c.commit(); c.close()
cleanup_old_noise()

def lens():
    return active_lens(session.get("private_lens",False))

def discover_and_store(L, quick=False):
    found=run_scouts(L,per_query=4 if quick else 6,quick=quick)
    kept=0
    max_candidates=18 if quick else 55
    for c in found[:max_candidates]:
        blob=(c.role+" "+c.snippet).lower()
        if "product manager" not in blob and "product lead" not in blob:
            continue
        c=enrich(c)
        a=assess(c,L)
        # Scotch is a shortlist, not a search-results dump. Hard gaps and weak
        # maybes stay out of the feed entirely.
        if a.recommendation in ("pursue","inspect") and a.signal>=60:
            save(c,a); kept+=1
    record_run(L.get("label","lens"),kept)
    return kept

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action=request.form.get("lens_action","")
        if action == "unlock":
            if verify_code(request.form.get("code","")):
                session["private_lens"]=True
                session.pop("first_pass_attempted",None)
                flash("your lens is on.")
            else:
                flash("that code didn't open a lens.")
            return redirect(url_for("home"))
        if action == "lock":
            session.pop("private_lens",None); session.pop("first_pass_attempted",None)
            flash("back to the public lens.")
            return redirect(url_for("home"))
        return redirect(url_for("home"))

    if session.get("private_lens",False) and not session.get("first_pass_attempted") and not list_all(0,""):
        session["first_pass_attempted"]=True
        try:
            kept=discover_and_store(lens(),quick=True)
            flash(f"{kept} strong move{'s' if kept!=1 else ''} made the first cut." if kept else "nothing strong enough made the first cut yet. try a wider look.")
        except Exception:
            flash("the first pass didn't finish. try a wider look.")

    min_score=int(request.args.get("min_score","60"))
    state=request.args.get("state","")
    rows=list_all(min_score,state)
    q=request.args.get("q","").lower().strip()
    if q:
        rows=[r for r in rows if q in (r["company"]+" "+r["role"]+" "+r["domain"]).lower()]
    return render_template("index.html",items=rows,lens=lens(),private=session.get("private_lens",False),private_available=private_available(),build=os.getenv("RENDER_GIT_COMMIT","local")[:7])

@app.post("/look")
def look():
    try:
        kept=discover_and_store(lens(),quick=False)
        flash(f"{kept} strong move{'s' if kept!=1 else ''} made the cut." if kept else "nothing strong enough survived this pass.")
    except Exception as ex:
        flash(f"couldn't finish that look — {ex}")
    return redirect(url_for("home"))

@app.route("/unlock",methods=["GET","POST"],strict_slashes=False)
def unlock():
    if request.method=="POST" and verify_code(request.form.get("code","")):
        session["private_lens"]=True; session.pop("first_pass_attempted",None)
    return redirect(url_for("home"))

@app.route("/lock",methods=["GET","POST"],strict_slashes=False)
def lock():
    session.pop("private_lens",None); session.pop("first_pass_attempted",None)
    return redirect(url_for("home"))

@app.post("/state/<oid>")
def state(oid):
    update_state(oid,request.form.get("state","New")); return redirect(request.referrer or url_for("home"))

@app.get("/api/opportunities")
def api(): return jsonify(list_all(0,""))

@app.get("/health")
def health(): return jsonify({"status":"ok","build":os.getenv("RENDER_GIT_COMMIT","local")[:7],"private_lens_configured":private_available()})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5050")),debug=False)
