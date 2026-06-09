# Plan — Push `Hazard_modeling` to its remote ✅ DONE

> **Status: ✅ Pushed (2026-06-09).** Live at **https://github.com/D-ivyy/Hazard_Modeling** (PRIVATE).
> Pushed `main` (HEAD `e32a48b`); `.env`, the 905 MB MRMS cache, parquets, `.venv`, and the cross-project
> symlinks all stayed local (gitignored — verified). The runbook below is kept as the historical record;
> the **actual outcome differs** from the originally-locked plan — see the next block.

## What actually happened (supersedes the locked plan below)

- **Destination: personal `D-ivyy/Hazard_Modeling`** (owner's call), **not** the `aamani-ai` org. Private.
- **Auth: SSH, not HTTPS.** The originally-planned HTTPS-via-`gh` path was **blocked** — the `gh` OAuth
  token lacks the **`workflow` scope**, so GitHub refused the push (it contains `.github/workflows/ci.yml`;
  *"refusing to allow an OAuth App to create or update workflow … without `workflow` scope"*).
  **SSH has no such restriction** (it authenticates as the user, who can push workflows).
- **The SSH identity matters:** this machine has 3 GitHub SSH aliases —
  `github.com-work → D-ivyy`, `github.com-personal → Divi-patel`, `github.com-divy → D-ivy` (a *different*
  account). **`D-ivyy` = the `github.com-work` alias** (`id_ed25519_work`). The default key returns
  *"Repository not found"* (no access to this private repo); the working remote is:
  ```
  git remote set-url origin git@github.com-work:D-ivyy/Hazard_Modeling.git
  git push -u origin main
  ```
- **Reusable rule:** to push to `D-ivyy`, use the `github.com-work` SSH alias. Prefer SSH over the `gh`
  HTTPS token whenever the repo contains GitHub Actions workflows (the token lacks `workflow` scope).

---

## Original (now-historical) plan — locked decisions

> _Last updated: 2026-06-08. Superseded by the outcome above (org → personal; HTTPS → SSH)._

## Decisions (locked)

| Item | Decision |
|---|---|
| Host | GitHub |
| Destination | **`aamani-ai`** org (matches `model-gpr` and `aamani-ai/hazards`) |
| Repo name | **`Hazard_modeling`** — keep the folder name. *(Note: the org's other repos use lowercase-kebab, e.g. `model-gpr`, `infrasure-docs`; this one is intentionally the folder name.)* |
| Visibility | **Private** (every `aamani-ai` repo is private; this contains internal methodology) |
| Remote name | `origin` |
| Auth / protocol | **HTTPS + the `gh` credential helper** — mirrors `model-gpr`'s working `aamani` remote. SSH keys on this machine auth as the *personal* account; HTTPS via `gh` uses the `D-ivyy` token, which **is** an `aamani-ai` member. |

## Current local state

- Branch: **`main`**
- Initial commit: **`ff50a00`** — _"Initial scaffold: docs, Notebooks, agent guidance, CI, Drive reference set"_ (14 files).
- **No remote configured** yet (`git remote -v` is empty).
- Active `gh` account: **`D-ivyy`** — `aamani-ai` org member, scopes `repo` + `read:org`.

## Steps to execute (when ready)

```bash
cd /Users/divy/code/work/infrasure_git_codes/Hazard_modeling

# 1. Create the private org repo (no auto-push — we set an explicit HTTPS remote)
gh repo create aamani-ai/Hazard_modeling --private

# 2. Add it as origin over HTTPS (so the gh credential helper handles org auth)
git remote add origin https://github.com/aamani-ai/Hazard_modeling.git

# 3. Push main + set upstream
git push -u origin main

# 4. Verify
gh repo view aamani-ai/Hazard_modeling --json name,visibility,url
git remote -v
```

## Pre-push checklist

- [ ] Confirm we actually want it remote (this plan is currently **deferred**).
- [ ] Decide whether to reorganize `docs/google_drive_docs/` into Drive-mirroring subfolders **before** the first push (currently flat).
- [ ] Confirm the commit author identity is acceptable (`Divi-patel <divy2023@gmail.com>`).
- [ ] Confirm `.gitignore` still excludes the local cross-project symlinks + `.venv` (true as of `ff50a00`).
- [ ] (Optional) Default-branch / branch-protection settings in the org.

## Notes / fallbacks

- If `gh repo create` fails on permissions, the `member` role may not allow repo creation in `aamani-ai` — an org admin would create the empty repo, then run steps **2–4** only.
- To push under the **personal** account instead (like `infrasure-hazard-competitive-research`), swap step 1 for `gh repo create D-ivyy/Hazard_modeling --private` and the remote URL accordingly.
