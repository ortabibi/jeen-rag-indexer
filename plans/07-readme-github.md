# Stage 7 – README, sample runs, GitHub

**Goal:** documentation and a clean, published repository.

**What I'm going to do**
Write `README.md` in English with:
- what the project does
- installation (venv + `pip install -r requirements.txt`)
- the environment variables (pointing to `.env.example`, never real values)
- how each chunking strategy works
- run examples
- **real** sample output copied from actual runs

Then remove leftovers like `check_setup.py` (if you want), confirm `.env` is ignored, and push to GitHub.

**Files:** create `README.md`; possibly delete `check_setup.py` and `note`

**Tasks**
- [ ] README: overview, install, env vars, usage, strategies, sample output, error handling, limitations, design decisions (from the list in `PLAN.md`)
- [ ] Run index + search for each strategy and paste the real output into the README
- [ ] `git init`, check that `git status` does **not** list `.env`
- [ ] First commit, create the GitHub repo, push

**How to test**
```
git status
git check-ignore .env
```
Expected: `.env` and `venv/` are not listed as files to commit, and `git check-ignore .env` prints `.env`. On GitHub, the README renders and no secrets are anywhere in the repo.

**Questions for you**
1. *Should the repository be public or private?* My recommendation is whatever the assignment's submission asks for. If it doesn't say, use private and add the reviewers as collaborators.
2. *Should the repo be just `part2` or the whole `jeen-assignment` folder (with part1)?* My recommendation is the whole folder if part1 should be submitted too, so the reviewers get one link.
3. *Should `check_setup.py` stay?* My recommendation is to keep it and mention it in the README as a quick connection test. It helps a reviewer check their `.env` before indexing.
