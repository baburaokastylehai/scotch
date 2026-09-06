import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from scotch.lens import active_lens, private_available, verify_code
from scotch.scouts import run_scouts
from scotch.evidence import enrich
from scotch.reasoner import assess
from scotch.store import init, save, list_all, update_state

app=Flask(__name__); app.secret_key=os.getenv("SECRET_KEY","scotch-local-dev"); init()
def lens(): return active_lens(session.get("private_lens",False))

@app.get("/")
def home():
    min_score=int(request.args.get("min_score","55")); state=request.args.get("state",""); rows=list_all(min_score,state); q=request.args.get("q","").lower().strip()
    if q: rows=[r for r in rows if q in (r["company"]+" "+r["role"]+" "+r["domain"]+" "+r["snippet"]).lower()]
    return render_template("index.html",items=rows,lens=lens(),private=session.get("private_lens",False),private_available=private_available())

@app.post("/explore")
def explore():
    L=lens(); found=run_scouts(L); kept=0
    for c in found[:60]:
        blob=(c.role+" "+c.snippet).lower()
        if "product manager" not in blob: continue
        c=enrich(c); a=assess(c,L)
        if a.scotch_score>=45: save(c,a); kept+=1
    flash(f"looked around: {kept} opportunities interpreted and remembered."); return redirect(url_for("home"))

@app.post("/unlock")
def unlock():
    if verify_code(request.form.get("code","")): session["private_lens"]=True; flash("Private lens active for this browser session.")
    else: flash("That lens code did not match.")
    return redirect(url_for("home"))

@app.post("/lock")
def lock(): session.pop("private_lens",None); return redirect(url_for("home"))

@app.post("/state/<oid>")
def state(oid): update_state(oid,request.form.get("state","New")); return redirect(request.referrer or url_for("home"))

@app.get("/api/opportunities")
def api(): return jsonify(list_all(0,""))

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5050")),debug=False)
