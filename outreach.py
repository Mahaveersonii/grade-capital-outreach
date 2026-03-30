#!/usr/bin/env python3
"""
Grade Capital — Automated Guest Post Outreach System
Runs daily via GitHub Actions | Built for Mahaveer Soni, Grade Capital
"""

import os
import csv
import time
import random
import requests
import smtplib
import datetime
import re
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import google.generativeai as genai

# ============================================================
# CONFIGURATION (all values from GitHub Secrets)
# ============================================================
GEMINI_API_KEY   = os.environ.get('GEMINI_API_KEY', '')
SERPER_API_KEY   = os.environ.get('SERPER_API_KEY', '')
SENDER_EMAIL     = os.environ.get('SENDER_EMAIL', 'mahaveer@grade.capital')
EMAIL_PASSWORD   = os.environ.get('EMAIL_PASSWORD', '')
SMTP_HOST        = 'smtp.gmail.com'
SMTP_PORT        = 587
ORGS_PER_DAY     = random.randint(10, 15)
LOG_FILE         = 'sent_log.csv'

# ============================================================
# GRADE CAPITAL MASTER CONTEXT
# (used to brief Gemini for every article it writes)
# ============================================================
GRADE_CAPITAL_CONTEXT = """
=== ABOUT GRADE CAPITAL ===
Grade Capital is India's first fully regulated, professionally managed crypto derivatives fund.
Website: https://grade.capital
Founded: January 1, 2023 | Inception NAV: $10.00 USDT
Current NAV: $132.15 USDT (Feb 20, 2026) | Total Return: +1,221.50% | CAGR: 127.67%
Track Record: 1,147 consecutive days of daily-published NAV
Sharpe Ratio: 1.38 | Sortino Ratio: 3.43 | Calmar Ratio: 3.56
ISO 9001:2015 Certified | PMLA Compliant | FIU Registered (VA00032718)
Custody: Fireblocks MPC institutional custody (same infrastructure as 1,800+ global institutions)
KYC: HyperVerge (700M+ verifications globally)

=== YEAR-BY-YEAR PERFORMANCE ===
2023: +215.20% (Bitcoin recovery from 2022 lows)
2024: +94.48%  (ETF approvals, Bitcoin halving year)
2025: +99.84%  (Volatile — option hedging deployed, drawdown contained)
2026 YTD: +7.88% (2 months | geopolitical tension — Iran war)

=== KEY DIFFERENTIATOR — TAX ADVANTAGE ===
Spot crypto in India: Flat 30% tax under Section 115BBH — no deductions, no loss set-off, no carry-forward
Grade Capital uses derivatives → classified as speculative business income (Sections 43(5) & 73)
Tax at applicable income slab rate — NOT the punitive 30% flat VDA rate
Losses deductible | 4-year loss carry-forward | All fund expenses deductible
This is NOT a loophole — it is a fundamental classification difference written in the Income Tax Act

=== INVESTMENT APPROACH ===
Derivatives-only (futures + options) — NOT spot crypto
All-weather: profits in rising, falling AND sideways markets
Active option hedging — demonstrated drawdown control in 2025 (NAV fell $90.35→$75.83, then recovered to $132.15)
CME crypto derivatives: 424,000 contracts/day in Nov 2025 = $13.2B notional, up 78% YoY

=== THE FOUNDING STORY ===
November 2016 — India's demonetisation. While 86% of India's currency became worthless paper overnight,
Bitcoin processed transactions without interruption. This contrast planted the seed for Grade Capital.
The founder spent 2016–2021 studying derivatives, crypto cycles, and institutional risk management
across one full crypto cycle — the 2017 euphoria, 2018 crash, and 2022 collapse.
Grade Capital launched January 1, 2023 with a $10 NAV and one mission:
give Indian investors access to crypto the right way — regulated, managed, tax-efficient, transparent.

=== MACRO DATA POINTS FOR ARTICLES ===
- BlackRock Bitcoin ETF: $115B+ AUM in first year — fastest ETF growth in financial history
- Goldman Sachs survey: 71% of institutional asset managers plan to increase crypto exposure in 12 months
- Rockefeller Capital Management: increased Bitcoin-linked position by 146%
- Amundi (Europe's largest asset manager, $2.8T AUM): increased crypto exposure 373% to $641M
- South Korea NPS (world's 3rd largest pension fund): increased Bitcoin position 20% to $83.2M
- JPMorgan research: explicitly comparing Bitcoin vs Gold as competing stores of value
- SWIFT: integrating blockchain with 11,500+ banks across 200+ countries (Chainlink partnership, Nov 2024)
- Bitcoin during Iran war crisis (Feb–Mar 2026): +17% while Nifty, S&P fell and gold retreated from ATH
- CME crypto derivatives: $13.2B notional daily volume, up 78% YoY (Nov 2025)

=== INDIA-SPECIFIC DATA POINTS ===
- India has 100M+ crypto users — among top 3 globally
- IFSCA (GIFT City regulator) published 55-page RWA tokenization consultation paper (Feb 2025)
- JPMorgan Kinexys: $1.5T+ processed, live with HDFC, ICICI, Axis, Yes, IndusInd banks in GIFT City
- Polygon built by Indian founders (ex-Deloitte), backed by Sequoia India + SoftBank ($450M)
- Telangana: India's first state Technical Guidance Note on Asset Tokenization (Dec 2023)
- Terazo: India's first regulated tokenized real estate project ($7M fund, Polygon blockchain, IFSCA sandbox)
- Section 115BBH: 30% flat tax on spot VDA gains — unchanged in Budget 2026
- Section 194S: 1% TDS on all crypto transfers above ₹10,000

=== EDUCATIONAL CONTENT FROM GRADE CAPITAL'S RESEARCH ===
Chapter 1: Why crypto is no longer optional for financial professionals to understand
Chapter 2: How blockchain works — distributed ledger, 50,000+ Bitcoin nodes, Proof of Work vs Proof of Stake
Chapter 3: India's VDA tax framework — Section 115BBH, 194S, CARF by 2027, professional CA obligations
Chapter 4: Bitcoin as sound money — money vs currency distinction, 21M hard cap, gold comparison, FASB change
Chapter 5: Protocol businesses — Ethereum (UPI-like infrastructure), Solana (Indian co-founder), Polygon (Indian founders),
           Aave (automated lending), Uniswap (automated exchange) — each evaluated like a VC-backed company
Chapter 6: Real World Assets — BlackRock BUIDL ($2.5B), JPMorgan MONY ($100M), Franklin Templeton FOBXX ($700M+)

=== AUTHOR BIO ===
Mahaveer Soni
Marketing Manager, Grade Capital
mahaveer@grade.capital | https://grade.capital
"""

# ============================================================
# SEARCH QUERIES — rotated daily so targets stay fresh
# ============================================================
SEARCH_QUERIES = [
    "crypto blockchain finance magazine \"write for us\" OR \"submit article\" OR \"guest post\"",
    "financial technology editorial \"contribute\" OR \"submission guidelines\" cryptocurrency",
    "fintech blog \"write for us\" crypto investment blockchain 2024 2025",
    "investment newsletter \"guest contributor\" OR \"guest author\" blockchain digital assets",
    "cryptocurrency media site editorial submission contact",
    "blockchain technology publication \"contribute an article\" OR \"guest post\"",
    "financial literacy platform guest post crypto blockchain India",
    "DeFi Web3 publication \"write for us\" OR \"contribute\"",
    "alternative investment magazine editorial submission blockchain",
    "wealth management blog guest post cryptocurrency fintech",
    "personal finance editorial \"submit\" crypto investing article",
    "India fintech technology blog \"write for us\" blockchain",
    "digital assets institutional finance publication submission",
    "crypto investment research blog contributor guidelines",
    "financial advisory newsletter guest article blockchain",
    "entrepreneurship finance startup blog \"guest post\" crypto",
    "tax finance crypto India blog editorial contribution",
    "hedge fund alternative assets publication submission 2024",
    "ETF investment blog \"write for us\" cryptocurrency",
    "global finance magazine editorial crypto article submission",
]

# Domains to skip — not relevant for guest post outreach
SKIP_DOMAINS = [
    'reddit.com', 'youtube.com', 'twitter.com', 'x.com', 'facebook.com',
    'linkedin.com', 'wikipedia.org', 'amazon.com', 'google.com', 'instagram.com',
    'tiktok.com', 'quora.com', 'medium.com', 'substack.com', 'pinterest.com',
    'yelp.com', 'trustpilot.com', 'glassdoor.com', 'indeed.com',
]


# ============================================================
# FUNCTIONS
# ============================================================

def load_sent_log():
    """Return set of already-contacted URLs and emails."""
    sent = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('url'):
                    sent.add(row['url'].lower().strip())
                if row.get('email'):
                    sent.add(row['email'].lower().strip())
    return sent


def log_result(org_name, url, email, subject, status):
    """Append one row to the CSV log."""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'org_name', 'url', 'email', 'subject', 'status'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'date':     datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'org_name': org_name,
            'url':      url,
            'email':    email,
            'subject':  subject,
            'status':   status,
        })


def search_organizations(query, num=20):
    """Call Serper (Google Search API) and return organic results."""
    try:
        resp = requests.post(
            'https://google.serper.dev/search',
            headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
            json={'q': query, 'num': num, 'gl': 'us', 'hl': 'en'},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get('organic', [])
    except Exception as e:
        print(f"  [Search error] {e}")
        return []


def scrape_org(url):
    """Fetch the org homepage and extract useful signals."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Title + meta description
        title      = (soup.find('title') or soup.new_tag('x')).get_text(strip=True)
        meta       = soup.find('meta', {'name': 'description'}) or {}
        meta_desc  = meta.get('content', '') if isinstance(meta, dict) else meta.get('content', '')

        # Clean body text
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        body_text = ' '.join(soup.get_text(separator=' ', strip=True).split())[:3000]

        # Emails in page source
        raw_emails = re.findall(r'[\w.+\-]+@[\w\-]+\.[\w.]+', resp.text)
        filtered   = [
            e for e in raw_emails
            if not e.lower().endswith(('.png', '.jpg', '.gif', '.css', '.js'))
            and '.' in e.split('@')[-1]
        ]
        priority_emails = [
            e for e in filtered
            if any(w in e.lower() for w in ['edit', 'submit', 'contribut', 'write', 'contact', 'info', 'hello', 'guest'])
        ]

        # Links pointing to submission / contact pages
        sub_links = []
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True).lower()
            href = a['href']
            if any(w in text for w in ['write for us', 'submit', 'contribut', 'guest post', 'editorial', 'contact us']):
                sub_links.append(href)

        return {
            'title':         title,
            'description':   meta_desc,
            'body':          body_text,
            'emails':        priority_emails[:5] + [e for e in filtered if e not in priority_emails][:5],
            'sub_links':     sub_links[:5],
        }
    except Exception as e:
        print(f"  [Scrape error] {e}")
        return None


def find_contact_email(base_url, org_data):
    """Best-effort extraction of a valid contact/editorial email."""
    # 1. Already found high-priority emails
    if org_data.get('emails'):
        return org_data['emails'][0]

    origin = '/'.join(base_url.rstrip('/').split('/')[:3])
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 2. Follow submission links found on homepage
    for link in org_data.get('sub_links', []):
        try:
            full = link if link.startswith('http') else origin + '/' + link.lstrip('/')
            r    = requests.get(full, headers=headers, timeout=10)
            mails = re.findall(r'[\w.+\-]+@[\w\-]+\.[\w.]+', r.text)
            valid = [m for m in mails if '.' in m.split('@')[-1] and not m.endswith(('.png','.jpg','.gif'))]
            if valid:
                return valid[0]
        except Exception:
            continue

    # 3. Try common paths
    for path in ['/contact', '/write-for-us', '/submit', '/contribute', '/editorial', '/about']:
        try:
            r     = requests.get(origin + path, headers=headers, timeout=8)
            mails = re.findall(r'[\w.+\-]+@[\w\-]+\.[\w.]+', r.text)
            valid = [m for m in mails if '.' in m.split('@')[-1] and not m.endswith(('.png','.jpg','.gif'))]
            if valid:
                return valid[0]
        except Exception:
            continue

    return None


def generate_content(org_name, org_description, org_body, url):
    """Use Gemini to create a tailored article + pitch email."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are a senior financial writer and researcher working with Grade Capital.
Your task: produce (1) a tailored pitch email and (2) a full exclusive article for the publication below.

=== PUBLICATION DETAILS ===
Name        : {org_name}
Website     : {url}
Description : {org_description}
Content tone (inferred from their site): {org_body[:800]}

=== GRADE CAPITAL CONTEXT ===
{GRADE_CAPITAL_CONTEXT}

=== ARTICLE INSTRUCTIONS ===
- Length: 1,500–2,000 words
- Tailor topic, depth, and tone precisely to THIS publication's audience
  (e.g., if it's a CA/tax publication → focus on VDA taxation + derivatives tax advantage;
   if institutional finance → focus on Bitcoin ETF inflows + RWA tokenization;
   if startup/entrepreneur → focus on the founding story + India's crypto opportunity)
- Synthesise data points uniquely — the article must NOT read like anything already on Google
- Weave in real, verifiable statistics (BlackRock $115B ETF, Goldman 71% survey, JPMorgan Kinexys $1.5T, etc.)
- Do NOT make it a Grade Capital advertisement — make it a genuinely valuable, research-backed piece
- End with EXACTLY this author bio line:
  "Mahaveer Soni is Marketing Manager at Grade Capital (grade.capital), India's first regulated crypto derivatives fund."

=== PITCH EMAIL INSTRUCTIONS ===
- Max 180 words — professional, concise
- Mention this is an exclusive article not published anywhere else
- State clearly: we offer the article free of charge in exchange for a byline crediting
  Mahaveer Soni and a mention of Grade Capital with a link to grade.capital
- Match the publication's tone (formal vs conversational)
- Do NOT sound like a mass email — reference their publication specifically

=== OUTPUT FORMAT (use EXACTLY these markers, nothing before ===SUBJECT===) ===
===SUBJECT===
[one compelling subject line for the pitch email]
===PITCH===
[pitch email body, 180 words max]
===ARTICLE===
[full article, 1500-2000 words]
===END===
"""

    try:
        response = model.generate_content(prompt)
        text     = response.text

        subject = text.split('===SUBJECT===')[1].split('===PITCH===')[0].strip()
        pitch   = text.split('===PITCH===')[1].split('===ARTICLE===')[0].strip()
        article = text.split('===ARTICLE===')[1].split('===END===')[0].strip()
        return subject, pitch, article
    except Exception as e:
        print(f"  [Gemini error] {e}")
        return None, None, None


def send_email(to_email, subject, pitch, article, org_name):
    """Send pitch + article via Gmail SMTP."""
    msg              = MIMEMultipart('alternative')
    msg['Subject']   = subject
    msg['From']      = f"Mahaveer Soni <{SENDER_EMAIL}>"
    msg['To']        = to_email

    body = f"""{pitch}

{"=" * 60}
ARTICLE (ready to publish)
{"=" * 60}

{article}

{"=" * 60}
Mahaveer Soni
Marketing Manager, Grade Capital
mahaveer@grade.capital | https://grade.capital
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"  [SMTP error] {e}")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    today = datetime.date.today()
    print(f"\n{'='*60}")
    print(f"  Grade Capital Outreach — {today}")
    print(f"  Target: {ORGS_PER_DAY} organisations today")
    print(f"{'='*60}\n")

    sent_log      = load_sent_log()
    contacted     = 0

    # Rotate search query by day-of-year
    day_index = today.timetuple().tm_yday % len(SEARCH_QUERIES)
    query     = SEARCH_QUERIES[day_index]
    print(f"Search query: {query}\n")

    results = search_organizations(query, num=30)
    random.shuffle(results)  # randomise order each run

    for result in results:
        if contacted >= ORGS_PER_DAY:
            break

        url      = result.get('link', '').strip()
        org_name = result.get('title', url)
        snippet  = result.get('snippet', '')

        if not url:
            continue

        # Skip irrelevant domains
        if any(d in url.lower() for d in SKIP_DOMAINS):
            continue

        # Skip already contacted
        if url.lower() in sent_log:
            print(f"[skip] Already contacted: {org_name}")
            continue

        print(f"\n[{contacted+1}] {org_name}")
        print(f"    URL: {url}")

        # --- Scrape ---
        org_data = scrape_org(url)
        if not org_data:
            log_result(org_name, url, '', '', 'scrape_failed')
            continue

        # --- Find email ---
        email = find_contact_email(url, org_data)
        if not email:
            print(f"    No email found — skipping")
            log_result(org_name, url, '', '', 'no_email')
            continue

        if email.lower() in sent_log:
            print(f"    Email {email} already contacted — skipping")
            continue

        print(f"    Email: {email}")

        # --- Generate content ---
        description = org_data.get('description') or snippet
        subject, pitch, article = generate_content(
            org_name, description, org_data.get('body', ''), url
        )
        if not subject:
            log_result(org_name, url, email, '', 'generation_failed')
            continue

        print(f"    Subject: {subject}")

        # --- Send ---
        success = send_email(email, subject, pitch, article, org_name)
        status  = 'sent' if success else 'email_failed'
        log_result(org_name, url, email, subject, status)

        if success:
            print(f"    ✅ Sent!")
            sent_log.add(url.lower())
            sent_log.add(email.lower())
            contacted += 1
        else:
            print(f"    ❌ Email failed")

        # Polite rate-limiting between orgs
        time.sleep(random.uniform(4, 8))

    print(f"\n{'='*60}")
    print(f"  Done. Contacted {contacted} organisations today.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
