# Productions by AG — portfolio site

Live: https://productionsbyag.vercel.app

A fast, static site. No frameworks, no `npm install` — just Python (already on every Mac) to build it.

## Edit content

All words, projects, links and emails live in **`content.py`**. Change what you need, then rebuild:

```bash
python3 build.py
```

That regenerates the finished site in `public/`. Commit and push — Vercel publishes `public/` automatically.

## Preview locally

```bash
python3 serve.py
```

Then open http://localhost:4173

## Where things are

| Path | What it is |
| --- | --- |
| `content.py` | All site text and project data |
| `build.py` | Turns `content.py` into HTML pages |
| `static/css/site.css` | Styles |
| `static/js/site.js` | Menu, showreel player, video players, work filters, both forms |
| `static/brand/` | Logo files — AG mark (SVG, dark and light) and full lockups (PNG, dark and light) |
| `static/img/` | Images (JPEG, ~1600px wide max) |
| `api/contact.js` | Vercel function that emails both forms to you |
| `public/` | Generated site — don't edit by hand |

## Adding a project image or stills

1. Save a JPEG to `static/img/` (e.g. `scil-school.jpg`, ideally 1600px wide, plus an 800px `scil-school-sm.jpg`).
2. In `content.py`, set the project's `"cover": "scil-school"`.
3. For a stills gallery: `"stills": [{"img": "scil-school-1", "alt": "Classroom, morning light"}]`.
4. For a film: add `{"vimeo": "123456789", "title": "...", "note": "...", "poster": "file.jpg"}` to `"films"`.

## Visual design

The homepage uses a layered CSS camera lens. Pointer movement changes the viewing angle. The Lens spacing control moves the rings along their optical axis and supports touch and keyboard input. Automatic motion follows the visitor's reduced-motion preference. Typography uses DM Sans, Georgia and IBM Plex Mono.

## The two forms

- **Start a project** (`/start`) — the project brief: type, timeline, details.
- **Contact** (`/contact`) — email, socials, and a short general note.

Both post to `/api/contact`, which sends via [Resend](https://resend.com).
In Vercel → Project → Settings → Environment Variables add:

- `RESEND_API_KEY` — your Resend API key
- `CONTACT_TO` — optional, defaults to productionbyag@gmail.com

Until the key is set, each form shows a one-click "send by email instead" link with the message pre-filled, so no enquiry is lost.
