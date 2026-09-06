# Scotch
**A quiet little product that goes looking and brings back the roles worth noticing.**

Scotch looks beyond job-title searches. It explores broadly, reads what a role actually gives you ownership of, and keeps the opportunities that could meaningfully change your next few years.

It is intentionally **not** a resume-to-job matcher.

A good opportunity can be:
- an obvious continuation,
- a step-up in scope,
- an adjacent industry move,
- an unusually high-ownership startup role,
- a lower-probability / higher-upside bet,
- or a company you did not know to search for.

## Product idea

Most career products start with a query: *"what job title are you looking for?"*

Scotch starts with a **trajectory**:

> What kinds of problems do you want to own, what evidence have you built, what constraints are real, and which moves compound your future options?

The agent pipeline separates exploration from judgment:

```
Scout swarm
   ↓
Evidence collector
   ↓
Interpreter
   ↓
Independent critic
   ↓
Scotch ranker
   ↓
Opportunity memory
```

This separation is deliberate. Discovery agents are rewarded for breadth and novelty. The critic is rewarded for skepticism. The ranker combines fit, ownership, upside, adjacency, company momentum, and risk.

## Public mode vs private lenses

The repository is safe to keep public.

The public app includes only a synthetic demonstration lens. Personal profiles, decisions, notes, and application states are **not committed**.

Private personalization is supplied at deployment through environment variables:

- `PRIVATE_LENS_JSON` — JSON profile/lens
- `PRIVATE_LENS_CODE_HASH` — SHA-256 of an unlock code
- `SECRET_KEY` — server session secret

After a correct code is entered, the server stores a session flag and exposes the private lens for that browser session. The source repository still contains no private profile.

This is a reusable capability called a **Private Lens**, not a one-off hidden user mode.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5050

## Live discovery

Click **look around**.

The current free discovery adapter uses DuckDuckGo search (`ddgs`) plus page retrieval. Search queries are generated from the active lens. There is no company allowlist.

The architecture supports additional scouts:
- open-market scout
- adjacency scout
- startup scout
- domain-neighbor scout
- known-company watcher
- ATS adapters

## Private lens setup

Generate a code hash:

```bash
python -c "import hashlib; print(hashlib.sha256(b'YOUR-CODE').hexdigest())"
```

Then export your private lens:

```bash
export PRIVATE_LENS_JSON='{"label":"My lens","desired_ownership":["..."],"evidence":["..."]}'
export PRIVATE_LENS_CODE_HASH='...'
export SECRET_KEY='use-a-long-random-value'
python app.py
```

Nothing personal needs to be committed.

## Design principles

1. **Open market, not allowlists.** Known companies are seeds, never boundaries.
2. **Ownership before keywords.** What the person would actually own matters more than tool overlap.
3. **Adjacency is a feature.** Domain changes can be valuable if the product motion transfers.
4. **Separate explorer from critic.** A single agent should not both invent and validate its own ideas.
5. **Track evidence, not vibes.** Scores should have inspectable reasons.
6. **Optimize for trajectory.** A 78-fit role can outrank a 95-fit role if it meaningfully expands future options.
7. **Private by construction.** Personalization is an injected lens, not source code.
8. **Restraint in the UI.** The product should show decisions and evidence, not every internal signal.

## Status

Prototype / product experiment. The architecture is intentionally provider-agnostic so stronger search, company-data, and model adapters can be added without changing the core product idea.
