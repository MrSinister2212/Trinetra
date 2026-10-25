# 👁 TRINETRA: Modular Open-Source Intelligence (OSINT) Platform

> **"Trinetra"** (Sanskrit for *The Third Eye*) is a modular, defensible open-source intelligence platform designed for investigative journalists, security researchers, brand fraud investigators, and individuals conducting ethical personal footprint audits.

---

## 🏛 Platform Architecture & Core Tenets

TRINETRA delivers a production-grade reconnaissance and evidence-preservation environment where **every output is tied to a verifiable digital artifact, an immutable SHA-256 hash, and a stated investigation purpose**.

```
                           ┌───────────────────────────────┐
                           │    React 18 + Tailwind UI     │
                           │  Dark Mode / D3 Link Graph    │
                           └───────────────┬───────────────┘
                                           │ REST API (JWT / API Key)
                                           ▼
                           ┌───────────────────────────────┐
                           │       FastAPI Gateway         │
                           │ Audit Log / Rate Limit Engine │
                           └───────┬───────────────┬───────┘
                                   │               │
     ┌─────────────────────────────┴─────┐   ┌─────┴────────────────────────────┐
     │          OSINT Modules            │   │          Report Engine           │
     ├───────────────────────────────────┤   ├──────────────────────────────────┤
     │ 1. Username (500+ Sites + Leet)   │   │ • Uncited-Claim Rejector         │
     │ 2. Email & Domain (DNS/CT/HIBP)   │   │ • Privacy Redaction Engine       │
     │ 3. Phone (ITU-T / Public Footprint│   │ • Relational Link Graph (Nx)     │
     │ 4. Image Provenance (EXIF/ELA)    │   │ • Chain of Custody & Hashes      │
     │ 5. Gated Dark Web (Tor/Ahmia)     │   │ • Exporters: PDF, DOCX, HTML, MD │
     └───────────────────────────────────┘   └──────────────────────────────────┘
```

---

## ⚖️ Legal & Ethical Framework (Mandatory Compliance)

TRINETRA is built with mandatory, automated architectural constraints to prevent misuse, stalking, or illegal data aggregation:

1. **Lawful Basis & Mandatory Purpose**:
   - Every single search request requires a stated investigation purpose (e.g. brand protection, journalist inquiry, authorized corporate audit).
   - All queries and report compilations are recorded in an **immutable audit log** containing investigator ID, target, timestamp, IP address, and stated justification.

2. **Strict Public Data Boundary**:
   - **No Credential Stuffing**: Never stores, searches, or returns leaked passwords. Breach monitors report that an incident occurred and compromised metadata classes only.
   - **No Private Login Scraping**: All data is retrieved via public APIs, public DNS, standard HTTP status codes, and open web registries.
   - **No People-Search Brokers**: The phone module strictly checks telecommunication numbering allocations (ITU-T E.164) and open web citations. It refuses to query consumer background-check brokers or cellular location data.
   - **Zero Biometric Facial Recognition**: The image module analyzes technical provenance (camera EXIF, GPS metadata, Error Level Analysis). It refuses to perform facial recognition or match faces to identities.

3. **Privacy Regulations (GDPR, DPDP Act 2023, CCPA Awareness)**:
   - Automated heuristic scanner warns investigators whenever a query resembles a private individual's full name, personal phone, or consumer email address (e.g. `@gmail.com`).
   - Personal footprint audits require confirmation of consent or self-assessment.

4. **Dark Web Safety Gate & Strict Blocklist**:
   - Gated behind 6 mandatory isolation declarations and backend Tor network verification (`check.torproject.org`).
   - Hard-blocked categories: CSAM, weapons, drug markets, hitman services, and hacking-for-hire. Content matching these categories is automatically dropped and logged.
   - Results are rendered as metadata only. Scripts are stripped and all media downloads are blocked.

---

## 📦 Installed Modules

| Module | Scope & Methodology | Key Capabilities |
| :--- | :--- | :--- |
| **1. Username Recon** | Platform presence across 500+ sites (`sites.json`) | Leetspeak & affix variant generation (`b4tman`, `batman_`, `batman123`), Wayback Machine CDX archive search, and open search engine web mentions. |
| **2. Email & Domain** | Mail exchange & infrastructure enumeration | RFC 5322 syntax validation, authoritative DNS MX/A/TXT records, HIBP breach check (no passwords), RDAP registration lookups, and crt.sh Certificate Transparency logs. |
| **3. Phone Footprint** | Telecommunication numbering plans & public listings | Google `libphonenumber` E.164 parsing, carrier range assignment, line type classification, and open public web listings without querying broker databases. |
| **4. Image Provenance** | Photographic forensics & metadata | EXIF header extraction, GPS coordinate parsing, Error Level Analysis (ELA) for digital manipulation triage, and perceptual/SHA-256 hash indexing. |
| **5. Dark Web Intelligence** | Ahmia onion indexing & leak mentions | Operates through Tor SOCKS proxy, strips scripts, blocks media downloads, and enforces hard-block keyword filtering. |
| **6. Report Builder** | Defensible evidence synthesis | Jinja2 templates for **Technical Reports**, **Executive Summaries**, **Personal Footprint Audits**, and **Brand Fraud Dossiers**. Exports to **PDF**, **DOCX**, **HTML**, **Markdown**, **JSON**, **CSV**, and digital **SHA-256 Checksum** files. |

---

## 🔒 Report Integrity & Evidence Preservation

The Report Builder implements strict institutional evidentiary standards:
- **Uncited-Claim Rejection**: Every single sentence in an executive summary or analyst narrative must cite one or more stored finding IDs (e.g. `[fnd_usr_01]`). The report compiler strictly refuses to render any claim that lacks explicit evidence citations.
- **Privacy Redaction Panel**: Field-level or global masking for emails (`a***e@domain.com`), phone numbers (`+1 ***-***-2671`), GPS coordinates (`[REDACTED_GPS_COORDINATES]`), usernames, and host URLs before export.
- **Tamper-Evident SHA-256 Manifest**: Computes cryptographic digests for all included findings and artifacts.
- **Version Locking**: Final reports can be locked. Any subsequent updates automatically clone the dossier and increment the version counter, preserving historical custody.

---

## 🚀 Quick Start with Docker Compose

Ensure Docker and Docker Compose are installed:

```bash
# 1. Clone repository
git clone https://github.com/your-org/trinetra.git
cd trinetra

# 2. Configure environment
cp .env.example .env

# 3. Launch all services (Backend, Frontend, Redis, Tor SOCKS Proxy)
docker-compose up --build -d
```

- **Frontend Application:** `http://localhost:3000`
- **FastAPI Documentation:** `http://localhost:8000/docs`
- **Tor SOCKS Proxy:** `localhost:9050`
- **Default Analyst Credentials:**
  - Username: `analyst`
  - Password: `trinetra2026`

---

## 💻 Local Developer Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Generate 500+ site definitions
python backend/generate_sites.py

# Run the test suite
pytest -v

# Start FastAPI server
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Vite runs at http://localhost:3000 with proxy to backend port 8000
```

---

## 🧪 Running Automated Tests

TRINETRA features comprehensive unit test coverage with mocked HTTP responses:

```bash
pytest -v
```

Tests include:
- `test_username.py`: Site existence signatures, error detection, variant generation.
- `test_email_domain.py`: RFC syntax, MX routing, HaveIBeenPwned breach validation without passwords, crt.sh CT logs.
- `test_phone.py`: E.164 parsing, carrier detection, absence of personal names/photos.
- `test_image.py`: EXIF tags, GPS coordinate parsing, Error Level Analysis (ELA), absence of facial recognition.
- `test_darkweb.py`: 6-box Safety Gate rejection, server-side Tor verification rejection, hard-block keyword filtering, script sanitization.
- `test_reporting.py`: Uncited-claim rejection, redaction correctness, SHA-256 hash manifest integrity, version locking, and multi-format exports (PDF, DOCX, HTML, MD, JSON, CSV).

---

## 📁 Sample Generated Reports

Sample multi-format reports synthesized from mock forensic data are available in [`sample_reports/`](./sample_reports):
- [`sample_report.html`](./sample_reports/sample_report.html) (Interactive standalone HTML)
- [`sample_report.pdf`](./sample_reports/sample_report.pdf) (Print-ready PDF with case watermarks)
- [`sample_report.docx`](./sample_reports/sample_report.docx) (Editable Microsoft Word document)
- [`sample_report.md`](./sample_reports/sample_report.md) (GitHub-flavored Markdown)
- [`sample_report.json`](./sample_reports/sample_report.json) (Machine-readable schema)
- [`sample_report.csv`](./sample_reports/sample_report.csv) (Tabular findings export)
- [`sample_report.sha256`](./sample_reports/sample_report.sha256) (Cryptographic verification checksum)

---

## 📄 License & Attribution

TRINETRA is released under the **Apache License 2.0**. Investigators using TRINETRA are responsible for ensuring that all reconnaissance operations comply with local and international privacy statutes.
