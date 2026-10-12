# Young's Collision Center — Website

Plain Node.js/Express app: serves the static site out of `public/` and handles the contact and
authorization forms, plus the careers page (job postings + applications), by emailing submissions
through Gmail SMTP.

```
site_deploy/
├── server.js             the backend entry point — static file serving + the two form routes,
│                         and wires in careers.js
├── careers.js            careers page API: public postings list + apply form, plus the admin
│                         dashboard's login and CRUD routes
├── careers-db.js         tiny JSON-file "database" for job postings and applications
├── package.json
├── .env.example          copy to .env for local testing (never commit the real .env)
├── public/               the actual website (HTML/CSS/images/video/fonts) — this is what's served
│   ├── careers.html       the public careers page (generated — see site-source/build_careers.py)
│   └── admin/careers.html  the admin dashboard for editing careers content (hand-written, not generated)
└── site-source/          Python templates that generate public/*.html — edit these, not the HTML directly
```

## 1. Generate a Gmail App Password

The forms send email through youngscollision@gmail.com's own SMTP, using an **App Password**
(a 16-character code), not the real account password.

1. Sign in to the Google Account that owns youngscollision@gmail.com.
2. Turn on 2-Step Verification if it isn't already on (Google requires this for App Passwords):
   https://myaccount.google.com/security
3. Go to https://myaccount.google.com/apppasswords
4. Create a new App Password (name it something like "Website Contact Form"), and copy the
   16-character code it gives you. You won't be able to see it again after this step.

Keep that code handy for step 3 below.

## 2. Push this code to GitHub

From inside this `site_deploy` folder:

```bash
git init
git add .
git commit -m "Initial site build"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

(If you already have a repo for this, skip `git init`/`remote add` and just commit + push to it.)

**If you're uploading through GitHub's website instead of using these git commands** (drag-and-drop
via "Add file → Upload files"): do **not** upload the `node_modules/` or `data/` folders if you see
them in your local copy — they're meant to stay off GitHub (a `.gitignore` file in this folder
tells the git *command line* to skip them automatically, but that file has no effect on the
website's drag-and-drop uploader, so it's on you to just not select those two folders when
dragging files in).

## 3. Deploy on Railway

1. In Railway, **New Project → Deploy from GitHub repo**, and pick the repo you just pushed.
2. Railway will detect the Node app automatically (via `package.json`) and build it.
3. Go to the project's **Variables** tab and add:
   - `GMAIL_USER` = `youngscollision@gmail.com`
   - `GMAIL_APP_PASSWORD` = the 16-character code from step 1
   - `TO_EMAIL` = `youngscollision@gmail.com` (or wherever you want submissions to land — can be
     different from GMAIL_USER)
   - `ADMIN_PASSWORD` = a password of your choosing — this logs into the careers admin dashboard
     at `/admin/careers.html`. Pick something you wouldn't mind a stranger guessing poorly at;
     it's the only thing protecting applicants' resumes and contact info.
   - `SESSION_SECRET` = any long random string (run `openssl rand -hex 32` locally, or just mash
     the keyboard for 40+ characters) — this signs the admin login cookie. Changing it later logs
     everyone out, which is harmless, just slightly annoying.
   - `DATA_DIR` = `/data` — see **4. Add a Volume for careers data** below before setting this;
     without a matching Volume mounted at that same path, this step alone won't persist anything.
4. Railway redeploys automatically whenever you push to `main` after this.
5. Once it's deployed, open the Railway-provided URL and test the forms end-to-end — submit each
   one and confirm the email actually arrives, including a test careers application.

## 4. Add a Volume for careers data

Job postings and submitted applications (plus uploaded resumes/cover letters) are stored as files
on disk, not in a database. Railway's filesystem is **not** persistent by default — every time you
deploy, the disk resets to whatever's in the GitHub repo, which would silently wipe out every
posting and application. A **Volume** is Railway's name for a small persistent disk that survives
deploys, and it's required for this feature to actually keep data.

1. In the Railway project, open the service and go to its **Settings** tab.
2. Find **Volumes** and click **New Volume** (or **Add Volume**, depending on Railway's current
   UI — it's a small additional cost, a couple cents a month at this size, billed like the rest of
   Railway's usage-based pricing).
3. Set the **mount path** to exactly `/data` — this has to match the `DATA_DIR` variable from step
   3 above, or the app will be writing to one place and reading from another.
4. Redeploy. From then on, postings and applications survive every future deploy.

If this step is skipped, the site still works, but every deploy quietly resets the careers page
back to "no postings, no applications" — worth doing before the careers page is actually in use.

## 5. Point the domain at Railway

1. In the Railway project, go to **Settings → Networking → Domains** and add
   `youngscollisioncenter.com` (and `www.youngscollisioncenter.com` if you want both).
2. Railway will show you a DNS record (usually a CNAME, sometimes an A/ALIAS depending on the
   domain's root) to add at wherever the domain is currently registered/managed.
3. Add that record, then wait for DNS to propagate (can take anywhere from a few minutes to a
   few hours). Railway will show the domain as verified once it sees the record.
4. Don't cancel/change the old hosting until the new domain is confirmed working — keeps you from
   any downtime during the switch.

## Using the careers admin dashboard

The careers page (job postings, the headline/intro text above them, and whether to accept
general/future-interest applications) is edited through a small admin dashboard — no code changes
or redeploys needed for day-to-day use.

1. Go to `youngscollisioncenter.com/admin/careers.html` and log in with the `ADMIN_PASSWORD` you
   set in Railway's Variables tab.
2. **Page Settings** — the headline and intro paragraph shown at the top of the careers page, plus
   a checkbox for whether the page invites general applications (useful for "not hiring right now,
   but send us your resume anyway" mode) versus only showing current open postings.
3. **Job Postings** — add, edit the status of, or delete individual postings. Each posting has a
   status of **Open** (actively hiring, shown with an "Open" badge), **General Only** (not an
   active opening, but still listed so people can apply with that role in mind — shown as "Open to
   Future Openings"), or **Closed** (hidden from the public page entirely, without deleting the
   posting or its past applications).
4. **Applications** — everyone who's applied, newest first, with their contact info, message, and
   download links for their resume and cover letter (if they attached one). Each one has a status
   dropdown (new / reviewed / contacted / etc. — whatever labels make sense) and a delete button.

This page is marked `noindex` so search engines won't list it, but it isn't otherwise hidden — the
`ADMIN_PASSWORD` is what actually keeps it private, so treat it like any other password.

Applicants also get emailed to `TO_EMAIL` automatically the moment they apply, so the dashboard is
for browsing/managing applications over time, not the only way to find out about a new one.

## Editing content later

Don't hand-edit the files in `public/*.html` — they're generated. Instead:

1. Edit the relevant file in `site-source/` (e.g. `build_services.py` for the Services page,
   `partials.py` for the header/footer/nav that's shared across every page).
2. From inside `site-source/`, run:
   ```bash
   python3 build_all.py
   ```
3. Commit and push both the `site-source/` changes and the regenerated `public/` files — Railway
   redeploys on push automatically.

No build step runs on Railway itself for the HTML — `public/` is committed as plain static files;
Railway only runs `npm install` + `node server.js` for the Express server.

## Local testing (optional)

```bash
npm install
cp .env.example .env   # then fill in GMAIL_APP_PASSWORD
npm start
```

Visit http://localhost:3000 — the whole site and both forms work locally exactly like they will
on Railway.

## What's next / not yet done

- **Railway Volume for careers data**: not yet provisioned — see **4. Add a Volume for careers
  data** above. Without it, postings and applications get wiped on every deploy. Do this before
  publicizing the careers page (e.g. before Jeff starts sending people to it).
- **`ADMIN_PASSWORD` / `SESSION_SECRET`**: not yet set in Railway — the careers admin dashboard
  won't work at all until these are added in the Variables tab (see step 3 above).
- **Google Analytics**: intentionally not wired up yet — add the tracking snippet after the site
  is live on the real domain, not before (so early testing traffic doesn't pollute the data).
- **Google Maps embed on the Contact page**: uses a no-API-key embed URL, so it should just work
  once live — worth a quick visual check after deploy since it couldn't be tested in the sandbox
  this was built in (no outbound internet there).
