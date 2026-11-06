# CoachPath on Google Play: free-stack roadmap

Written 6 Nov 2026. Assumes:
- a GitHub Student Developer Pack;
- Figma Pro;
- a paid Play Console personal account ($25 already paid).

Prices and limits change often. Recheck each one on the vendor's own page before you rely on it.

## 1. The decision: ship the web app we already have as an Android app

CoachPath is already a working Next.js + FastAPI product, so we do not rewrite it in Kotlin or React Native. We wrap it with a **Trusted Web Activity (TWA)**:
- A TWA is Google's own way to publish a PWA on Play. It runs the site full-screen in Chrome, with no URL bar.
- [Bubblewrap](https://github.com/GoogleChromeLabs/bubblewrap) or [PWABuilder](https://www.pwabuilder.com) generates the signed `.aab` file for free.
- Every Vercel deploy updates the app instantly. Only changes to the Android shell need a new store upload.

| Option | Cost | Effort | When |
|---|---|---|---|
| **TWA (PWA in Play)** | Free | ~1 week | **Now** |
| Capacitor | Free | 2–3 weeks: needs a static export, and our dynamic routes and auth need rework | Only if we need native APIs a PWA can't reach |
| Expo / React Native rewrite | Free tier, about 15 Android builds a month | 2–3 months | Later, if the app outgrows the web |

## 2. The free stack

| Need | Use | Free because |
|---|---|---|
| Frontend hosting | **Vercel Hobby**, which we already use | Free tier |
| Backend API, always on | **Heroku Basic dyno**, paid with the Student Pack credit (reported as $13 a month for 24 months) | Student Pack |
| Fallback API host | **Azure App Service** on the $100 Azure for Students credit | Student Pack |
| Database | **Neon Postgres free**: 1 GB per project, scales to zero, no expiry | Free tier |
| Resume files | **Cloudflare R2**: 10 GB, no egress fees | Free tier |
| AI | Groq free tier, protected by our per-user limits (PR #7) | Free tier |
| Domain | Namecheap, Name.com or .TECH domain | Student Pack |
| Design and store graphics | Figma Pro | You have it |
| IDE and AI coding help | JetBrains all-products licence. Copilot student sign-ups were reported paused in April 2026, so check yours. | Student Pack |
| Push notifications | Web Push. TWAs pass notifications through to Android. | Free |
| CI | GitHub Actions on a public repo, or the Pro minutes | Student Pack |

**Why not Render free for the API?**
- A free Render service sleeps after 15 minutes idle and takes about a minute to wake. Play reviewers and new users will see that as "the app is broken".
- A free Render Postgres database is deleted after 30 days, plus a 14-day grace period.
- If our production database is a free Render Postgres, moving to Neon is **urgent**.

## 3. Play Store rules we must meet

- **12 testers for 14 days.** A personal account made after Nov 2023 needs a closed test with **at least 12 testers opted in for 14 continuous days** before it can apply for production. Pausing the track restarts the clock. Start recruiting testers in week 1.
- **Target API 36.** From 31 Aug 2026, new apps must target Android 16 (API 36). Set this in Bubblewrap's config.
- **Account deletion** inside the app **and** on a public web URL. This is planned Phase 16 work, which is now a launch blocker.
- **Privacy policy URL**, the **Data safety** form (we collect resumes and career data, and AI processes them), the content rating questionnaire and the target audience.
- **Digital Asset Links:** `/.well-known/assetlinks.json` on the Vercel domain. Without it the app shows a URL bar and looks like a website.
- **Store listing:** a 512px icon, a 1024×500 feature graphic, at least 2 phone screenshots, a short description (80 chars) and a full description. Build these in Figma.

## 4. The roadmap

### Week 0: finish the safety work (in progress)
- Merge PR #7. Set up R2 in Render.
- Move the database to Neon if it is on free Render Postgres.
- Move the API to the Heroku student credit, or to Azure, so it never sleeps.

### Weeks 1–2: make CoachPath a real PWA
- Add `manifest.webmanifest`: name, icons from Figma, `display: standalone`, the theme colour from the Look D tokens.
- Add a service worker with an offline fallback page. A TWA must not show Chrome's "no connection" page.
- Mobile pass on every app page:
  - a bottom nav or drawer instead of the sidebar below 768px;
  - tap targets of 44px or more;
  - no hover-only actions.
- Make login persist across app restarts, and make Google sign-in work inside the TWA.
- **Recruit 12+ testers now:** classmates, a college club, family. Collect their Gmail addresses.

### Week 3: Android shell plus the closed test
- Run `bubblewrap init --manifest https://<domain>/manifest.webmanifest`, then `bubblewrap build`, which produces the `.aab` and a signing key.
- **Back up the signing key and its password in two places.** If you lose them, you can never update the app.
- Enrol in Play App Signing, and publish `assetlinks.json` with both SHA-256 fingerprints: yours and Google's.
- Play Console:
  - create the app;
  - complete the store listing, privacy policy, Data safety and content rating;
  - upload to **Closed testing** and invite the testers.
- **The 14-day clock starts here.** Keep building in the meantime: web deploys reach testers without a new upload.

### Weeks 3–5: build the remaining product phases during testing
- Phase 16 first, because Play requires it: account deletion and data export.
- Then Phase 12 (pipeline tracker), Phase 14 (interview prep) and Phase 15 (readiness), as planned in `next-phases-plan.md`.
- Ask testers for feedback in-app. Fix crashes and confusing flows.

### Week 5: production
- After 14 days with 12+ testers, apply for production access. Answer Google's questions about the test honestly.
- Roll out in stages: 20%, then 50%, then 100%.
- Add free error monitoring. Sentry's free developer plan is enough.

### After launch
- Use web push for "your roadmap task is due" and "new matching jobs".
- Consider Capacitor or Expo only if a feature truly needs native APIs: a home-screen widget, calendar sync, offline AI.

## 5. Costs

| Item | Cost |
|---|---|
| Play Console | $25, already paid |
| Hosting, database, storage, AI, domain | $0, using free tiers and Student Pack credits |
| Risk | Credits expire, after about 24 months for Heroku. Note the dates. |

## Sources
- [GitHub Student Developer Pack](https://education.github.com/pack) (official). Summaries: [geek.college](https://www.geek.college/i/github-student-developer-pack), [creditforstartups](https://creditforstartups.com/students/github-student-developer-pack), [perkstack](https://perkstack.co/blog/github-student-pack-guide)
- [Play target API requirement](https://developer.android.com/google/play/requirements/target-sdk)
- [Play testing requirements for new personal accounts](https://support.google.com/googleplay/android-developer/answer/14151465), [12-tester guide](https://www.testerscommunity.com/blog/google-play-closed-testing-requirements-2026)
- [Render free tier](https://render.com/docs/free)
- [Neon free plan limits](https://neon.com/faqs/free-plan-limits-and-quotas)
- [Cloudflare R2 free tier](https://agentdeals.dev/vendor/cloudflare-r2)
- [Expo plans](https://docs.expo.dev/billing/plans/), [Expo free tier 2026](https://agentdeals.dev/vendor/expo)
- [Capacitor web-app guide](https://capgo.app/blog/how-easy-is-it-to-make-web-app-into-mobile-app-with-capacitor/)
