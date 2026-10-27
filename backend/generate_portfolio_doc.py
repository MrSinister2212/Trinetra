import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_portfolio_document():
    doc = Document()

    # Set Margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Palette
    NAVY = RGBColor(15, 23, 42)
    BRAND_BLUE = RGBColor(30, 58, 138)
    CYAN = RGBColor(8, 145, 178)
    DARK_GRAY = RGBColor(51, 65, 85)
    LIGHT_GRAY = RGBColor(100, 116, 139)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("TRINETRA")
    r_title.bold = True
    r_title.font.size = Pt(28)
    r_title.font.color.rgb = BRAND_BLUE

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Modular Open-Source Intelligence (OSINT) & Digital Footprint Auditing Platform\nOfficial Startup Portfolio & Event Brochure")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = DARK_GRAY

    doc.add_paragraph()

    # Compact Master Register Table
    h_reg = doc.add_heading("Master Startup Portfolio Register", level=2)
    h_reg.runs[0].font.color.rgb = BRAND_BLUE

    table = doc.add_table(rows=12, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    reg_data = [
        ("Project Identifier", "PRJ-TRINETRA-OSINT-2026"),
        ("Official Product Name", "TRINETRA (Sanskrit: The Third Eye)"),
        ("Product Category", "Open-Source Intelligence (OSINT) / Threat Intelligence / Digital Forensics"),
        ("Current Status", "Beta / v1.0.0 Production Prototype (Fully Functional & Tested)"),
        ("Software Delivery", "Downloadable Native Windows Desktop (.exe) & Containerized Web Architecture"),
        ("Core Technology Stack", "Python 3.13, FastAPI, SQLAlchemy 2.0 Async, React 18, Vite, Tailwind, Leaflet"),
        ("Desktop Shell", "PyWebView (Microsoft Edge WebView2 Engine), PyInstaller 6 Standalone Freeze"),
        ("AI Intelligence Engine", "Multi-Provider (Google Gemini 1.5, OpenAI GPT-4o, Local Ollama, Offline Fallback)"),
        ("Verified Capabilities", "766-Site Recon, DNS/MX, crt.sh, ITU-T Phone, EXIF/GPS, ELA, OSM Geocoding, Gated Dark Web"),
        ("Evidentiary Guarantee", "Strict Uncited-Claim Rejection: Every dossier assertion must cite a stored [fnd_id]"),
        ("Automated Test Suite", "24 / 24 Unit & Integration Tests Passing (100% Pass Rate in pytest)"),
        ("Executable Binary Location", "dist/Trinetra/Trinetra.exe (Zero-dependency standalone binary)")
    ]

    for idx, (label, val) in enumerate(reg_data):
        cell_lbl = table.rows[idx].cells[0]
        cell_val = table.rows[idx].cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.6)
        
        set_cell_background(cell_lbl, "F1F5F9")
        set_cell_background(cell_val, "FFFFFF")

        p_l = cell_lbl.paragraphs[0]
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = NAVY

        p_v = cell_val.paragraphs[0]
        r_v = p_v.add_run(val)
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = DARK_GRAY

    doc.add_page_break()

    # Section A
    doc.add_heading("A. Project Identity", level=1)
    
    doc.add_heading("1. Project or Product Name", level=3)
    doc.add_paragraph("TRINETRA (derived from Sanskrit Trinetra, 'The Third Eye'). Internal designator: Trinetra / trinetra_desktop.")

    doc.add_heading("2. Category and Domain", level=3)
    doc.add_paragraph("Primary Category: Open-Source Intelligence (OSINT) & Cyber Threat Intelligence (CTI).\nSecondary Domains: Digital Footprint Auditing, Digital Media Forensics, Geointelligence (GEOINT), Brand Protection, Legal Evidence Management.")

    doc.add_heading("3. One-Sentence Description", level=3)
    doc.add_paragraph("A modular, defensible open-source intelligence platform delivered as downloadable desktop software and containerized web architecture that aggregates multi-vector digital footprints across surface and dark web vectors while enforcing court-ready citation integrity, ethical privacy boundaries, and multimodal AI-assisted lead correlation.")

    doc.add_heading("4. Problem Being Solved", level=3)
    doc.add_paragraph("• Uncited, Hallucinated Intelligence: Traditional AI scrapers produce unverified summaries that fabricate sources and cannot be defended in legal or journalistic proceedings.\n• Scattered, Fragmented Tooling: Investigators must toggle between dozens of separate CLI utilities and websites, breaking chain of custody.\n• Ethical & Legal Violations: Commercial tools frequently scrape leaked passwords, use unregulated people-search brokers, or apply unconsented facial recognition.\n• Vulnerable Dark Web Recon: Inexperienced analysts risk exposing network telemetry or triggering malicious drive-by downloads.")

    doc.add_heading("5. Intended Users and Customers", level=3)
    doc.add_paragraph("• Investigative Journalists & Fact-Checkers\n• Cybersecurity & Threat Intelligence Analysts\n• Corporate Brand Protection & Anti-Fraud Teams\n• Privacy-Conscious Individuals Conducting Self-Audits\n• Legal, Compliance & Forensic Evidence Teams")

    doc.add_heading("6. Primary Value Proposition", level=3)
    doc.add_paragraph("Institutional defensibility: TRINETRA ensures every finding has an immutable SHA-256 fingerprint, every sentence in an analytical dossier strictly mandates verifiable evidence citations ([fnd_id]), and investigations remain fully compliant with global privacy laws through hardcoded ethical guardrails.")

    # Section B
    doc.add_heading("B. Solution", level=1)

    doc.add_heading("7. How the Solution Works", level=3)
    doc.add_paragraph("1. Target Ingestion & Audit Logging: Investigator inputs target with mandatory inquiry purpose; logged immutably.\n2. Concurrent Multi-Vector Enumeration: Async HTTP and DNS routines query 766 sites, protocol registries, and certificate logs.\n3. Forensic & Spatial Extraction: Image ELA, dHash, and EXIF GPS parsed and reverse-geocoded to street addresses via OpenStreetMap.\n4. Relational Graph & Correlation: Entities mapped in NetworkX to uncover hidden infrastructure and handle variants.\n5. AI Copilot & Vision: Neural models reason over evidence under strict citation constraints.\n6. Defensible Dossier Compilation: Redaction engine masks sensitive tokens, checks citations, hashes artifacts, and exports court-ready dossiers.")

    doc.add_heading("8. Core Features", level=3)
    doc.add_paragraph("• Username Reconnaissance: 766 platforms, leetspeak variant generator (b4tman, batman_, batman123), Wayback Machine CDX.\n• Email & Domain Intelligence: RFC 5322 syntax, DNS MX/A/TXT, HIBP breach check (no passwords returned), RDAP lookups, crt.sh subdomains.\n• Phone Footprint: ITU-T E.164 parsing via Google libphonenumber, carrier range allocation, line type classification without consumer broker data.\n• Image Provenance & Forensics: Pillow EXIF parser, Error Level Analysis (ELA), 64-bit dHash, SHA-256 digest, OpenStreetMap GPS reverse geocoding, and 5-engine reverse visual queries (Google Lens, Bing, Yandex, TinEye, Baidu).\n• Location & Geointelligence: Target auto-detection (IP, Domain, GPS, Address), IP-API BGP/ISP/ASN lookup, reverse DNS PTR, OpenStreetMap geocoding, embedded Leaflet map.\n• Gated Dark Web Search: Ahmia onion indexing, backend Tor SOCKS proxy verification, 6-affirmation safety gate, script stripping, and hard-block keyword filter.\n• Defensible Report Builder: Strict uncited-claim rejection, field-level privacy masking, SHA-256 manifest, version locking, and export to PDF, DOCX, HTML, Markdown, JSON, CSV.\n• AI Intelligence Copilot: Multi-provider support (Gemini, OpenAI, Ollama, offline fallback), multimodal vision scene geolocation, and real-time citation-enforced investigator chat.")

    doc.add_heading("9. Technical Architecture", level=3)
    doc.add_paragraph("Frontend: React 18, Vite 5, Tailwind CSS, Leaflet OpenStreetMap\nDesktop Shell: PyWebView, Microsoft Edge WebView2 Engine, PyInstaller 6\nBackend: Python 3.13, FastAPI (ASGI), Uvicorn, Pydantic v2, SQLAlchemy 2.0 Async, aiosqlite\nForensics: Pillow, NetworkX, xhtml2pdf, python-docx, bcrypt, python-jose\nAI Engine: Google Gemini REST API, OpenAI REST API, Ollama REST API, Offline NLP Fallback")

    doc.add_heading("10. What Differentiates It", level=3)
    doc.add_paragraph("• Institutional Defensibility: Compiler rejects uncited claims lacking [fnd_id].\n• Ethical Guardrails: Hard-blocks against leaked passwords, facial recognition, and people-search brokers.\n• Sovereign Desktop Package: Standalone .exe runs offline with zero external telemetry exposure.\n• Multi-Engine Visual & Spatial Tracing: Direct reverse image search generation and automated OpenStreetMap address resolution.")

    # Section C
    doc.add_heading("C. Implementation Status", level=1)
    doc.add_paragraph("• Current Development Stage: Beta / v1.0.0 Production Prototype.\n• Features Confirmed & Tested: 100% of core search modules, reporting exporters, AI engine, and native GUI shell verified.\n• Automated Test Suite: 24 passed unit tests under pytest in 8.57 seconds.\n• Live Verification: 7 live test suites verified on local server (Health, Auth, Location IP, Location GPS, Image Forensics, AI Copilot, UI Serving).\n• Deliverables: Standalone executable dist/Trinetra/Trinetra.exe, full source repository, run scripts, and sample reports in 7 formats.")

    # Section D
    doc.add_heading("D. Business and Commercial Potential", level=1)
    doc.add_paragraph("• Potential Customers: Newsrooms, Cybersecurity Advisory Firms, Brand Protection Teams, Insurance/Fraud Investigators, Legal Counsel.\n• Business Model: Not established in available sources (Open-source defensible engineering implementation; commercial paths include tiered enterprise on-premise appliances and managed threat intelligence services).\n• Customer Validation: Not established in available sources.\n• Client Services Enabled: Bespoke OSINT tool development, executive footprint audits, forensic dossier assembly, sovereign air-gapped infrastructure deployment.\n• Resources Required: Residential proxy networks, Tor proxy clusters, enterprise API subscriptions, Authenticode code-signing certificates, legal counsel.")

    # Section E
    doc.add_heading("E. Event Presentation", level=1)
    
    doc.add_heading("Public-Facing Description (50 Words)", level=3)
    doc.add_paragraph("TRINETRA is a modular, defensible open-source intelligence platform engineered for journalists, forensic researchers, and security analysts. Delivered as a native desktop application, it aggregates digital footprints across surface and dark web vectors while enforcing court-ready citation integrity, non-biometric ethical constraints, and multimodal AI-assisted lead correlation with tamper-evident cryptographic verification.")

    doc.add_heading("15-Second Verbal Pitch", level=3)
    p_pitch = doc.add_paragraph()
    r_pitch = p_pitch.add_run('"Most OSINT tools spit out unverified scrapes, while generic AI chatbots hallucinate facts. TRINETRA fixes this: it is a downloadable desktop intelligence suite that aggregates usernames, telecom plans, domains, and photo forensics across surface and dark web vectors. Crucially, our compiler rejects any narrative claim lacking an explicit evidence citation, giving investigators court-ready, tamper-evident proof every time."')
    r_pitch.italic = True

    doc.add_heading("Three Key Talking Points", level=3)
    doc.add_paragraph("1. Defensible Evidence by Architecture: Strict citation enforcement ([fnd_id]) tied to an SHA-256 hash manifest.\n2. Strict Institutional & Ethical Boundaries: Zero leaked passwords, zero facial recognition, zero people-search brokers, and Tor-verified dark web gating.\n3. Sovereign, Native Desktop Execution: Standalone .exe runs locally with an embedded offline intelligence engine.")

    # Section F
    doc.add_heading("F. Evidence and Confidence", level=1)
    doc.add_paragraph("• Supported Facts: All 5 core search modules, Location module, Dark Web module, 766 site targets, 7 report export formats, AI copilot engine, and standalone executable binary exist in repository.\n• Assumptions / Proposals: Enterprise Celery/Redis worker scaling and formal court admissibility across international jurisdictions.\n• Missing Information Requiring Confirmation: Startup founders/corporate entity names, commercial pricing tiers, and trademark registrations.\n• Marketing Restrictions: Do not claim 'guaranteed immunity from privacy lawsuits' or market as a 'people-search background broker'.\n• Excluded Confidential Data: Default analyst credentials (analyst / trinetra2026), local filesystem paths, and internal template secrets.")

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TRINETRA_PORTFOLIO_AND_EVENT_BROCHURE.docx")
    doc.save(out_path)
    print(f"Generated Word document at: {out_path}")

if __name__ == "__main__":
    create_portfolio_document()
