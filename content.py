"""
All the words, links and project data for the site live in this file.

Edit anything here, then run:   python3 build.py
That regenerates the finished site in the `public/` folder.
"""

SITE = {
    "name": "Productions by AG",
    "url": "https://productions-by-ag.vercel.app",
    "tagline": "Films, documentaries, and visual stories — Lahore.",
    "description": (
        "Abdul Ghaffar is a Lahore-based filmmaker crafting brand films, founder "
        "stories, and documentary work for companies that want their story told properly."
    ),
    "email": "productionbyag@gmail.com",
    "linkedin": "https://www.linkedin.com/in/abdul-ghaffar-khan-799929252/",
    "instagram": "https://www.instagram.com/productionsbyag/",
    "location": "Lahore, Pakistan",
    "year": 2026,
    "showreel_vimeo": "1197639477",
}

NAV = [
    ("Work", "/work"),
    ("About", "/about"),
    ("Services", "/services"),
    ("Contact", "/contact"),
]

FOOTER_NAV = [
    ("Work", "/work"),
    ("About", "/about"),
    ("Services", "/services"),
    ("Collaborations", "/collaborations"),
    ("Contact", "/contact"),
]

# ---------------------------------------------------------------- Home

HOME = {
    "headline": ["Films and content", "for brands", "worth remembering."],
    "subhead": (
        "A Lahore-based filmmaker crafting brand films, founder stories, and documentary "
        "work for companies that want their story told properly."
    ),
    "featured_heading": "Stories I've stayed long enough to find.",
    "featured": ["alkhidmat", "total-parco", "care-pharmacy", "tedx-gcu"],
    "trusted_heading": "Trusted alongside.",
    "trusted": ["Sony", "Nikon", "Sigma", "Insta360", "Hollyland", "TEDx GCU", "Alkhidmat Foundation"],
    "about_heading": "The person behind the work.",
    "about_text": (
        "I'm Abdul Ghaffar — a filmmaker and photographer in Lahore. Six years and more than "
        "fifty documentaries in, I still work the same way: stay with a real person and a real "
        "story long enough to find what's actually there, then make the film that does it justice."
    ),
}

DISCIPLINES = [
    {"id": "brand-films", "name": "Brand Films", "line": "Founder stories & flagship films"},
    {"id": "documentary", "name": "Documentary", "line": "Cause storytelling for NGOs"},
    {"id": "social-content", "name": "Social Content", "line": "Monthly production retainers"},
    {"id": "photography", "name": "Photography", "line": "Editorial & event coverage"},
]

CTA = {
    "heading": "Have something worth filming?",
    "line": "Tell me about your project — I respond within two working days.",
    "button": "Start a project",
}

# ---------------------------------------------------------------- Work

WORK_INTRO = (
    "A selection of recent films, campaigns, and documentary work — brand cinema, "
    "founder portraits, and field reporting."
)
WORK_FILTERS = ["Brand", "Documentary", "Founder", "Event", "Education"]

# Each project gets its own case-study page at /work/<slug>.
# Sections (brief / approach / outcome / films / stills / making) only appear
# when they have content, so a project can start small and grow.
PROJECTS = [
    {
        "slug": "alkhidmat",
        "client": "Alkhidmat Foundation",
        "title": "Alkhidmat Foundation — Flood Relief",
        "short": "Flood Relief",
        "type": "Documentary",
        "year": "2023",
        "role": "Director, DP, Editor",
        "cover": "alkhidmat",
        "standfirst": (
            "Documentaries built to move donors — staying with families through the 2022 "
            "floods, from displacement to the return home."
        ),
        "brief": (
            "Alkhidmat Foundation needed films for its flood-relief work — not reports, not a "
            "montage of statistics. Something that could sit with one family long enough that "
            "a viewer would feel the scale of what was lost, and act."
        ),
        "brief_quote": "Don't make a film about a disaster. Make a film about a family that lived through one.",
        "approach": (
            "I spent days in flood-affected areas of southern Punjab, filming families in "
            "temporary shelters and the volunteers rebuilding around them. No voiceover. No "
            "statistics on screen. Just the people, the silence between them, and a soundtrack "
            "that doesn't tell viewers how to feel."
        ),
        "outcome": (
            "The films were used across Alkhidmat's fundraising channels. The working relationship "
            "grew into more than fifty short documentaries — a body of work that became the "
            "foundation of my documentary practice."
        ),
        "films": [
            {"vimeo": "1197307917", "title": "The Deluge", "note": "A story of endurance, hope, and the ongoing journey to rebuild.", "poster": "film-deluge.jpg"},
            {"vimeo": "1197642234", "title": "The Outlands", "note": "The unheard voices of Jalalpur Pirwala.", "poster": "film-outlands.jpg"},
        ],
        "stills": [],
        "making": [
            ("Client", "Alkhidmat Foundation"),
            ("Role", "Director, Director of Photography, Editor"),
            ("Format", "Documentary · 4K · 16:9"),
            ("Locations", "Southern Punjab — Jalalpur Pirwala"),
            ("Relationship", "50+ short documentaries · 2023 – present"),
        ],
    },
    {
        "slug": "total-parco",
        "client": "Total Parco",
        "title": "Total Parco — “Fueling Progress”",
        "short": "Fueling Progress",
        "type": "Brand",
        "year": "2024",
        "role": "Senior Editor & Designer",
        "cover": "total-parco",
        "standfirst": "“Fueling Progress” — a brand campaign about the people behind the pump. Innovate. Serve. Grow.",
        "brief": "",
        "approach": "",
        "outcome": "",
        "films": [],
        "stills": [],
        "making": [
            ("Client", "Total Parco"),
            ("Campaign", "Fueling Progress"),
            ("Role", "Senior Editor & Designer"),
            ("Deliverables", "Brand campaign film & key visuals"),
        ],
    },
    {
        "slug": "care-pharmacy",
        "client": "Care Pharmacy",
        "title": "Care Pharmacy",
        "short": "Brand film & social",
        "type": "Brand",
        "year": "2024",
        "role": "Senior Editor & Designer",
        "cover": "care-pharmacy",
        "cover_square": True,
        "standfirst": "A brand film and an ongoing run of social content for a healthcare brand that wanted to sound human.",
        "brief": "",
        "approach": "",
        "outcome": "",
        "films": [],
        "stills": [],
        "making": [
            ("Client", "Care Pharmacy"),
            ("Role", "Senior Editor & Designer"),
            ("Deliverables", "Brand film · social reels · campaign design"),
        ],
    },
    {
        "slug": "uzair-siddiqui-podcast",
        "client": "Uzair Siddiqui Podcast",
        "title": "Uzair Siddiqui Podcast",
        "short": "Founder content",
        "type": "Founder",
        "year": "2024",
        "role": "Editor & Designer",
        "cover": None,
        "standfirst": "Long-form conversations shaped into founder-led video and short-form cuts.",
        "brief": "",
        "approach": "",
        "outcome": "",
        "films": [],
        "stills": [],
        "making": [
            ("Client", "Uzair Siddiqui"),
            ("Role", "Editor & Designer"),
            ("Deliverables", "Podcast episodes · short-form clips · thumbnails"),
        ],
    },
    {
        "slug": "tedx-gcu",
        "client": "TEDx GCU",
        "title": "TEDx GCU",
        "short": "Event coverage",
        "type": "Event",
        "year": "2023",
        "role": "Lead Photographer & Videographer",
        "cover": "tedx",
        "standfirst": "Photo and video coverage of TEDxGCU Lahore — from the stage to the moments between talks.",
        "brief": "",
        "approach": "",
        "outcome": "",
        "films": [],
        "stills": [],
        "making": [
            ("Event", "TEDxGCU, Lahore"),
            ("Role", "Lead Photographer & Videographer"),
            ("Deliverables", "Event photography · highlight video · social edits"),
        ],
    },
    {
        "slug": "scil-school",
        "client": "Scil School",
        "title": "Scil School",
        "short": "Education content",
        "type": "Education",
        "year": "2024",
        "role": "Senior Editor & Designer",
        "cover": None,
        "standfirst": "Brand and admissions content for a school — showing the classroom as it really is.",
        "brief": "",
        "approach": "",
        "outcome": "",
        "films": [],
        "stills": [],
        "making": [
            ("Client", "Scil School"),
            ("Role", "Senior Editor & Designer"),
            ("Deliverables", "Brand content · social video"),
        ],
    },
]

SHORT_CUTS = [
    {"vimeo": "1197647820", "title": "Hollyland", "note": "Creator partnership", "poster": "cut-hollyland.jpg"},
    {"vimeo": "1197641621", "title": "Infinix", "note": "Short-form product film", "poster": "cut-infinix.jpg"},
]

# ---------------------------------------------------------------- About

ABOUT = {
    "headline": "The person behind the films.",
    "intro": (
        "I'm Abdul Ghaffar, a filmmaker and photographer based in Lahore. I take on a small "
        "number of projects at a time — brand films, founder stories, documentaries, and "
        "editorial content for people and organisations who care how their story is told. "
        "Most content is made quickly and forgotten quickly; I work the opposite way. "
        "Fewer projects. More time on each. Better films."
    ),
    "roles": "Director · Cinematographer · Documentary filmmaker",
    "story": [
        "I started in computer science. By my second semester at university, I was more interested in cameras than code — but that systems thinking never left, and it's how I work.",
        "I'm now pursuing filmmaking at the National College of Arts (NCA), Lahore, formalising the documentary and cinematic practice I've built over the last six years.",
        "I've worked across photography, video editing, documentary direction, and brand content — for healthcare brands, education institutions, fuel companies, fashion labels, and humanitarian organisations, including 50+ short documentaries for the Alkhidmat Foundation.",
        "That documentary lens — staying with a real person and a real story long enough to find what's actually there — is what I bring to everything.",
    ],
    "stats": [
        ("Since", "2019", "First commission"),
        ("Years", "06", "In film & content"),
        ("Docs", "50+", "For Alkhidmat"),
        ("Based", "LHE", "Lahore, Pakistan"),
    ],
    "principles": [
        ("Small projects, deeply done.", "Each project gets my full attention. I'd rather turn work away than rush it."),
        ("One point of contact.", "You work directly with me, first call to delivery — no handoffs."),
        ("The work is the proposal.", "I'd rather show than pitch."),
    ],
}

# ---------------------------------------------------------------- Services

SERVICES_INTRO = {
    "heading": "What I do.",
    "subhead": "Four disciplines, one point of contact on every project.",
}

SERVICES = [
    {
        "id": "brand-films",
        "name": "Brand Films & Founder Stories",
        "covers": "Flagship brand films, founder-led storytelling",
        "runs": ["3–7 min", "1–3 shoot days", "3–5 week delivery"],
        "body": "Cinematic films built around the story behind a brand, a founder, or a company milestone — for websites, launches, anniversaries, investor decks, and social cut-downs.",
        "process": [
            "Research, interviews and creative direction",
            "1–3 shoot days, original cinematography and lighting",
            "Edit, colour and sound design",
            "Master film plus social cut-downs",
        ],
        "example": ("Total Parco — “Fueling Progress”", "/work/total-parco"),
    },
    {
        "id": "documentary",
        "name": "Documentary & Cause Storytelling",
        "covers": "Field documentaries for NGOs and causes",
        "runs": ["Field shoots", "2–5 days", "4–6 week delivery"],
        "body": "Documentary work for NGOs, foundations, and CSR programmes — for fundraising, donor reporting, and public awareness. Built around real people, not staged scenarios.",
        "process": [
            "Subject research and pre-shoot interviews",
            "Field shooting, 2–5 days depending on scope",
            "Long-form edit plus shorter campaign cuts",
            "Optional stills from the same shoot",
        ],
        "example": ("Alkhidmat — Flood Relief", "/work/alkhidmat"),
    },
    {
        "id": "social-content",
        "name": "Social Content Production",
        "covers": "Ongoing content for brands",
        "runs": ["Monthly retainer", "3-month minimum", "8–15 deliverables / month"],
        "body": "Reels, photography, and short-form video for Instagram, LinkedIn, and TikTok — consistent, high-quality output without hiring an in-house team.",
        "process": [
            "Monthly planning call",
            "One production day per month",
            "8–15 finished pieces — reels, photos, short-form video",
            "Two rounds of revisions per deliverable",
        ],
        "example": ("Care Pharmacy", "/work/care-pharmacy"),
    },
    {
        "id": "photography",
        "name": "Event & Editorial Photography",
        "covers": "Event coverage and editorial stills",
        "runs": ["Same-day social edits", "Full gallery in 7 working days"],
        "body": "Coverage for conferences, launches, summits, and brand activations — fast turnaround, editorial-grade output.",
        "process": [
            "Shot list agreed before the day",
            "Single or multi-day coverage",
            "Same-day social-ready selects",
            "Full edited gallery within 7 working days",
        ],
        "example": ("TEDx GCU", "/work/tedx-gcu"),
    },
]

PROCESS = [
    ("A conversation.", "A 30-minute call to understand what you're making and whether I'm the right fit."),
    ("A proposal.", "Within a week: scope, timeline, deliverables, and investment. No 40-page decks."),
    ("The work.", "Once we're aligned and the deposit is in, pre-production starts."),
]

# ---------------------------------------------------------------- Collaborations

COLLAB_INTRO = {
    "heading": "In good company.",
    "subhead": "Partnerships, programmes, and bodies of work I've been part of.",
}

COLLAB_GROUPS = [
    {
        "title": "Camera & creator brands",
        "cols": ("Brand", "Collaboration"),
        "rows": [
            ("Sony", "Sony Pakistan", "Creator partnerships & photowalk programmes"),
            ("Nikon", "", "Creator partnerships & photowalk programmes"),
            ("Sigma", "Sigma Pakistan", "Creator partnerships & photowalk programmes"),
            ("Insta360", "", "Creator partnerships & photowalk programmes"),
            ("Hollyland", "", "Creator / gear partnership"),
        ],
    },
    {
        "title": "Events & institutions",
        "cols": ("Collaboration", "Role"),
        "rows": [
            ("TEDx GCU", "TEDxGCU", "Lead photographer / videographer"),
            ("Photographic Society of Pakistan", "PSOP", "Social media manager"),
            ("Sigma Pakistan events", "", "Event manager, photographer / videographer"),
        ],
    },
    {
        "title": "Humanitarian & social impact",
        "cols": ("Organisation", "Work"),
        "rows": [
            ("Alkhidmat Foundation", "", "50+ short documentaries · Director, DP, Editor · 2023 – present"),
        ],
    },
    {
        "title": "Brand & social content",
        "note": "Through agency teams at IM Corporation and Luminogics, and as an independent filmmaker.",
        "cols": ("Brand", "Work"),
        "rows": [
            ("Mera Brand Pakistan", "", "Social content · Editor & Designer"),
            ("Total Parco", "", "Brand campaign"),
            ("Care Pharmacy", "", "Brand film"),
            ("PWS Inmol", "", "Brand content"),
            ("Umeed", "", "Documentary / content"),
            ("Scil School", "", "Brand / education content"),
            ("LIBF", "", "Brand content"),
        ],
    },
]

# ---------------------------------------------------------------- Contact

CONTACT = {
    "heading": "Tell me about what you're making.",
    "subhead": "I respond to every enquiry within two working days. The first call is 30 minutes — you talk, I listen.",
    "project_types": ["Brand film", "Founder story", "Documentary", "Social content retainer", "Event / photography", "Something else"],
    "timelines": ["Flexible", "Within a month", "1–3 months", "3+ months"],
    "hours": "Monday – Friday · 10:00 – 18:00 PKT",
    "travel": "Available across Pakistan and the region",
}
