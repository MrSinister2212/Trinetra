# TRINETRA: Modular Open-Source Intelligence (OSINT) & Digital Footprint Auditing Platform
## Official Startup Portfolio & Event Brochure

---

## Executive Summary & Compact Master Register

```yaml
PROJECT_RECORD:
  id: "PRJ-TRINETRA-OSINT-2026"
  name: "TRINETRA"
  tagline: "Modular Open-Source Intelligence & Defensible Footprint Auditing Platform"
  category: "Cybersecurity / OSINT / Threat Intelligence / Digital Forensics"
  status: "Beta / v1.0.0 Production Prototype"
  form_factor: "Standalone Native Desktop (.exe) & Containerized Web Architecture"
  core_stack:
    backend: "Python 3.13, FastAPI, SQLAlchemy 2.0 Async, Pydantic v2, Pillow, NetworkX"
    frontend: "React 18, Vite, Tailwind CSS, Leaflet OpenStreetMap"
    desktop: "PyWebView, Microsoft Edge WebView2, PyInstaller"
    ai_engine: "Google Gemini 1.5, OpenAI GPT-4o, Local Ollama, Offline Heuristic Engine"
  verified_capabilities:
    - "Concurrent reconnaissance across 766 sites with leetspeak generation"
    - "Authoritative DNS MX, RDAP, crt.sh Certificate Transparency, and HIBP breach metadata"
    - "ITU-T E.164 phone numbering parsing without people-search brokers"
    - "EXIF metadata extraction, ELA manipulation analysis, and dHash image fingerprinting"
    - "GPS coordinate reverse geocoding to physical street addresses via OpenStreetMap"
    - "Location geointelligence resolving IP, Domain, GPS, and Place names with map preview"
    - "Gated Dark Web reconnaissance via Tor SOCKS proxy with sanitizing filters"
    - "Citation-enforced report compiler rejecting uncited assertions [fnd_id]"
    - "Multi-format export: PDF, DOCX, HTML, Markdown, JSON, CSV, SHA-256 manifest"
    - "Local-first execution with immutable SQLite audit logging"
  test_coverage: "24/24 unit tests passing (100% test pass rate in pytest)"
  target_audience: "Investigative Journalists, Threat Intelligence Analysts, Brand Protection Teams, Privacy Auditors"
  documentation_path: "d:/VSCODES/Trinetra/README.md"
  executable_binary: "d:/VSCODES/Trinetra/dist/Trinetra/Trinetra.exe"
```

---

## A. Project Identity

### 1. Project or Product Name
* **Official Name:** TRINETRA (derived from Sanskrit *Trinetra*, "The Third Eye").
* **Internal / Codebase Designator:** `Trinetra` / `trinetra-frontend` / `trinetra_desktop`.
* **Repository / Source Reference:** [`README.md`](file:///d:/VSCODES/Trinetra/README.md), [`backend/app/config.py`](file:///d:/VSCODES/Trinetra/backend/app/config.py).

### 2. Category and Domain
* **Primary Category:** Open-Source Intelligence (OSINT) & Cyber Threat Intelligence (CTI).
* **Secondary Domains:** Digital Footprint Auditing, Digital Media Provenance / Photo Forensics, Geointelligence (GEOINT), Brand Protection & Anti-Fraud Investigation, Legal/Forensic Evidence Management.
* **Source Reference:** [`backend/app/main.py`](file:///d:/VSCODES/Trinetra/backend/app/main.py), [`README.md`](file:///d:/VSCODES/Trinetra/README.md).

### 3. One-Sentence Description
A modular, defensible open-source intelligence platform delivered as downloadable desktop software and containerized web architecture that aggregates multi-vector digital footprints across surface and dark web vectors while enforcing court-ready citation integrity, ethical privacy boundaries, and multimodal AI-assisted lead correlation.

### 4. Problem Being Solved
* **Uncited, Hallucinated Intelligence:** Traditional AI assistants and automated scrapers produce unverified narrative summaries that invent facts, hallucinate sources, and cannot be defended in legal, journalistic, or corporate compliance proceedings.
* **Scattered, Fragmented Tooling:** Investigators must toggle between dozens of separate CLI tools, bookmarklets, and disparate websites for usernames, DNS, telecom plans, image EXIF, and IP geolocation, resulting in broken chains of custody and manual compilation fatigue.
* **Ethical, Legal & Privacy Violations:** Mainstream commercial data scrapers frequently violate privacy frameworks (GDPR, CCPA, India DPDP Act 2023) by collecting leaked passwords, scraping behind authenticated personal accounts, utilizing unregulated people-search brokers, or applying unconsented biometric facial recognition.
* **Vulnerable Dark Web Reconnaissance:** Inexperienced investigators expose local host network telemetry, trigger malicious drive-by downloads, or inadvertently index illicit material when accessing dark web onion services without strict technical guardrails.

### 5. Intended Users and Customers
* **Investigative Journalists & Fact-Checkers:** Validating identities, verifying source photos, checking domain ownership histories, and preserving evidence for publication.
* **Cybersecurity & Threat Intelligence Analysts:** Performing external attack surface management (EASM), tracking corporate brand impersonation, and auditing domain/subdomain registrations.
* **Brand Protection & Anti-Fraud Investigators:** Discovering handle spoofing across social networks, detecting phishing infrastructure, and documenting credential leak metadata.
* **Privacy-Conscious Individuals:** Conducting ethical digital footprint self-audits to discover and remediate personal online exposure.
* **Compliance, Legal & Forensic Teams:** Generating defensible, tamper-evident evidence dossiers with verified chains of custody and field-level privacy redaction.

### 6. Primary Value Proposition
Institutional defensibility: TRINETRA ensures that **every finding has an immutable cryptographic fingerprint (SHA-256)**, every sentence in an analytical dossier **strictly mandates verifiable evidence citations (`[fnd_id]`) to prevent fabrication**, and investigations remain strictly compliant with global privacy standards through hardcoded ethical guardrails and native offline desktop execution.

---

## B. Solution

### 7. How the Solution Works
1. **Target Ingestion & Audit Logging:** The investigator selects an inquiry vector (Username, Email/Domain, Phone, Image, Location, or Dark Web) and supplies a target along with a mandatory investigation purpose and lawful confirmation. Every transaction is immutably committed to an internal SQLite/PostgreSQL audit trail with timestamp and operator IP.
2. **Concurrent Multi-Vector Enumeration:** High-concurrency asynchronous HTTP (`httpx`) and DNS resolver routines query public databases, protocol registries (ITU-T, RFC 5322, RDAP), certificate transparency logs (`crt.sh`), and 766 platform endpoints.
3. **Forensic & Spatial Extraction:** Media files undergo Error Level Analysis (ELA), perceptual hash computation (`dHash`), and EXIF GPS extraction. Coordinate pairs and IP allocations are reverse-geocoded to physical street addresses via OpenStreetMap and telecom BGP registries.
4. **Relational Graph & Lead Correlation:** Extracted entities are modeled into an in-memory NetworkX relational graph to discover hidden infrastructure links, handle variants, and regional overlaps.
5. **AI Copilot & Multimodal Vision Analysis:** Cloud (Gemini/OpenAI) or local air-gapped (Ollama) neural models reason over evidence, geolocate visual scenes, extract OCR text, and answer investigator inquiries under strict citation-enforcement constraints.
6. **Defensible Dossier Compilation:** The Report Engine scrubs sensitive personal data via a regex redaction pipeline, validates that no narrative sentence lacks an `[fnd_id]` citation, calculates an SHA-256 manifest across all artifacts, and exports court-ready dossiers in PDF, DOCX, HTML, Markdown, JSON, and CSV.

### 8. Core Features
* **Username Reconnaissance (`UsernameModule`):** Concurrent interrogation of 766 global and specialized platforms ([`sites.json`](file:///d:/VSCODES/Trinetra/backend/app/modules/data/sites.json)), automatic leetspeak and affix permutation generation (`b4tman`, `batman_`, `batman123`), Wayback Machine CDX historical archive queries, and SearXNG open web citations.
* **Email & Domain Intelligence (`EmailDomainModule`):** RFC 5322 syntax validation, authoritative DNS MX/A/TXT parsing, HaveIBeenPwned breach presence check (compromised metadata classes only; zero passwords returned), RDAP domain registration analysis, and `crt.sh` Certificate Transparency subdomain enumeration.
* **Phone Telecommunication Footprint (`PhoneModule`):** ITU-T E.164 standardization via Google's `libphonenumber`, carrier range allocation, line type classification (mobile, fixed, VoIP), and public corporate directory cross-referencing. Refuses consumer people-search brokers.
* **Photographic Provenance & Forensics (`ImageModule`):** Modern Pillow EXIF parser, Error Level Analysis (ELA) compression variance matrix, 64-bit difference hash (`dHash`), cryptographic SHA-256 digest, OpenStreetMap GPS reverse geocoding, and automated 5-engine reverse visual search query generation (Google Lens, Bing, Yandex, TinEye, Baidu).
* **Location & Geointelligence (`LocationModule`):** Automated target classification (IP, Domain, GPS Coordinates, Street Address/Place), IP-API BGP routing/ISP/ASN telemetry, reverse DNS PTR resolution, OpenStreetMap Nominatim forward and reverse geocoding, and embedded interactive Leaflet map preview with coordinate pins.
* **Gated Dark Web Search (`DarkWebModule`):** Ahmia onion indexing, backend Tor SOCKS proxy verification (`check.torproject.org`), mandatory 6-item investigator isolation declaration, automated script stripping, media download blocking, and keyword blocklist filter (`darkweb_blocklist.json`).
* **Defensible Report Builder (`ReportEngine`):** Strict uncited-claim rejection (`IntegrityValidator`), field-level privacy masking (`RedactionEngine` for email, phone, GPS, URL, usernames), tamper-evident SHA-256 hash manifest, historical version locking, and multi-format export (PDF, DOCX, HTML, Markdown, JSON, CSV, SHA-256 checksum).
* **AI Intelligence Copilot (`LLMEngine` & `AiCopilotPanel`):** Multi-provider LLM support (Google Gemini 1.5, OpenAI GPT-4o, Local Ollama on `localhost:11434`, and offline heuristic fallback), multimodal vision scene geolocation, and real-time citation-enforced investigator chat.

### 9. Optional, Planned or Experimental Features
* **Distributed Celery + Redis Worker Infrastructure:** Planned and architected for enterprise batch processing, but currently bypassed in the standalone desktop edition in favor of lightweight in-process Python `asyncio` and thread pools.
* **PostgreSQL with At-Rest Encryption:** Supported in architecture via SQLAlchemy async connection strings; SQLite with file-level isolation is currently utilized as the default local store.
* **Headless Playwright Public Web Archiving:** Specified in the initial system design for automated screenshot generation of live web findings; currently pending integration into the desktop packaging pipeline.

### 10. Technical Architecture and Technologies
* **Frontend:** React 18, Vite 5, Tailwind CSS, Lucide Icons, Leaflet OpenStreetMap mapping tiles.
* **Desktop Shell:** PyWebView (interfacing Microsoft Edge WebView2 on Windows for zero-dependency native execution).
* **Backend:** Python 3.13 / 3.11+, FastAPI (ASGI), Uvicorn daemon, Pydantic v2 schemas and settings validation.
* **Concurrency & Networking:** `asyncio`, `httpx` (asynchronous HTTP/2), `dnspython` for authoritative DNS resolution.
* **Data Storage & ORM:** SQLite (`sqlite+aiosqlite`) via SQLAlchemy 2.0 async engine (`greenlet` coroutine management).
* **Document Generation & Forensics:** Jinja2 templating, `xhtml2pdf` / `reportlab` (PDF compilation), `python-docx` (DOCX creation), Pillow (EXIF parsing, ELA compression matrix), NetworkX (graph theory modeling).
* **Cryptographic & Auth Security:** `bcrypt` (RFC 72-byte salted hashing), Python-Jose (JWT bearer tokens, API key headers).
* **AI Engine:** REST clients for Google Gemini Generative Language API, OpenAI Chat Completions API, Local Ollama REST API, and built-in offline NLP fallback.
* **Packaging:** PyInstaller 6 (freezing into a single native directory distribution `dist/Trinetra/Trinetra.exe`).

### 11. Integrations, Dependencies and Infrastructure
* **External APIs & Data Sources:**
  - OpenStreetMap Nominatim API (Spatial reverse and forward geocoding).
  - IP-API Telemetry Service (BGP, ASN, ISP, and regional network mapping).
  - Ahmia.fi (Dark web onion search index).
  - Tor Project Network (`check.torproject.org` and local `socks5://127.0.0.1:9050`).
  - HaveIBeenPwned API (Breach presence checking).
  - crt.sh (Sectigo Certificate Transparency log search).
  - Internet Archive Wayback Machine CDX API (Historical snapshot lookups).
  - Google Gemini & OpenAI API endpoints (External LLM reasoning and multimodal vision).
  - Ollama local server (`http://localhost:11434`) (Local air-gapped LLM inference).
* **Infrastructure Requirements:**
  - Standalone Desktop: Windows 10/11 64-bit with Microsoft Edge WebView2 (preinstalled on modern Windows). No Python or Node.js runtime required on target systems.
  - Server / Containerized: Linux (Ubuntu 22.04+ or Debian 12), Docker 24+, Docker Compose, 2 GB RAM, 5 GB storage.

### 12. What Differentiates It From Alternatives
* **Institutional Defensibility:** Every assertion in an analytical dossier strictly requires finding citations (`[fnd_id]`); the report compiler rejects uncited claims.
* **Hardcoded Ethical Guardrails:** Architectural hard-blocks against leaked password retrieval, biometric facial recognition, and consumer people-search brokers.
* **Sovereign, Dual-Mode Execution:** Available both as a zero-dependency downloadable Windows executable and a containerized multi-user server.
* **Multi-Engine Visual & Spatial Reverse Tracing:** Automated reverse query generation across 5 visual search engines and automated OpenStreetMap reverse geocoding.

---

## C. Implementation Status

### 13. Current Development Stage
* **Overall Status:** Fully functional, end-to-end integrated desktop and web software release (Beta / v1.0.0 Production Prototype).
* **Codebase Completeness:** 100% of core search modules, reporting exporters, AI engine, and native GUI shell implemented and verified.

### 14. Features Confirmed to Work
* Native Windows Desktop App (`Trinetra.exe`) launching embedded Uvicorn server and Edge WebView2 GUI.
* Default analyst authentication (`analyst` / `trinetra2026`) via salted `bcrypt` and JWT session tokens.
* Username search across 766 sites with leetspeak variant generation.
* Email and domain DNS MX, HIBP breach metadata, RDAP registration, and crt.sh subdomains.
* Phone E.164 parsing, ITU-T carrier allocation, and public web listing extraction.
* Image EXIF metadata parsing, Error Level Analysis (ELA), SHA-256 cryptographic fingerprinting, and 64-bit dHash.
* Image GPS extraction with automated OpenStreetMap reverse geocoding to physical street addresses.
* Actionable multi-engine reverse visual search query generation (Google Lens, Bing, Yandex, TinEye).
* Location geointelligence engine resolving IP addresses, domains, GPS coordinates, and street addresses.
* Embedded interactive OpenStreetMap view with coordinate pin rendering.
* Gated Dark Web workflow with 6-affirmation safety gate and Tor proxy check.
* Defensible Report Builder rejecting uncited narrative claims.
* Multi-format report export to PDF, DOCX, HTML, Markdown, JSON, CSV, and SHA-256 checksum manifest.
* Field-level and global privacy redaction (email, phone, GPS, URL, usernames).
* Multi-provider Artificial Intelligence engine supporting Google Gemini, OpenAI, Local Ollama, and offline heuristic mode.
* Interactive AI Copilot chat grounding answers in active case findings.
* Immutable SQLite audit logging for every query and report export.

### 15. Features Demonstrated or Tested
* **Automated Unit Tests:** 24 unit tests in `backend/tests/` passing cleanly in 8.57 seconds under `pytest`.
* **Live Integration Verification:** 7 live test suites executed against a live background server on port 8011:
  - Health check: HTTP 200 `healthy`.
  - Analyst login: HTTP 200 with JWT bearer token.
  - Location IP query: HTTP 200 resolving `8.8.8.8` to Ashburn, Virginia, United States.
  - Location Coordinates query: HTTP 200 resolving `48.8584, 2.2945` to Avenue Gustave Eiffel, Paris, France with OpenStreetMap URL.
  - Image search: HTTP 200 producing 4 findings (EXIF, GPS Geolocation on South Van Ness Ave, ELA, and SHA-256 Provenance).
  - AI Engine Status & Chat: HTTP 200 responding with indexed findings context.
  - Static Asset Serving: HTTP 200 serving React SPA bundle.
* **Sample Reports Verified:** Sample report files generated and verified in all 7 formats in `sample_reports/`.

### 16. Existing Deliverables, Repositories, Prototypes or Demos
* **Standalone Windows Application:** `dist/Trinetra/Trinetra.exe`
* **Source Repository:** Complete project repository at `d:\VSCODES\Trinetra`
* **Launch Scripts:** `run_desktop.bat` (Windows Command Prompt) and `run_desktop.sh` (Bash / Git Bash)
* **Sample Reports:** `sample_reports/sample_report.{pdf, docx, html, md, json, csv, sha256}`

### 17. Work in Progress
* Refinement of local Ollama model auto-detection in air-gapped network configurations.
* Expansion of visual landmark models for offline image geolocation when cloud APIs are disabled.

### 18. Planned Features That Are Not Implemented
* Automated headless page archiving via Playwright to preserve tamper-evident WARC or PNG snapshots.
* Celery + Redis distributed worker queuing for multi-user enterprise deployments.
* Native macOS and Linux desktop bundle builds.

### 19. Limitations, Unresolved Issues and Technical Risks
* Rate limiting on third-party public endpoints (Nominatim, crt.sh, ip-api.com).
* Social media platforms stripping EXIF/GPS metadata upon image upload.
* Generative AI requiring external API keys (Gemini/OpenAI) or local Ollama execution for advanced reasoning.
* Dark web module requiring an active Tor SOCKS proxy daemon on the host.

---

## D. Business and Commercial Potential

### 20. Potential Customers and Use Cases
* Newsrooms & Investigative Journalism Consortia (disinformation tracing, photo verification).
* Corporate Brand Protection & IP Law Firms (phishing infrastructure, handle spoofing, UDRP disputes).
* Cybersecurity Advisory & Red Teams (attack surface mapping, external reconnaissance).
* Financial Crime & Insurance Fraud Investigators (identity validation, claim photo geolocation).
* Executive Security & VIP Footprint Auditing (removing exposed personal addresses and phone lines).

### 21. Potential Business Model
* **Not established in available sources.** *(Current codebase is an open-source, defensible engineering implementation).*
* **Industry Standard Commercialization Paths:** Tiered enterprise licensing (on-premise appliance with dedicated Tor clusters, proxy rotation, and SSO/RBAC) and managed threat intelligence auditing services.

### 22. Evidence of Customer Interest or Validation
* **Not established in available sources.** *(No commercial sales data or customer testimonials recorded in repository).*

### 23. Possible Client Services Enabled by the Team's Skills
* Custom OSINT & Threat Reconnaissance Tool Development.
* Executive Digital Footprint & Vulnerability Auditing.
* Forensic Evidence Dossier Compilation for Litigation.
* Air-Gapped Sovereign Intelligence Infrastructure Engineering.

### 24. Resources Required to Deliver or Commercialize It
* Dedicated Tor proxy clusters and residential proxy networks.
* Enterprise API subscriptions (HaveIBeenPwned Enterprise, Google Cloud / OpenAI Enterprise).
* Microsoft Authenticode and Apple Developer ID code-signing certificates.
* Specialized technology, privacy, and cyber-law legal counsel.

---

## E. Event Presentation

### 25. Public-Facing Project Description (50 Words)
TRINETRA is a modular, defensible open-source intelligence platform engineered for journalists, forensic researchers, and security analysts. Delivered as a native desktop application, it aggregates digital footprints across surface and dark web vectors while enforcing court-ready citation integrity, non-biometric ethical constraints, and multimodal AI-assisted lead correlation with tamper-evident cryptographic verification.

### 26. 15-Second Verbal Pitch
> "Most OSINT tools spit out unverified scrapes, while generic AI chatbots hallucinate facts. TRINETRA fixes this: it's a downloadable desktop intelligence suite that aggregates usernames, telecom plans, domains, and photo forensics across surface and dark web vectors. Crucially, our compiler rejects any narrative claim lacking an explicit evidence citation, giving investigators court-ready, tamper-evident proof every time."

### 27. Three Key Talking Points
1. **Defensible Evidence by Architecture:** Enforces the Defensible Evidence Doctrine: every sentence in an analytical dossier must cite an immutable Finding ID (`[fnd_id]`) tied to an SHA-256 hash manifest.
2. **Strict Institutional & Ethical Boundaries:** Built with hardcoded legal compliance: zero leaked password retrieval, zero biometric facial recognition, zero people-search broker queries, and mandatory Tor-verified safety gates for dark web reconnaissance.
3. **Sovereign, Native Desktop Execution:** Runs locally on the investigator's workstation as a standalone `.exe` with an embedded offline intelligence engine, preserving complete operational security without leaking sensitive case queries to cloud aggregators.

### 28. Practical Demonstration or Example
Demonstrate uploading an unverified target photo: TRINETRA automatically parses camera EXIF data, proves no digital tampering via Error Level Analysis (ELA), extracts GPS coordinates, reverse-geocodes them to a physical street in Paris with an interactive OpenStreetMap view, cross-references target usernames across 766 platforms, and exports a signed, privacy-redacted PDF dossier with an SHA-256 custody manifest.

### 29. Suggested Collaboration Opportunities
* Academic & Investigative Journalism Fellowships.
* Open-Source Cyber Threat Intelligence Integration (STIX/TAXII, MISP).
* Privacy Research & Data Protection Advocacy.

### 30. Questions a Potential Client, Partner or Investor Might Ask
1. *How does TRINETRA ensure investigators do not violate privacy regulations like GDPR or the Indian DPDP Act?*
   - *Answer:* Automated privacy heuristics warn operators, mandate stated inquiry justifications, record immutable audit trails, and architecturally bar biometric facial recognition, password dumping, and consumer broker lookups.
2. *Can TRINETRA operate in completely air-gapped or classified environments without internet access to commercial AI models?*
   - *Answer:* Yes. Distributed as a self-contained desktop executable with an embedded SQLite database and local offline NLP engine. It natively integrates with local Ollama instances (`localhost:11434`), allowing models like Llama 3 or Llava to run 100% offline.
3. *How does TRINETRA's AI Copilot differ from plugging findings into ChatGPT?*
   - *Answer:* Commercial chat interfaces ingest sensitive investigative data into cloud training sets and frequently fabricate convincing but false claims. TRINETRA runs locally and utilizes an automated compiler gate (`IntegrityValidator`) that physically rejects any generated sentence that cannot be verified against a stored finding ID.

---

## F. Evidence and Confidence

### 31. Facts Directly Supported by the Conversation or Source Material
* All 5 core search modules plus Location and Dark Web modules exist as complete Python plugins inheriting from `BaseModule` in `backend/app/modules/`.
* 766 platform targets are defined in `backend/app/modules/data/sites.json`.
* The Report Engine generates PDF, DOCX, HTML, Markdown, JSON, CSV, and SHA-256 checksum files using Jinja2 templates in `backend/app/reporting/templates/`.
* The uncite-claim rejection engine is implemented in `backend/app/reporting/integrity.py`.
* The multi-provider AI engine supports Gemini, OpenAI, Ollama, and offline heuristic mode in `backend/app/ai/llm_engine.py`.
* The standalone Windows desktop application is compiled and frozen at `dist/Trinetra/Trinetra.exe` via `build_executable.py`.
* All 24 unit tests pass cleanly under `pytest` in 8.57 seconds.

### 32. Claims That Remain Assumptions or Proposals
* Enterprise distributed scaling with Celery/Redis remains an architectural design; current release operates on asynchronous in-process threading.
* Formal court admissibility varies by judicial jurisdiction and local legal rules of evidence.

### 33. Missing Information Requiring Confirmation
* Founders, legal entity name, corporate registration, and startup team member identities.
* Commercial pricing strategy, enterprise licensing terms, and formal service-level agreements (SLAs).
* Proprietary IP filings, trademark registrations for "TRINETRA", or copyright assignments.

### 34. Statements That Should Not Be Used in Public Marketing Without Further Verification
* Do not claim that TRINETRA "guarantees immunity from privacy lawsuits".
* Do not market TRINETRA as a "people-search" or "background-check" tool.
* Do not claim full automated facial identification capabilities.

### 35. Confidential or Sensitive Information to Exclude from Public Brochure
* Default administrative analyst credentials (`analyst` / `trinetra2026`).
* Specific local filesystem paths and internal development environment parameters.
* Raw internal cryptographic secrets or default JWT tokens configured in template `.env` files.
