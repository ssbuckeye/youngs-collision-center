# Young's Collision Center — Website

Plain Node.js/Express app: serves the static site out of `public/` and handles the two forms
(`/api/contact`, `/api/authorization`) by emailing submissions through Gmail SMTP.

```
site_deploy/
├── server.js          the whole backend — static file serving + the two form routes
├── package.json
├── .env.example        copy to .env for local testing (never commit the real .env)
├── public/              the actual website (HTML/CSS/images/video/fonts) — this is what's served
└── site-source/         Python templates that generate public/*.html — edit these, not the HTML directly
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

## 3. Deploy on Railway

1. In Railway, **New Project → Deploy from GitHub repo**, and pick the repo you just pushed.
2. Railway will detect the Node app automatically (via `package.json`) and build it.
3. Go to the project's **Variables** tab and add:
   - `GMAIL_USER` = `youngscollision@gmail.com`
   - `GMAIL_APP_PASSWORD` = the 16-character code from step 1
   - `TO_EMAIL` = `youngscollision@gmail.com` (or wherever you want submissions to land — can be
     different from GMAIL_USER)
4. Railway redeploys automatically whenever you push to `main` after this.
5. Once it's deployed, open the Railway-provided URL and test both forms end-to-end — submit each
   one and confirm the email actually arrives.

## 4. Point the domain at Railway

1. In the Railway project, go to **Settings → Networking → Domains** and add
   `youngscollisioncenter.com` (and `www.youngscollisioncenter.com` if you want both).
2. Railway will show you a DNS record (usually a CNAME, sometimes an A/ALIAS depending on the
   domain's root) to add at wherever the domain is currently registered/managed.
3. Add that record, then wait for DNS to propagate (can take anywhere from a few minutes to a
   few hours). Railway will show the domain as verified once it sees the record.
4. Don't cancel/change the old hosting until the new domain is confirmed working — keeps you from
   any downtime during the switch.

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

- **Google Analytics**: intentionally not wired up yet — add the tracking snippet after the site
  is live on the real domain, not before (so early testing traffic doesn't pollute the data).
- **Google Maps embed on the Contact page**: uses a no-API-key embed URL, so it should just work
  once live — worth a quick visual check after deploy since it couldn't be tested in the sandbox
  this was built in (no outbound internet there).
