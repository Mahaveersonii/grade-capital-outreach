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
import imaplib
import email as email_lib
import datetime
import re
import json
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from bs4 import BeautifulSoup
import anthropic
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ============================================================
# CONFIGURATION (all values from GitHub Secrets)
# ============================================================
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
SERPER_API_KEY   = os.environ.get('SERPER_API_KEY', '')
SENDER_EMAIL     = os.environ.get('SENDER_EMAIL', 'mahaveer@grade.capital')
EMAIL_PASSWORD   = os.environ.get('EMAIL_PASSWORD', '')
SMTP_HOST        = 'smtp.gmail.com'
SMTP_PORT        = 587
ORGS_PER_DAY     = random.randint(10, 15)
LOG_FILE         = 'sent_log.csv'

# ============================================================
# GRADE CAPITAL MASTER CONTEXT — FULL 6-CHAPTER CONTENT
# (used to brief Claude for every article it writes)
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

=== CHAPTER 1: WHY THIS CONVERSATION IS HAPPENING NOW ===
Clients are already in crypto — they brought this conversation to their CAs, not the other way around.
India has 100M+ crypto users. Clients ask about Bitcoin gains declaration, stablecoin yields (8%), token ESOPs from startups.

THREE SIMULTANEOUS SHIFTS:
1. Global institutional adoption — BlackRock, Goldman Sachs, pension funds entering crypto
2. Indian regulatory formalization — VDA tax framework, PMLA notification, CARF by 2027
3. Mass retail client exposure — clients already hold crypto, often non-compliant

INDIA REGULATORY TIMELINE EVERY PROFESSIONAL MUST KNOW:
- 2018: RBI circular banned banks from dealing with crypto → exchanges went P2P
- 2020: Supreme Court struck down RBI circular (IMAI v. RBI) → banking restored, market exploded
- 2022: Union Budget introduced Section 115BBH (30% flat tax) and Section 194S (1% TDS)
- 2023 March: PMLA notification — crypto service providers under same umbrella as banks/NBFCs
- 2026: CARF (Crypto Asset Reporting Framework) arrives — automatic cross-border data exchange

"LEGAL BUT NOT LEGAL TENDER": Crypto is taxable property. Holding/trading is legal. Cannot be used as payment.

REGULATORY ARCHITECTURE:
- SEBI: Securities angle
- RBI: Payment systems
- MCA: Corporate disclosures (companies must disclose crypto holdings)
- PMLA/FIU-IND: AML/KYC enforcement

THE CA OPPORTUNITY — 3 TYPES OF PROFESSIONALS:
1. Those who avoid crypto entirely (send clients to unqualified sources)
2. Those who dabble without framework (give inconsistent advice)
3. Those who build genuine expertise (the opportunity — time-limited before CARF closes the window)

FOUR THINGS TO ACCEPT:
1. Clients are already in crypto — deflecting sends them to unqualified advisors
2. India has a tax law — ignoring it creates client AND professional liability
3. CARF window is closing — voluntary disclosure opportunity exists NOW, not in 3 years
4. Professional evaluation requires a framework, not an opinion

=== CHAPTER 2: HOW BLOCKCHAIN ACTUALLY WORKS ===
THE PROBLEM BLOCKCHAIN SOLVES:
Traditional finance needs trusted intermediaries (banks, clearinghouses) to prevent double-spending.
Blockchain replaces the trusted third party with a distributed, cryptographically secured ledger.

KEY CONCEPTS:
LEDGER: A shared record of all transactions — like a publicly auditable trial balance that no single party controls.

NODES: Bitcoin has 50,000+ active nodes across every continent. Each independently validates every transaction.
No single node is the authority. If an entire country's nodes go offline, the network continues without interruption.
No central server, no headquarters, no single point of failure.

CONSENSUS MECHANISMS:
- Proof of Work (Bitcoin): Miners compete with computing power to add blocks. Energy-intensive but extremely secure.
  An attacker would need to out-compute 51% of the entire global network simultaneously — practically impossible.
- Proof of Stake (Ethereum): Validators lock up collateral (stake) to earn validation rights. Energy-efficient.
  Ethereum uses 99.95% less energy than Proof of Work after its 2022 "Merge."

CRYPTOGRAPHIC KEYS:
- Private key = signing authority (like a wet signature but mathematically unforgeable)
- Public key = address (like a bank account number you can share freely)
- Losing your private key = permanent loss of access. No bank to call. No password reset.

IMMUTABILITY: Once recorded, transactions cannot be altered without rewriting every subsequent block
across 50,000+ nodes simultaneously. Each block contains the cryptographic hash of the previous block.
Change one block → every subsequent block becomes invalid → network rejects it instantly.

TYPES OF BLOCKCHAINS:
- Public/permissionless: Bitcoin, Ethereum — open to all, fully transparent, censorship-resistant
- Private/permissioned: Used by banks (JPMorgan Kinexys) — controlled access, known participants
- Layer 2s: Built on top of base chains for speed/cost (Polygon on Ethereum)

SMART CONTRACTS: Self-executing code on blockchain. When conditions are met, execution is automatic.
No intermediary needed. Used for DeFi lending, exchanges, RWA tokenization, compliance automation.

=== CHAPTER 3: INDIA'S CRYPTO TAX FRAMEWORK ===
VDA DEFINITION (Section 2(47A) Income Tax Act):
Covers: All crypto assets, NFTs, tokens. Excludes: Foreign currency, traditional securities, gift cards, loyalty points, CBDCs.

SECTION 115BBH — SPOT CRYPTO (THE PUNITIVE REGIME):
- Flat 30% tax on ALL VDA transfers — no slab benefit, no exemptions
- Only deduction: Cost of acquisition (nothing else)
- NO loss set-off against ANY income (not even other crypto gains)
- NO loss carry-forward to future years
- 1% TDS on every transfer above ₹10,000 (₹50,000 for non-specified persons)
- Same rate whether held 1 day or 10 years — no long-term benefit
- ITR-2 filing required (Capital Gains schedule)

AIRDROPS, MINING, STAKING: Taxed as income at fair market value on date of receipt.
Subsequently taxed again at 30% when sold — effectively double taxation.

SECTION 43(5) — CRYPTO DERIVATIVES (THE BETTER REGIME):
Crypto derivatives (futures, options, perpetuals where settlement is based on crypto price but no actual delivery)
are NOT VDAs under Section 115BBH. They are speculative transactions under Section 43(5).

COMPARISON TABLE:
Feature | Spot Crypto (115BBH) | Derivatives (43(5) & 73)
Tax rate | Flat 30% | Slab rate (5/20/30%)
Deductions | Cost of acquisition only | All business expenses
Loss set-off | Not allowed | Against speculative income
Loss carry-forward | Not allowed | 4 years
TDS | 1% on transfers >₹10,000 | Standard provisions
ITR form | ITR-2 | ITR-3

REAL MONEY DIFFERENCE:
₹10 lakh profit: Spot = ₹3L tax | Derivatives (20% bracket) = ₹2L tax → ₹1L saved
₹1 crore profit: Spot = ₹30L tax | Derivatives (20% bracket) = ₹20L tax → ₹10L saved per year

SECTION 194S — TDS OBLIGATIONS:
- Exchange handles TDS for on-platform trades
- For P2P/OTC: BUYER is responsible for deducting and depositing TDS
- CA must advise clients BEFORE transactions — post-transaction compliance gap already exists

CA PROFESSIONAL OBLIGATIONS:
- MUST file Schedule VDA when client has crypto income — omitting = professional misconduct
- MUST advise TDS compliance before P2P/OTC transactions
- MUST NOT advise non-disclosure (ICAI Code of Ethics, Chapter VI violation)
- MUST flag CARF implications for offshore holders — voluntary disclosure window is open NOW
- CARF arrives 2027: Automatic exchange of crypto data between 50+ countries

=== CHAPTER 4: BITCOIN AS SOUND MONEY ===
MONEY vs CURRENCY — THE CRITICAL DISTINCTION:
Currency: Medium of exchange (used for transactions). Can be printed infinitely.
Money: Store of value across time. Must hold purchasing power across generations.
The rupee is currency — you transact with it. But India's inflation (5-7%) erodes its value every year.
Every fiat currency in history has lost purchasing power. The US Dollar has lost 97% of its value since 1913.

WHY GOLD HAS BEEN MONEY FOR 5,000 YEARS:
Properties: Scarce, durable, divisible, portable, fungible, recognizable.
Gold's limitation: Can't be sent digitally. Can be confiscated. Hard to verify purity. Storage costs.

BITCOIN'S DESIGN — DIGITAL SOUND MONEY:
Created by Satoshi Nakamoto in 2008 during the global financial crisis. Question: "Can we create digital scarcity?"
- Hard cap: Exactly 21,000,000 Bitcoin. Ever. This CANNOT be changed.
- Why can't it be changed: No CEO. No headquarters. 50,000+ nodes all enforce the same rules.
  A majority of nodes would have to agree to change — and they have no incentive to dilute their own holdings.
- Supply schedule: New Bitcoin issued on a fixed, predictable schedule that halves every 4 years.
- Current supply: ~19.8M mined. ~1.2M left to mine over the next ~120 years.

BITCOIN vs GOLD vs FIAT:
Property | Bitcoin | Gold | Fiat
Scarcity | Hard cap 21M — absolute | Limited but uncertain | Unlimited — printed at will
Verification | Instant, cryptographic | Requires testing | Requires trust in institution
Portability | Send anywhere in minutes | Physically heavy | Digital but controlled
Confiscation resistance | High (self-custody) | Low | Very low
Divisibility | To 8 decimal places | Limited | Limited

WHY DOES BITCOIN HAVE VALUE? Same logic as gold:
- Scarce (can't be inflated away)
- Accepted by growing global network
- Credibly neutral (no government controls it)
- Now: 1,800+ institutional custody clients, $115B+ ETF AUM, corporate treasuries

INSTITUTIONAL ADOPTION (MID-2026):
- BlackRock Bitcoin ETF: $115B+ AUM — fastest-growing ETF in financial history
- MicroStrategy: 528,000+ BTC on balance sheet (~$45B)
- Goldman Sachs survey: 71% of institutional managers plan to increase crypto exposure
- Rockefeller Capital: Increased Bitcoin position 146%
- South Korea NPS (world's 3rd largest pension): $83.2M Bitcoin position
- US Spot Bitcoin ETFs approved January 2024 by SEC

FASB ACCOUNTING CHANGE (December 2024):
Previous: Bitcoin on corporate balance sheet written DOWN to cost — gains not recognized until sale.
New (FASB ASC 350-60): Mark-to-market — Bitcoin carried at fair value. Gains AND losses flow through P&L.
Implication: Major barrier to corporate treasury adoption removed. More companies will now hold Bitcoin.

BITCOIN DURING IRAN WAR CRISIS (Feb-Mar 2026):
Bitcoin: +17% | Nifty 50: Down | S&P 500: Down | Gold: Fell from ATH of $5,595
Bitcoin rising while stocks AND gold fell = non-correlation thesis proven in real time.

CA EVALUATION FRAMEWORK FOR BITCOIN:
Question: "Is this a credible store of value?"
Evaluate: Scarcity mechanism (21M cap) | Decentralization (50,000 nodes) | Institutional adoption
Track record: 15+ years of operation, survived multiple 70%+ crashes, always reached new highs.

=== CHAPTER 5: PROTOCOL BUSINESSES (ETHEREUM, SOLANA, POLYGON, AAVE, UNISWAP) ===
KEY INSIGHT: These are NOT like Bitcoin. Bitcoin = evaluate as sound money. Protocols = evaluate as businesses.
They have founders, employees, revenue, VC funding, and can be evaluated using standard business frameworks.

ETHEREUM — THE INFRASTRUCTURE LAYER:
Indian parallel: UPI — infrastructure that enables multiple applications to work on top of it.
- Ethereum Foundation: Switzerland-registered non-profit
- Treasury: $650M+ (Oct 2024 annual report — publicly available at ethereum.org)
- Governance: Annual financial reports, open-source codebase, transparent treasury
- Proof of Stake since Sept 2022: 99.95% energy reduction
- BlackRock BUIDL fund built ON Ethereum: $2.5B AUM, BNY Mellon custodian
- Robert Mitchnick (BlackRock Head of Digital Assets): "This is the latest progression of our digital assets strategy"
- If BlackRock's legal, compliance and risk teams approved building on Ethereum — what did their due diligence conclude?

SOLANA — HIGH-SPEED INFRASTRUCTURE:
Indian parallel: Flipkart/Freshworks — VC-backed, rapidly scaling, competing on speed.
- Co-founder: Raj Gokal (Indian-origin, Wharton graduate, began career at Finaco India)
- Funding: $314M from a16z, Multicoin Capital, Alameda (pre-FTX), others
- Financial performance: $461M annualized revenue (Q4 2024), $1B+ cumulative fees
- Institutional ETF products approved (Bloomberg, Reuters Oct-Nov 2025)
- Speed: 65,000 transactions per second vs Ethereum's ~15 TPS

POLYGON — INDIA'S GLOBAL BLOCKCHAIN SUCCESS:
Indian parallel: Infosys/TCS — built in India, serving the world.
- Founders: Jaynti Kanani (ex-Housing.com data scientist), Sandeep Nailwal (ex-Deloitte), Anurag Arjun (ex-Deloitte)
- Funding: $450M from Sequoia Capital India, Tiger Global, SoftBank (Feb 2022)
- India adoption: IRCTC using Polygon blockchain for loyalty program
- Jio Partnership (Jan 2025): Polygon CEO Marc Boiron + Kiran Thomas (Jio Platforms CEO) announced integration
- Global: Meta, Starbucks, Adobe, Disney used Polygon for NFT/loyalty programs
- "First Indian crypto billionaires" — Business Insider India, May 2021

AAVE — AUTOMATED LENDING PROTOCOL:
Indian parallel: HDFC Bank's lending operation — but fully automated, every loan visible on public ledger.
- Founder: Stani Kulechov (Finland). Entity: Aave Companies (UK-registered)
- Funding: $25M from Framework Ventures, Three Arrows Capital, others
- Revenue: $115M annualized (stated by founder publicly, CryptoSlate June 2024)
- Business model: Borrowers pay interest → protocol takes spread → distributed to token holders
- Transparency advantage: Every loan, every interest rate, every liquidation visible on-chain in real time

UNISWAP — AUTOMATED EXCHANGE:
Indian parallel: NSE/BSE — but 24/7/365, globally accessible, every trade on public ledger.
- Funding: $11M (Series A, a16z) + $165M (Series B, Polychain, a16z, others)
- Volume: $2.5T+ cumulative trading volume
- The Block (Nov 2025): Reported multi-billion dollar monthly volumes
- No central counterparty. No KYC at protocol level. Smart contracts execute trades automatically.

INSTITUTIONAL VALIDATION:
SWIFT (Nov 5, 2024): Partnership with Chainlink — enabling 11,500+ banks across 200+ countries to settle tokenized assets.
Participating: UBS, JPMorgan, Euroclear, DTCC, Citi, BNY Mellon, BNP Paribas.
SWIFT official: "Enable digital asset transactions to settle with fiat payment systems."

Wall Street Stablecoin (Oct 2025): Goldman Sachs, JPMorgan, others launching joint stablecoin.
Source: Bloomberg, Yahoo Finance (Oct 10, 2025)

ADDRESSING SKEPTIC DOUBTS:
Doubt 1 — "No regulation": Reality: US (SEC/CFTC framework), EU (MiCA), India (PMLA, VDA tax). Regulation EXISTS.
Doubt 2 — "No real use": Reality: JPMorgan Kinexys $1.5T processed; SWIFT integrating 11,500 banks; India banks using blockchain.
Doubt 3 — "No revenue": Reality: Aave $115M annualized; Uniswap billions in volume fees; Solana $461M annualized.
Doubt 4 — "Scams and collapses": Reality: ALL major collapses (FTX, Celsius, Luna) were CENTRALIZED entities with opaque operations.
The decentralized protocols (Ethereum, Solana, Polygon, Aave, Uniswap) continued operating throughout every crash.

=== CHAPTER 6: REAL WORLD ASSETS (RWAs) ===
SIMPLE DEFINITION: An RWA token is a digital representation of something that already exists in the real world.
Government bonds. Real estate. Money market funds. Gold. Bank deposits.
The blockchain doesn't CREATE the asset. The blockchain RECORDS who owns it.

ANALOGY: When you buy a mutual fund, you don't physically hold Infosys shares — a registrar records your units.
RWA tokenization does the same — but the ledger is a blockchain instead of a centralized database.

WHAT CHANGES: How ownership is recorded, transferred, and settled.
Traditional: Multiple intermediaries, different ledgers, T+2 settlement, limited operating hours.
Tokenized: Single shared ledger, near-instant settlement, 24/7 operation, programmable compliance.

REAL EXAMPLES — INSTITUTIONS YOU ALREADY KNOW:

BlackRock BUIDL (March 2024):
- Full name: USD Institutional Digital Liquidity Fund
- Holds: US Treasury bills, cash, repurchase agreements — same as traditional money market fund
- Custodian: Bank of New York Mellon (world's largest custodian bank)
- Tokenized by: Securitize (SEC-registered broker-dealer and transfer agent)
- AUM: $2.5B by December 2025 | Dividends paid: $100M+
- Robert Mitchnick (BlackRock): "This is the latest progression of our digital assets strategy"

JPMorgan MONY (December 15, 2025):
- Full name: My OnChain Net Yield Fund
- Built on: Public Ethereum blockchain
- JPMorgan official: "J.P. Morgan is the largest GSIB on a public blockchain"
- Size: $100M initial | Platform: Morgan Money (institutional liquidity platform)

Franklin Templeton FOBXX (2021):
- One of the first tokenized government money market funds
- Invests in: US government securities
- AUM: $700M+ | Uses blockchain to record share ownership and transactions

JPMorgan Kinexys (formerly Onyx/JPM Coin):
- Processes: $1.5T+ in total transactions since inception
- Live with Indian banks: HDFC, ICICI, Axis, Yes Bank, IndusInd Bank in GIFT City
- Solves: Indian banks can now settle dollar transactions 24/7 — not just US banking hours
- Nov 2024: Added on-chain FX conversions starting with USD/EUR

SWIFT Integration (Nov 5, 2024):
- Partnership with Chainlink
- Enables 11,500+ banks across 200+ countries to connect to tokenized asset networks
- Participants: UBS, JPMorgan, Euroclear, DTCC, Citi, BNY Mellon, BNP Paribas

BENEFITS OF RWA TOKENIZATION:
1. 24/7 Settlement: No waiting for US banking hours or weekends
2. Reduced Settlement Time: T+2 → near-instant (IFSCA paper: "propel estimated time savings of 30-40%")
3. Fractional Ownership: ₹400cr GIFT City building → accessible to smaller investors via Terazo (min ₹10L)
4. Programmable Compliance: KYC/AML built into the token itself (ERC3643 standard)
5. Improved Liquidity: BUIDL tokens exchangeable for USDC through automated pools
6. Collateral Efficiency: BUIDL accepted as collateral by Binance, Crypto.com, Deribit

MARKET SIZE PROJECTIONS:
- BCG (2022): $16T by 2030 = 10% of global GDP
- BCG + Ripple (2025 update): $9.4T by 2030, $19T by 2033
- McKinsey (2024): $2-4T by 2030
- Standard Chartered: $30.1T by 2034
- Citi: $5T by 2030
Current (late 2025): Tokenized US Treasuries alone = $8.6-8.7B; Tokenized MMFs = $4B+

INDIA-SPECIFIC RWA INITIATIVES:
IFSCA (GIFT City regulator): Published 55-page consultation paper "Regulatory Approach Towards Tokenization of Real-World Assets" (Feb 26, 2025)
- Expert Committee on Asset Tokenization constituted September 2023
- IFSCA explicitly separates RWA tokenization FROM cryptocurrency
- Asset classes: Financial securities (funds, bonds, stocks), payments, deposits, real estate, commodities

JPMorgan in GIFT City (since June 2023): Operating Kinexys for interbank dollar transactions.
Participating banks: HDFC, ICICI, Axis, Yes Bank, IndusInd Bank.

Terazo (India's first regulated tokenized real estate):
- Project Oryx: 968,500 sq ft Grade-A commercial building in GIFT City SEZ (developed by Savvy Group)
- Fund: $7M, under IFSCA regulatory sandbox
- Technology: Polygon blockchain, ERC3643 standard, Tokeny platform
- Primary investors: Min $100,000 | Secondary: Min ₹10L

Telangana (December 2023): India's first state Technical Guidance Note on Asset Tokenization
- Published in partnership with IIIT-Hyderabad, CDAC, Tech Mahindra
- Blockchain District: Physical hub in Hyderabad
- T-Block Accelerator: 4-month program for blockchain startups

CA EVALUATION FRAMEWORK FOR RWAs (same questions as any asset-backed product):
1. What is the underlying asset? (T-bills vs real estate vs private credit)
2. Who is the issuer/manager? (BlackRock $11.5T AUM vs unknown entity)
3. Who is the custodian? (BNY Mellon vs self-custody)
4. Who is the auditor? (Independent verification frequency)
5. Can you redeem it? (Redemption terms, liquidity conditions)
6. What is the regulatory status? (SEC-registered? IFSCA sandbox? Unregulated?)

Where to verify: ifsca.gov.in | rwa.xyz | NY Federal Reserve Liberty Street Economics | BCG/McKinsey reports

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
    # === INDIA-FOCUSED BLOGS & PUBLICATIONS (PRIMARY — ~60%) ===
    "India \"write for us\" fintech startup crypto blockchain technology blog",
    "India crypto blockchain blog \"write for us\" OR \"guest post\" -site:reddit.com -site:quora.com",
    "\"contribute to our blog\" cryptocurrency fintech investment India",
    "Indian fintech blog \"guest post\" OR \"write for us\" blockchain crypto",
    "India finance blog \"submit article\" OR \"guest contributor\" crypto blockchain",
    "startup entrepreneur blog India \"guest post\" crypto blockchain fintech",
    "Indian cryptocurrency blog \"write for us\" OR \"contribute\" 2025 2026",
    "India blockchain technology blog \"submit\" OR \"guest author\"",
    "\"write for us\" Indian finance investment crypto tax blockchain",
    "India web3 DeFi blog \"write for us\" OR \"guest post\" editorial",

    # === INDIA MAGAZINES & BUSINESS MEDIA ===
    "India finance business magazine \"submit article\" OR \"contributor guidelines\"",
    "technology magazine India \"write for us\" blockchain crypto fintech 2025",
    "\"business magazine\" India \"submit\" OR \"contribute\" OR \"editorial\" crypto blockchain",
    "Indian business magazine \"guest article\" OR \"contribute\" fintech crypto",
    "India digital magazine fintech crypto blockchain \"submit\" OR \"write for us\"",
    "Indian startup magazine \"write for us\" OR \"guest post\" fintech blockchain",

    # === INDIA PROFESSIONAL BODIES & ASSOCIATIONS ===
    "CA ICAI chartered accountant association newsletter \"guest article\" crypto tax blockchain",
    "fintech association India \"submit article\" OR \"guest contributor\" 2025",
    "India NASSCOM fintech blockchain \"contribute\" OR \"guest post\"",
    "Indian professional body finance crypto blockchain editorial contribute",
    "ICAI journal \"submit\" OR \"contribute\" cryptocurrency taxation India",
    "India CFA institute \"guest article\" OR \"contribute\" crypto investment",

    # === INDIA RESEARCH & THINK TANKS ===
    "fintech research institute India \"contribute\" OR \"guest author\" OR \"submit article\"",
    "India financial research \"contribute\" crypto blockchain technology policy",
    "Indian think tank blockchain crypto fintech \"submit\" OR \"call for papers\"",
    "IFSCA GIFT City research \"contribute\" OR \"submit\" blockchain tokenization",
    "India digital finance research \"call for papers\" OR \"submit\" blockchain 2025",

    # === INDIA NEWSLETTERS & NEWS PLATFORMS ===
    "fintech finance newsletter India \"contribute\" OR \"submit\" article",
    "India startup finance news \"contributor\" OR \"write for us\" crypto blockchain",
    "Indian crypto news \"guest columnist\" OR \"write for us\" OR \"contribute\"",
    "\"op-ed\" OR \"opinion piece\" blockchain cryptocurrency finance India media",
    "Indian fintech news \"contributed content\" OR \"guest contributor\" crypto",

    # === GLOBAL WITH INDIA RELEVANCE (SECONDARY — ~25%) ===
    "crypto blockchain \"write for us\" \"guest post\" India emerging markets -site:reddit.com -site:quora.com",
    "\"submit a guest post\" OR \"contribute an article\" crypto blockchain India investment",
    "fintech finance blog \"write for us\" cryptocurrency blockchain India regulation",
    "\"accepting guest posts\" crypto blockchain investment finance India 2025",
    "web3 DeFi blog \"write for us\" OR \"guest post\" India regulation editorial",

    # === GLOBAL (MINIMAL — ~15%) ===
    "crypto blockchain \"write for us\" \"guest post\" -site:reddit.com -site:quora.com",
    "cryptocurrency blockchain magazine \"contribute\" OR \"submit article\" OR \"editorial submissions\"",
    "blockchain research organization \"call for papers\" OR \"submit research\" OR \"guest post\"",
    "\"open access journal\" blockchain cryptocurrency finance \"submit article\"",
    "\"call for papers\" blockchain cryptocurrency finance journal 2025",
]

# Domains to skip — social media, paywalled, or irrelevant
SKIP_DOMAINS = [
    # Social / aggregator
    'reddit.com', 'youtube.com', 'twitter.com', 'x.com', 'facebook.com',
    'linkedin.com', 'wikipedia.org', 'amazon.com', 'google.com', 'instagram.com',
    'tiktok.com', 'quora.com', 'medium.com', 'substack.com', 'pinterest.com',
    'yelp.com', 'trustpilot.com', 'glassdoor.com', 'indeed.com',
    # Big paywalled / institutional (don't accept guest posts)
    'wealthmanagement.com', 'rothschildandco.com', 'advisorperspectives.com',
    'wsj.com', 'ft.com', 'bloomberg.com', 'reuters.com', 'economist.com',
    'forbes.com', 'businessinsider.com', 'techcrunch.com', 'cnbc.com',
    'investopedia.com', 'morningstar.com', 'seekingalpha.com',
    'coindesk.com', 'cointelegraph.com', 'theblock.co', 'decrypt.co',
    'bitgo.com', 'pwmnet.com', 'tciwealth.com', 'avaloq.com',
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
                # Only skip orgs where email was actually SENT successfully
                # Failed attempts (no_email, scrape_failed, generation_failed) get retried
                if row.get('status') == 'sent':
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


def load_followup_targets():
    """
    Return a list of dicts for orgs that:
      - Had status='sent' exactly 2 days ago (by date field)
      - Have NOT already received a follow-up (no row with status='followup_sent' for that email)
    Each dict: {org_name, url, email, subject}
    """
    if not os.path.exists(LOG_FILE):
        return []

    cutoff_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

    sent_rows   = []   # rows where status=sent on cutoff_date
    followed_up = set()  # emails already followed-up

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email  = (row.get('email') or '').strip().lower()
            status = (row.get('status') or '').strip()
            date   = (row.get('date') or '')[:10]  # YYYY-MM-DD portion only

            if status == 'followup_sent' and email:
                followed_up.add(email)

            if status == 'sent' and date == cutoff_date and email:
                sent_rows.append({
                    'org_name': row.get('org_name', ''),
                    'url':      row.get('url', ''),
                    'email':    email,
                    'subject':  row.get('subject', ''),
                })

    # Return only those not yet followed up
    return [r for r in sent_rows if r['email'] not in followed_up]


def has_replied(sender_email):
    """
    Check our inbox via IMAP for any email FROM sender_email.
    Returns True if a reply exists (meaning they already responded).
    """
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(SENDER_EMAIL, EMAIL_PASSWORD)
        mail.select('INBOX')

        # Search for any email from this sender address
        status, data = mail.search(None, f'(FROM "{sender_email}")')
        mail.logout()

        if status == 'OK' and data[0]:
            # data[0] is a space-separated list of message IDs; non-empty = reply exists
            return True
        return False

    except Exception as exc:
        print(f"    ⚠ IMAP check failed for {sender_email}: {exc}")
        # If IMAP check fails, skip the follow-up to be safe (don't annoy someone who replied)
        return True


def send_followup_email(to_email, org_name, original_subject):
    """Send a short, polite follow-up nudge referencing the original pitch."""
    try:
        msg             = MIMEMultipart('alternative')
        msg['Subject']  = f"Re: {original_subject}"
        msg['From']     = f"Mahaveer Soni <{SENDER_EMAIL}>"
        msg['To']       = to_email

        body = (
            f"Hi,\n\n"
            f"I hope this message finds you well. I'm following up on the guest article "
            f"proposal I sent to {org_name} two days ago regarding the above subject.\n\n"
            f"We believe the article offers genuine value for your audience and aligns well "
            f"with the topics your platform covers. I'd love to hear your thoughts and am "
            f"happy to make any adjustments you may require.\n\n"
            f"Looking forward to your prompt response.\n\n"
            f"Warm regards,\n"
            f"Mahaveer Soni\n"
            f"Marketing Manager, Grade Capital\n"
            f"mahaveer@grade.capital  |  https://grade.capital"
        )

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        return True

    except Exception as exc:
        print(f"    ❌ Follow-up email error: {exc}")
        return False


def run_followups():
    """Check for orgs due a 2-day follow-up and send nudge emails."""
    targets = load_followup_targets()

    if not targets:
        print("[follow-up] No organisations due a follow-up today.\n")
        return

    print(f"[follow-up] {len(targets)} organisation(s) due a follow-up today.")

    for t in targets:
        print(f"  → Checking: {t['org_name']} <{t['email']}>")

        # Skip if they already replied to our original email
        if has_replied(t['email']):
            print(f"    ↩ Already replied — skipping follow-up")
            log_result(t['org_name'], t['url'], t['email'], t['subject'], 'replied_skip')
            continue

        print(f"    No reply found — sending follow-up")
        success = send_followup_email(t['email'], t['org_name'], t['subject'])
        status  = 'followup_sent' if success else 'followup_failed'
        log_result(t['org_name'], t['url'], t['email'], t['subject'], status)

        if success:
            print(f"    ✅ Follow-up sent!")
        time.sleep(random.uniform(3, 6))

    print()


def search_organizations(query, num=20):
    """Call Serper (Google Search API) and return organic results."""
    try:
        resp = requests.post(
            'https://google.serper.dev/search',
            headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
            json={'q': query, 'num': num, 'gl': 'in', 'hl': 'en'},
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

        # Emails in page source — strict validation
        raw_emails = re.findall(r'[\w.+\-]+@[\w\-]+\.[\w.]+', resp.text)
        VALID_TLDS = {
            'com','org','net','io','co','in','uk','au','ca','de','fr','sg',
            'info','biz','edu','gov','media','finance','tech','digital','blog',
        }
        # Infrastructure/error-tracking domains — never editorial contacts
        BLOCKED_DOMAINS = {
            'sentry.io', 'ingest.sentry.io', 'example.com', 'test.com',
            'noreply.com', 'no-reply.com', 'mailer.com', 'bounce.com',
            'googleusercontent.com', 'amazonaws.com', 'cloudfront.net',
        }
        # Generic public email providers — not real org contacts
        PUBLIC_EMAIL_DOMAINS = {
            'gmail.com', 'yahoo.com', 'yahoo.in', 'yahoo.co.in',
            'hotmail.com', 'outlook.com', 'live.com', 'icloud.com',
            'protonmail.com', 'rediffmail.com', 'ymail.com',
        }
        filtered = []
        for e in raw_emails:
            e = re.sub(r'^[^a-zA-Z0-9]+', '', e)   # strip non-alphanum prefix
            e = re.sub(r'^u[0-9a-f]{4}', '', e)    # strip HTML unicode escapes e.g. u003e
            e = re.sub(r'^(amp|gt|lt|quot);', '', e, flags=re.IGNORECASE)  # strip &amp; etc
            parts = e.split('@')
            if len(parts) != 2: continue
            local, domain = parts[0], parts[1].lower()
            tld = domain.split('.')[-1]
            if tld not in VALID_TLDS: continue                      # skip bootstrap@5.3.3
            if not tld.isalpha(): continue                          # skip numeric TLDs like swiper@12.1.2
            if len(domain) < 4 or len(e) > 70: continue            # skip junk lengths
            if not re.match(r'^[\w.+\-]+$', local): continue       # skip malformed local
            if e.lower().endswith(('.png','.jpg','.gif','.css','.js')): continue
            if re.match(r'^[0-9a-f]{16,}$', local, re.IGNORECASE): continue  # skip MD5/hash locals like sentry IDs
            if any(domain == bd or domain.endswith('.' + bd) for bd in BLOCKED_DOMAINS): continue
            if domain in PUBLIC_EMAIL_DOMAINS: continue                # skip gmail/yahoo — not real org emails
            filtered.append(e)
        # De-duplicate
        filtered = list(dict.fromkeys(filtered))
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


RESEARCH_QUERIES = [
    # India-focused research (primary)
    "India crypto regulation VDA tax blockchain policy research 2024 2025",
    "India cryptocurrency taxation Section 115BBH research paper",
    "IFSCA GIFT City blockchain tokenization India research 2025",
    "India fintech blockchain adoption research paper 2024 2025",
    "blockchain financial inclusion emerging markets India research",
    "India digital rupee CBDC RBI stablecoin research paper 2024 2025",
    "India crypto derivatives regulation IFSCA research",
    "Indian cryptocurrency market institutional adoption research 2025",
    "Polygon Solana Indian blockchain ecosystem research paper",
    # Global with India relevance
    "cryptocurrency blockchain investment institutional adoption research paper 2024 2025",
    "Bitcoin store of value digital gold academic research 2024",
    "real world asset tokenization institutional blockchain research 2024 2025",
    "crypto derivatives risk management hedge fund research paper",
    "crypto asset portfolio diversification non-correlation research 2024",
]

RESEARCH_SOURCES = [
    # India-specific sources (prioritized)
    "site:rbi.org.in",        # RBI working papers
    "site:ifsca.gov.in",      # IFSCA publications
    "site:sebi.gov.in",       # SEBI research
    "site:nipfp.org.in",      # National Institute of Public Finance & Policy
    "site:icai.org",          # ICAI — Institute of Chartered Accountants of India
    # Global academic/research
    "site:ssrn.com",
    "site:papers.ssrn.com",
    "site:scholar.google.com",
    "site:bis.org",           # Bank for International Settlements
    "site:imf.org",           # IMF working papers
    "site:nber.org",          # NBER papers
    "site:brookings.edu",     # Brookings Institution
    "site:cfa.institute",     # CFA Institute research
]


def fetch_research_papers(topic_hint):
    """Search for and extract key findings from research papers relevant to the article topic."""
    research_findings = []

    # Pick 2 random research sources and 1 query to keep it fast
    sources   = random.sample(RESEARCH_SOURCES, 2)
    base_query = random.choice(RESEARCH_QUERIES)

    # Bias query toward topic if we can detect it
    topic_lower = topic_hint.lower()
    if any(w in topic_lower for w in ['tax', 'ca', 'chartered', 'compliance', 'audit']):
        base_query = "India crypto VDA tax compliance research paper 2024 2025"
    elif any(w in topic_lower for w in ['rwa', 'real world', 'tokeniz', 'asset']):
        base_query = "real world asset tokenization institutional blockchain research 2024 2025"
    elif any(w in topic_lower for w in ['bitcoin', 'btc', 'store of value', 'gold']):
        base_query = "Bitcoin store of value digital gold institutional research 2024 2025"
    elif any(w in topic_lower for w in ['defi', 'protocol', 'ethereum', 'solana']):
        base_query = "DeFi protocol revenue institutional adoption research 2024 2025"
    elif any(w in topic_lower for w in ['india', 'indian', 'gift city', 'sebi', 'rbi']):
        base_query = "India blockchain crypto regulation financial inclusion research 2025"

    for source in sources:
        query = f"{base_query} {source}"
        try:
            resp = requests.post(
                'https://google.serper.dev/search',
                headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
                json={'q': query, 'num': 5},
                timeout=10,
            )
            results = resp.json().get('organic', [])

            for result in results[:3]:
                paper_url     = result.get('link', '')
                paper_title   = result.get('title', '')
                paper_snippet = result.get('snippet', '')

                if not paper_url or not paper_title:
                    continue

                # Try to scrape abstract/key findings from the paper page
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                    r = requests.get(paper_url, headers=headers, timeout=10)
                    soup = BeautifulSoup(r.text, 'html.parser')

                    # Remove nav/script/style
                    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                        tag.decompose()

                    # Try to get abstract specifically
                    abstract_el = soup.find(id=re.compile(r'abstract', re.I)) or \
                                  soup.find(class_=re.compile(r'abstract', re.I))
                    if abstract_el:
                        content = abstract_el.get_text(separator=' ', strip=True)[:600]
                    else:
                        content = ' '.join(soup.get_text(separator=' ', strip=True).split())[:600]

                    if len(content) > 100:
                        research_findings.append({
                            'title':   paper_title,
                            'url':     paper_url,
                            'excerpt': content,
                            'snippet': paper_snippet,
                        })
                        print(f"    [Research] Found: {paper_title[:60]}...")
                except Exception:
                    # Even if scraping fails, use the snippet
                    if paper_snippet:
                        research_findings.append({
                            'title':   paper_title,
                            'url':     paper_url,
                            'excerpt': paper_snippet,
                            'snippet': paper_snippet,
                        })

        except Exception as e:
            print(f"    [Research search error] {e}")

        time.sleep(1)  # polite delay between searches

    return research_findings[:6]  # cap at 6 papers


def format_research_for_prompt(papers):
    """Format extracted research papers into a clean prompt section."""
    if not papers:
        return "No additional research papers found for this run."

    lines = []
    for i, p in enumerate(papers, 1):
        lines.append(f"Paper {i}: {p['title']}")
        lines.append(f"Source: {p['url']}")
        lines.append(f"Key findings/abstract: {p['excerpt']}")
        lines.append("")
    return '\n'.join(lines)


def generate_content(org_name, org_description, org_body, url):
    """Search research papers, then use Claude to create a tailored article + pitch email."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # --- Step 1: Fetch relevant research papers ---
    print(f"    Searching research papers...")
    topic_hint = f"{org_description} {org_body[:300]}"
    papers = fetch_research_papers(topic_hint)
    research_section = format_research_for_prompt(papers)
    print(f"    Found {len(papers)} research papers")

    # --- Step 2: Generate article + pitch with full context ---
    prompt = f"""
You are a senior financial writer and researcher working with Grade Capital.
Your task: produce (1) a tailored pitch email and (2) a full exclusive article for the publication below.

=== PUBLICATION DETAILS ===
Name        : {org_name}
Website     : {url}
Description : {org_description}
Content tone (inferred from their site): {org_body[:800]}

=== GRADE CAPITAL PROPRIETARY RESEARCH (6 CHAPTERS) ===
{GRADE_CAPITAL_CONTEXT}

=== ADDITIONAL RESEARCH PAPERS (freshly sourced — use findings to add depth) ===
{research_section}

=== ARTICLE INSTRUCTIONS ===
- Length: 1,500–2,000 words
- PRIMARY AUDIENCE: Indian readers — Indian investors, Indian CAs, Indian finance professionals, Indian startups.
  Frame everything from an Indian perspective FIRST. Use Indian examples (₹, lakh, crore, ITR forms, SEBI, RBI, IFSCA).
  Reference Indian regulations (Section 115BBH, 194S, PMLA), Indian institutions, and Indian market context.
  Global data is fine as supporting evidence, but the core narrative must be India-centric.
- Tailor topic, depth, and tone precisely to THIS publication's audience
  (e.g., if it's a CA/tax publication → focus on VDA taxation + derivatives tax advantage;
   if institutional finance → focus on Bitcoin ETF inflows + RWA tokenization + GIFT City;
   if startup/entrepreneur → focus on the founding story + India's crypto opportunity)
- SYNTHESISE both the Grade Capital chapter research AND the external research papers above
- The article must NOT read like anything already on Google — combine proprietary insights with fresh research
- Cite research papers naturally within the article (e.g., "A 2024 SSRN paper found that...")
- Weave in real, verifiable statistics from both sources
- Do NOT make it a Grade Capital advertisement — make it genuinely valuable and research-backed
- End with EXACTLY this author bio line:
  "Mahaveer Soni is Marketing Manager at Grade Capital (https://grade.capital/), India's first regulated crypto derivatives fund."
- The author bio MUST contain a clickable hyperlink to https://grade.capital/

=== PITCH EMAIL INSTRUCTIONS ===
- Max 180 words — professional, concise
- Mention this is an exclusive, research-backed article not published anywhere else
- State clearly: we offer the article free of charge in exchange for two backlinks:
  1) a backlink to Mahaveer Soni's profile/name (linked to grade.capital/team or author page)
  2) a backlink to Grade Capital's website: https://grade.capital/
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

    # Retry up to 3 times with backoff for rate limit errors
    for attempt in range(3):
        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=4096,
                messages=[{'role': 'user', 'content': prompt}],
            )
            text = response.content[0].text
            subject = text.split('===SUBJECT===')[1].split('===PITCH===')[0].strip()
            pitch   = text.split('===PITCH===')[1].split('===ARTICLE===')[0].strip()
            article = text.split('===ARTICLE===')[1].split('===END===')[0].strip()
            return subject, pitch, article
        except Exception as e:
            err = str(e)
            if '429' in err or 'overloaded' in err.lower() or 'rate' in err.lower():
                wait = 30 * (attempt + 1)  # 30s, 60s, 90s
                print(f"  [Claude rate limit] Waiting {wait}s before retry {attempt+1}/3...")
                time.sleep(wait)
            else:
                print(f"  [Claude error] {e}")
                return None, None, None
    print(f"  [Claude] All retries exhausted")
    return None, None, None


def markdown_to_reportlab(text, styles):
    """
    Convert markdown-style text into a list of ReportLab Paragraph flowables.
    Handles: **bold**, # headings, ## subheadings, blank lines as spacers,
    and regular paragraphs with justified alignment.
    """
    # Inline bold: convert **text** → <b>text</b> for ReportLab XML
    def inline_bold(line):
        return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)

    flowables = []
    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 0.2 * cm))
            continue

        if stripped.startswith('### '):
            content = inline_bold(stripped[4:])
            flowables.append(Paragraph(content, styles['h3']))
        elif stripped.startswith('## '):
            content = inline_bold(stripped[3:])
            flowables.append(Paragraph(content, styles['h2']))
        elif stripped.startswith('# '):
            content = inline_bold(stripped[2:])
            flowables.append(Paragraph(content, styles['h1']))
        elif stripped.startswith('- ') or stripped.startswith('* '):
            content = inline_bold(stripped[2:])
            flowables.append(Paragraph(f'• {content}', styles['bullet']))
        else:
            content = inline_bold(stripped)
            flowables.append(Paragraph(content, styles['body']))

    return flowables


def build_article_pdf(subject, article, org_name):
    """
    Build a professionally structured PDF in memory and return the bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    base = getSampleStyleSheet()

    # Custom styles
    styles = {
        'header_brand': ParagraphStyle(
            'header_brand',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        'header_sub': ParagraphStyle(
            'header_sub',
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#555555'),
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        'title': ParagraphStyle(
            'title',
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            leading=26,
        ),
        'byline': ParagraphStyle(
            'byline',
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.HexColor('#777777'),
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        'h1': ParagraphStyle(
            'h1_body',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#1a1a2e'),
            spaceBefore=14,
            spaceAfter=6,
        ),
        'h2': ParagraphStyle(
            'h2_body',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#2c2c54'),
            spaceBefore=10,
            spaceAfter=4,
        ),
        'h3': ParagraphStyle(
            'h3_body',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            spaceBefore=8,
            spaceAfter=3,
        ),
        'body': ParagraphStyle(
            'body_text',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#222222'),
            alignment=TA_JUSTIFY,
            leading=16,
            spaceAfter=6,
        ),
        'bullet': ParagraphStyle(
            'bullet_text',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#222222'),
            leftIndent=14,
            spaceAfter=4,
            leading=15,
        ),
        'footer': ParagraphStyle(
            'footer_text',
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER,
            spaceBefore=6,
        ),
    }

    story = []

    # ── Header ──────────────────────────────────────────────
    story.append(Paragraph('GRADE CAPITAL', styles['header_brand']))
    story.append(Paragraph(
        "India's First Regulated Crypto Derivatives Fund  |  grade.capital",
        styles['header_sub'],
    ))
    story.append(HRFlowable(width='100%', thickness=1.5,
                             color=colors.HexColor('#1a1a2e'), spaceAfter=10))

    # ── Article Title ────────────────────────────────────────
    story.append(Paragraph(subject, styles['title']))
    story.append(Paragraph(
        f"Submitted for consideration — {org_name}  |  "
        f"By Mahaveer Soni, Grade Capital  |  {datetime.date.today().strftime('%B %d, %Y')}",
        styles['byline'],
    ))
    story.append(HRFlowable(width='100%', thickness=0.5,
                             color=colors.HexColor('#cccccc'), spaceAfter=12))

    # ── Article Body ─────────────────────────────────────────
    story.extend(markdown_to_reportlab(article, styles))

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width='100%', thickness=0.5,
                             color=colors.HexColor('#cccccc'), spaceBefore=6))
    story.append(Paragraph(
        'Mahaveer Soni  |  Marketing Manager, Grade Capital  |  '
        'mahaveer@grade.capital  |  https://grade.capital',
        styles['footer'],
    ))
    story.append(Paragraph(
        'Grade Capital is ISO 9001:2015 certified and PMLA compliant.',
        styles['footer'],
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def send_email(to_email, subject, pitch, article, org_name):
    """Send pitch as email body + article as a structured PDF attachment."""
    msg            = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From']    = f"Mahaveer Soni <{SENDER_EMAIL}>"
    msg['To']      = to_email

    # ── Plain-text pitch in email body ───────────────────────
    body = f"""{pitch}

---
Please find the full article attached as a PDF, ready to publish.

Best regards,
Mahaveer Soni
Marketing Manager, Grade Capital
mahaveer@grade.capital | https://grade.capital
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # ── Generate + attach PDF ────────────────────────────────
    try:
        pdf_bytes = build_article_pdf(subject, article, org_name)
        pdf_part  = MIMEBase('application', 'octet-stream')
        pdf_part.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_part)
        safe_title = re.sub(r'[^\w\s-]', '', subject)[:60].strip().replace(' ', '_')
        pdf_part.add_header(
            'Content-Disposition',
            'attachment',
            filename=f"GradeCapital_Article_{safe_title}.pdf",
        )
        msg.attach(pdf_part)
    except Exception as e:
        print(f"  [PDF error] {e} — sending plain text fallback")
        msg.attach(MIMEText(article, 'plain', 'utf-8'))

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
# SELF-TEST — runs before main outreach loop every day
# Sends one test email to mahaveer@grade.capital to confirm
# Claude API + SMTP are both working before touching any orgs.
# ============================================================
def run_self_test():
    """
    1. Do a real Serper search for one generic finance topic.
    2. Generate a short article using Claude API.
    3. Send it to SENDER_EMAIL (mahaveer@grade.capital).
    Returns True if both API and SMTP work, False otherwise.
    """
    print("\n[SELF-TEST] Verifying Claude API + SMTP before outreach...")

    # Step 1: Quick Claude API test — generate a short test blurb
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        test_prompt = (
            "Write exactly 3 sentences about why crypto derivatives are useful for "
            "institutional investors. Be concise and professional."
        )
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=200,
            messages=[{'role': 'user', 'content': test_prompt}],
        )
        test_blurb = response.content[0].text.strip()
        print(f"  [SELF-TEST] Claude API ✓ — got {len(test_blurb)} chars")
    except Exception as e:
        print(f"  [SELF-TEST] Claude API FAILED: {e}")
        return False

    # Step 2: Build a test PDF
    test_subject = f"Grade Capital — Self-Test Article ({datetime.date.today()})"
    test_article = (
        "# Why Crypto Derivatives Matter\n\n"
        f"{test_blurb}\n\n"
        "## Key Benefits\n\n"
        "**Risk management**: Derivatives allow institutions to hedge exposure without "
        "selling underlying positions.\n\n"
        "**Capital efficiency**: Leveraged positions free up capital for other allocations.\n\n"
        "## Conclusion\n\n"
        "This is a **self-test PDF**. If **bold text** appears bold and headings are styled, "
        "the PDF pipeline is working correctly."
    )
    try:
        pdf_bytes = build_article_pdf(test_subject, test_article, "Self-Test")
        print(f"  [SELF-TEST] PDF ✓ — generated {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"  [SELF-TEST] PDF FAILED: {e}")
        return False

    # Step 3: Send test email with PDF attached to our own inbox
    try:
        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"[Grade Capital Outreach — Self-Test] {datetime.date.today()}"
        msg['From']    = f"Mahaveer Soni <{SENDER_EMAIL}>"
        msg['To']      = SENDER_EMAIL
        body = (
            "Automated self-test before today's outreach run.\n"
            "Claude API + SMTP + PDF generation all working.\n\n"
            "Check the attached PDF — bold text should be bold, headings styled.\n\n"
            "-- Grade Capital Outreach Bot"
        )
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        pdf_part = MIMEBase('application', 'octet-stream')
        pdf_part.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_part)
        pdf_part.add_header('Content-Disposition', 'attachment',
                            filename=f"GradeCapital_SelfTest_{datetime.date.today()}.pdf")
        msg.attach(pdf_part)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
        print(f"  [SELF-TEST] SMTP ✓ — test email + PDF sent to {SENDER_EMAIL}")
    except Exception as e:
        print(f"  [SELF-TEST] SMTP FAILED: {e}")
        return False

    print("[SELF-TEST] All checks passed — proceeding with outreach.\n")
    return True


# ============================================================
# MAIN
# ============================================================
def main():
    today = datetime.date.today()
    print(f"\n{'='*60}")
    print(f"  Grade Capital Outreach — {today}")
    print(f"  Target: {ORGS_PER_DAY} organisations today")
    print(f"{'='*60}\n")

    # --- Self-test: verify Claude API + SMTP before touching any org ---
    if not run_self_test():
        print("\n[ABORT] Self-test failed. No outreach emails sent today.")
        print("Check ANTHROPIC_API_KEY and EMAIL_PASSWORD secrets.\n")
        raise SystemExit(1)

    # --- Send follow-up emails to orgs contacted 2 days ago ---
    run_followups()

    sent_log = load_sent_log()

    # ── PHASE 1: Keep searching until ORGS_PER_DAY orgs WITH confirmed emails are found ──
    # Only an org that yields a real contact email is added to the qualified list.
    # We search in rounds (one query per round) until the target is met.
    qualified       = []   # list of dicts: {url, org_name, email, snippet, org_data}
    tried_urls      = set()
    qualified_emails = set()  # track emails already queued this session — avoid duplicate sends
    day_index     = today.timetuple().tm_yday
    max_rounds    = 8    # safety cap — won't loop forever
    round_num     = 0

    print(f"Target: {ORGS_PER_DAY} organisations with confirmed emails.\n")

    while len(qualified) < ORGS_PER_DAY and round_num < max_rounds:
        round_num += 1
        query = SEARCH_QUERIES[(day_index + round_num - 1) % len(SEARCH_QUERIES)]
        print(f"[Round {round_num}] Query: {query}")
        print(f"  Qualified so far: {len(qualified)}/{ORGS_PER_DAY}\n")

        results = search_organizations(query, num=20)
        random.shuffle(results)

        for result in results:
            if len(qualified) >= ORGS_PER_DAY:
                break

            url      = result.get('link', '').strip()
            org_name = result.get('title', url)
            snippet  = result.get('snippet', '')

            if not url or url in tried_urls:
                continue
            tried_urls.add(url)

            # Skip irrelevant or already contacted
            if any(d in url.lower() for d in SKIP_DOMAINS):
                continue
            if url.lower() in sent_log:
                print(f"  [skip] Already contacted: {org_name}")
                continue

            print(f"  Checking: {org_name}")
            print(f"    URL: {url}")

            # --- Scrape ---
            org_data = scrape_org(url)
            if not org_data:
                print(f"    Scrape failed — skipping")
                log_result(org_name, url, '', '', 'scrape_failed')
                continue

            # --- Find email — only qualify if email found ---
            email = find_contact_email(url, org_data)
            if not email:
                print(f"    No email found — not adding to queue")
                log_result(org_name, url, '', '', 'no_email')
                continue

            if email.lower() in sent_log:
                print(f"    Email {email} already contacted — skipping")
                continue

            if email.lower() in qualified_emails:
                print(f"    Email {email} already queued this session — skipping duplicate")
                continue

            # ✅ Has a confirmed email — add to qualified list
            print(f"    ✅ Qualified! Email: {email}")
            qualified_emails.add(email.lower())
            qualified.append({
                'url':      url,
                'org_name': org_name,
                'email':    email,
                'snippet':  snippet,
                'org_data': org_data,
            })

    print(f"\n{'='*60}")
    print(f"  Phase 1 done. {len(qualified)} organisations qualified with emails.")
    print(f"{'='*60}\n")

    # ── PHASE 2: Generate content and send to every qualified org ──
    contacted = 0
    for org in qualified:
        url      = org['url']
        org_name = org['org_name']
        email    = org['email']
        snippet  = org['snippet']
        org_data = org['org_data']

        print(f"\n[{contacted+1}/{len(qualified)}] Sending to: {org_name} <{email}>")

        description = org_data.get('description') or snippet
        subject, pitch, article = generate_content(
            org_name, description, org_data.get('body', ''), url
        )
        if not subject:
            print(f"    Content generation failed — skipping")
            log_result(org_name, url, email, '', 'generation_failed')
            continue

        print(f"    Subject: {subject}")

        success = send_email(email, subject, pitch, article, org_name)
        status  = 'sent' if success else 'email_failed'
        log_result(org_name, url, email, subject, status)

        if success:
            print(f"    ✅ Sent!")
            sent_log.add(url.lower())
            sent_log.add(email.lower())
            contacted += 1
        else:
            print(f"    ❌ Email send failed")

        time.sleep(random.uniform(4, 8))

    print(f"\n{'='*60}")
    print(f"  Done. Sent to {contacted} organisations today.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
