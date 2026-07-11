# AI-Powered Resume Builder

A web app for building an ATS-friendly resume tailored to a specific job
description -- without inventing experience, skills, or qualifications the
user doesn't have. 

## Status: Phase 3 complete

- [x] **Phase 1** -- Personal details, Education, Experience, Projects, and
      Skills forms.
- [x] **Phase 2** -- Upload an existing resume (.pdf/.docx/.txt) to pre-fill
      every section, as an alternative to entering everything manually.
      Anything the parser can't confidently map to a known section is kept
      verbatim, tagged with its original heading from the resume.
- [x] **Phase 3** -- Paste/upload a job description, extract its keywords,
      compare them against the resume, and show an ATS match score plus the
      matched and missing keywords.
- [ ] **Phase 4** -- AI-generated professional summary, AI rewrite of
      experience bullet points, AI project description enhancement, AI
      resume improvement suggestions.

## Tech Stack

Python, Streamlit, pypdf, python-docx, reportlab, pandas, scikit-learn,
OpenAI API (Phase 4). (The original stack listed spaCy for Phase 3; see the
Phase 3 notes below for why scikit-learn is used instead.)

## Project Structure

```
resume-builder/
├── app.py                  # Thin navigation shell (registers pages, no content of its own)
├── requirements.txt
├── models/
│   └── resume_data.py      # Dataclasses: the single source of truth for resume content
├── utils/
│   ├── session_manager.py  # Bridges Streamlit session_state and the data models
│   ├── validators.py       # Email / phone / URL format validation
│   ├── date_picker.py      # Month + Year dropdown pair for resume dates
│   ├── navigation.py       # Page order + custom top bar / Previous-Next buttons
│   ├── resume_parser.py    # Best-effort .pdf/.docx/.txt resume text extraction + parsing
│   └── ats_analyzer.py     # JD keyword extraction + resume match scoring
│   (docx_export.py, resume_generator.py added in later phases)
├── pages/                  # One Streamlit page per section (order controlled by utils/navigation.py, not filenames)
│   ├── 0_🏠_Home.py
│   ├── 1_📤_Upload_Resume.py
│   ├── 2_👤_Personal_Details.py
│   ├── 3_🎓_Education.py
│   ├── 4_💼_Experience.py
│   ├── 5_🚀_Projects.py
│   ├── 6_🛠️_Skills.py
│   ├── 7_📄_Review.py
│   └── 8_🎯_ATS_Match.py
├── assets/                 # Static assets (icons, sample data, etc.)
├── templates/              # Resume document templates (used by the exporter, Phase 4)
└── output/                 # Generated resume files (git-ignored)
```

## How It Works

### Phase 1 -- Manual entry

- `models/resume_data.py` defines dataclasses (`PersonalInfo`,
  `EducationEntry`, `ExperienceEntry`, `ProjectEntry`, `SkillCategory`,
  `ExtraSection`, `ResumeData`) that represent everything the user enters.
  This is the only place resume data is *defined* -- every other module
  reads/writes these objects rather than raw dicts.
- `utils/session_manager.py` stores one `ResumeData` instance in Streamlit's
  `st.session_state` for the duration of the browser session, and exposes
  small functions (`add_education`, `remove_experience`, `set_resume_data`,
  etc.) so pages never touch `session_state` directly.
- **Navigation is a top bar, not a sidebar.** `app.py` registers every page
  with `st.navigation(..., position="hidden")` -- purely so
  `st.switch_page()` and URL routing work -- and each page then calls
  `utils.navigation.render_top_nav()` to draw its own horizontal row of page
  buttons, plus `render_prev_next()` at the bottom for Previous/Left and
  Next/Right buttons. `utils/navigation.py`'s `PAGES` list is the single
  source of truth for page order, titles, and icons. (Streamlit's built-in
  `position="top"` was tried first, but with 8 pages it collapses most of
  them into an "N more" dropdown instead of showing them all -- rendering
  the bar manually avoids that.)
- Each file in `pages/` is a self-contained form for one resume section.
  Multi-entry sections (Education, Experience, Projects, Skills) let you add
  or remove entries freely. Each entry's fields live inside an `st.form`
  with its own **Save Entry** button -- nothing is written back to the data
  model until you click it, so typing never triggers a page rerun mid-edit.
  The only feedback shown is the success/error alert immediately after that
  click; there's no separate summary text elsewhere on the page.
- `utils/validators.py` checks that Email, Phone (must include a country
  code, e.g. `+1 555-123-4567`), and URL fields (LinkedIn, Portfolio, Project
  URL) are well-formed before they're saved; scheme-less URLs like
  `github.com/you` are auto-normalized to `https://github.com/you`.
- `utils/date_picker.py` renders Start/End Date as Month + Year dropdowns
  (resumes don't need a specific day) instead of free-text fields, storing
  them as a plain `"Aug 2019"` string. `is_start_after_end()` blocks saving
  an entry where the start date comes after the end date.
- GPA uses `st.number_input` so only numeric values can be entered at all.
- `pages/7_📄_Review.py` gives a read-only summary of everything entered so
  far, and flags which sections are still incomplete.

### Phase 2 -- Upload an existing resume

- The Home page offers two starting points: **Upload a Resume** or **Enter
  Details Manually**. Both eventually land on the same forms -- uploading
  just pre-fills them.
- `pages/1_📤_Upload_Resume.py` accepts a `.pdf`, `.docx`, or `.txt` file and
  calls `utils/resume_parser.py`.
- `resume_parser.py` is deliberately a **heuristic, rule-based parser**
  (regex + section-heading detection), not AI -- resume formatting varies
  too much for anything to be trustworthy without review:
  - `extract_text()` pulls raw text out of the file (`pypdf` for PDF,
    `python-docx` for DOCX).
  - `split_into_sections()` scans for short, standalone, Title Case or ALL
    CAPS lines as section headings, and buckets the text under each one.
    Headings that match common aliases ("Work Experience", "Employment
    History", etc.) map to a canonical section (education / experience /
    projects / skills / summary); anything else -- "Certifications",
    "Awards", "Languages", whatever the resume actually calls it -- is kept
    as-is under its **original heading** rather than being dropped.
  - Each canonical section has its own best-effort field parser
    (`parse_education`, `parse_experience`, `parse_projects`,
    `parse_skills`) that splits the block into per-entry chunks and pulls
    out dates, degree/job-title lines, GPA, bullet points, etc.
  - Dates are only ever converted to the app's `"Mon YYYY"` format when the
    month is explicit in the source text (e.g. `"Aug 2019"`, `"08/2019"`) --
    a bare year like `"2019"` is left blank rather than guessing a month
    that was never stated, in keeping with the app's "never invent" rule.
- Parsed data is loaded straight into the session's resume data via
  `set_resume_data()`, so it appears immediately on every page including
  Review -- the user explicitly asked uploading to fill everything in, and
  the parser only ever transcribes what the file actually says, never
  invents content. What isn't guaranteed is *accuracy*: parsing can misread
  a line, so every page's own **Save Entry** button is still there to let
  the user correct anything before treating it as final.
- Anything routed to an `ExtraSection` (unmatched heading) is shown on the
  Upload page immediately after parsing, and again on the Review page under
  **"Additional Information (from uploaded resume)"**, tagged with its
  original heading -- so nothing from the uploaded file is silently lost,
  even if the app couldn't figure out where it belongs.

### Phase 3 -- Job description matching (ATS)

- The **ATS Match** page lets the user paste or upload a job description and
  reports how well the resume matches it, using `utils/ats_analyzer.py`.
- **Why scikit-learn instead of spaCy.** The original stack listed spaCy for
  this phase, but spaCy needs a ~12MB language model downloaded at runtime,
  which is fragile in a sandboxed/offline environment. Phase 3 uses
  scikit-learn's TF-IDF for the similarity score plus a rule-based keyword
  extractor -- close to how many real ATS tools actually work, and with no
  runtime model download. (spaCy can be swapped in later for smarter
  noun-phrase extraction if desired.)
- **Keyword extraction** (`extract_keywords`) draws from two sources:
  (1) a curated **gazetteer** of real skills, tools, cloud platforms, certs,
  and soft skills found in the JD, and (2) **acronyms / tech-punctuation
  tokens** (AI, AWS, C++, Data+). Named products in ordinary title case
  (Azure, CompTIA, Python) are covered by the gazetteer, so we deliberately
  don't try to guess title-case proper nouns -- that keeps ordinary words
  that merely open a bullet ("Developing", "Strong") out of the results.
- **Matching** (`analyze`) checks each JD keyword against the resume's full
  searchable text (`ResumeData.searchable_text()` -- skills *and* experience
  bullets, projects, education, and uploaded extra sections), then reports:
  a **keyword-coverage score**, a **TF-IDF cosine-similarity score**, and
  the **matched** (green) and **missing** (red) keyword lists.
- Matching is literal, mirroring how real ATS software screens resumes: if a
  job asks for "Azure" and the resume only says "cloud", Azure shows as
  missing. Missing keywords are presented as information framed **"add these
  only if you genuinely have the experience"** -- the app never rewrites the
  resume or invents a skill.

## Setup

```bash
cd resume-builder
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. All data lives in the browser
session only (nothing is persisted to disk yet) -- refreshing the page or
closing the tab clears it.

## Rules Followed by Design

- The app never invents work experience, skills, or qualifications -- both
  manual entry and resume parsing only ever surface what the user actually
  wrote, and parsed data must still be reviewed and explicitly saved before
  it's kept.
- UI (`pages/`), data models (`models/`), and business logic (`utils/`) are
  kept in separate modules.
- Type hints are used throughout; important functions have docstrings.
