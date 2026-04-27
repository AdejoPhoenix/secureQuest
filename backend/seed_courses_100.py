#!/usr/bin/env python3
"""Seed 100 additional security awareness courses.
Usage: python seed_courses_100.py [BASE_URL]
"""
import sys, os
from dotenv import load_dotenv
import requests

load_dotenv()
BASE  = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE_URL","http://localhost:8000")).rstrip("/")+"/api/v1"
EMAIL = os.environ.get("SEED_ADMIN_EMAIL","admin@securequest.local")
PASSW = os.environ.get("SEED_ADMIN_PASSWORD","Admin1234!")

def login():
    r = requests.post(f"{BASE}/auth/login", json={"email":EMAIL,"password":PASSW})
    if not r.ok: print(f"Login failed: {r.text}"); sys.exit(1)
    print(f"✔ Logged in as {EMAIL}\n"); return r.json()["access_token"]

def api(method, path, tok, **kw):
    r = getattr(requests,method)(f"{BASE}{path}", headers={"Authorization":f"Bearer {tok}"}, **kw)
    if not r.ok: print(f"  ✗ {r.status_code}: {r.text[:200]}"); r.raise_for_status()
    return r.json()

def C(tok, **kw):
    c = api("post", "/admin/courses/", tok, json=kw)
    print(f"  ✓ [{c['id']:>3}] {c['name']}"); return c["id"]

def M(tok, cid, **kw):
    api("post", f"/admin/courses/{cid}/modules", tok, json=kw)

def yt(v, title):
    return (f'<div class="ratio ratio-16x9 mb-3 rounded overflow-hidden border border-secondary">'
            f'<iframe src="https://www.youtube.com/embed/{v}" title="{title}" frameborder="0" allowfullscreen></iframe></div>\n')

def lesson(body): return {"body": body, "callouts": []}
def warn(body, tip): return {"body": body, "callouts": [{"type":"warning","text":tip}]}
def quiz(*qs): return {"questions": list(qs)}
def q(text, a, b, c, d, correct, exp): return {"text":text,"options":{"a":a,"b":b,"c":c,"d":d},"correct":correct,"explanation":exp}
def scenario(desc, *choices): return {"description":desc,"choices":[{"text":t,"outcome":o,"is_correct":ok} for t,o,ok in choices]}
def dragdrop(instruction, categories, items): return {"instruction":instruction,"categories":categories,"items":[{"text":t,"category":cat} for t,cat in items]}

# YouTube IDs
PHI="b3DNc4QE1Sg"; PWD="aEmgNkxUcVQ"; SOC="lc7scxvKQOo"; MAL="n8mbzU0X2nQ"
NET="ZxL4UPCm4WY"; WEB="JV-PGJ2ArEY"; GDP="4p4y1C2YL7Q"; INC="bzNADLfFo2Q"
CLD="M988_fsOSWo"; MOB="3GmCLlMkFno"; MFA="hGRii5f_usc"; VPN="R-JUOpCgTZc"
FWL="kDEX1HXybrU"; ZTR="FCX0IhRsMOM"; IOT="ycgRZPi1VFM"; BEC="XBkzBrXlle0"

def seed(tok):
    # ── PHISHING (20) ─────────────────────────────────────────────────────────
    print("\n── PHISHING ──")

    cid = C(tok, name="Spot the Phish", category="phishing", difficulty="easy",
            description="Learn to identify phishing emails in under 5 minutes.", xp_reward=50,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="What Is Phishing?", type="lesson", order=1, xp_reward=15,
      content=warn(yt(PHI,"Phishing explained")+"<p>Phishing tricks you into revealing credentials by impersonating trusted senders.</p>",
                   "Never click links in unexpected emails asking for your password."))
    M(tok, cid, title="Real or Fake?", type="quiz", order=2, xp_reward=35,
      content=quiz(q("An email says 'Verify your account or it will be deleted.' What should you do?",
                     "Click the link immediately","Go to the site directly by typing the URL",
                     "Reply with your password","Ignore all future emails","b",
                     "Always navigate directly to the site rather than clicking email links.")))

    cid = C(tok, name="Email Red Flags", category="phishing", difficulty="easy",
            description="Recognise the warning signs buried in phishing messages.", xp_reward=50,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Anatomy of a Phishing Email", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(PHI,"Phishing anatomy")+"<p>Key red flags: mismatched sender domain, urgent language, generic greeting, suspicious attachments.</p>"))
    M(tok, cid, title="Sort the Red Flags", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Drag each signal to the correct category",
                       ["Red Flag","Legitimate"],
                       [("Urgent: Act now or lose access","Red Flag"),("From: support@paypa1.com","Red Flag"),
                        ("Dear Customer","Red Flag"),("From: hr@yourcompany.com","Legitimate"),
                        ("Your name personalised in greeting","Legitimate")]))

    cid = C(tok, name="Link Inspection 101", category="phishing", difficulty="easy",
            description="Hover before you click — a hands-on hover-link drill.", xp_reward=50,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="How to Read a URL", type="lesson", order=1, xp_reward=20,
      content=warn("<p>The real domain is the part just before the first single <code>/</code>. <code>secure.paypal.com</code> is PayPal. <code>paypal.secure-login.xyz</code> is NOT PayPal.</p>",
                   "Check the domain, not just the subdomain, before clicking."))
    M(tok, cid, title="Safe or Suspicious?", type="quiz", order=2, xp_reward=30,
      content=quiz(q("Which URL is the real Microsoft login?",
                     "microsoft.login-secure.com","account.microsoft.com.phish.net",
                     "login.microsoftonline.com","microsofft.com","c",
                     "login.microsoftonline.com is the legitimate Microsoft identity endpoint.")))

    cid = C(tok, name="Smishing & Vishing", category="phishing", difficulty="easy",
            description="Phishing via SMS and phone calls.", xp_reward=60,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Beyond Email Phishing", type="lesson", order=1, xp_reward=25,
      content=lesson(yt(SOC,"Smishing vishing")+"<p>Smishing = SMS phishing. Vishing = voice phishing. Both use urgency and authority to bypass your guard.</p>"))
    M(tok, cid, title="Handle the Call", type="scenario", order=2, xp_reward=35,
      content=scenario("'This is IT Support. Your account was compromised. Give me your password to reset it.'",
                       ("Give the password — it's IT!","You've been socially engineered.",False),
                       ("Hang up and call IT using the number from the company directory.",
                        "Correct. Always verify through a known-good channel.",True),
                       ("Ask them to email you instead","Better, but the attacker may email too.",False)))

    cid = C(tok, name="Spear Phishing Deep Dive", category="phishing", difficulty="medium",
            description="Targeted attacks that use personal details to appear credible.", xp_reward=75,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Personalised Attacks", type="lesson", order=1, xp_reward=30,
      content=warn(yt(PHI,"Spear phishing")+"<p>Spear phishing uses your name, role, and recent activity harvested from LinkedIn or social media to craft convincing lures.</p>",
                   "A message that knows your name and job title is MORE suspicious, not less."))
    M(tok, cid, title="Classify the Attack", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Is this mass phishing or spear phishing?",
                       ["Mass Phishing","Spear Phishing"],
                       [("Dear Customer, verify your account","Mass Phishing"),
                        ("Hi Alex, saw your LinkedIn post about the merger — please review this contract","Spear Phishing"),
                        ("Your package is delayed — click here","Mass Phishing"),
                        ("As discussed in yesterday's meeting with Sarah...","Spear Phishing")]))

    cid = C(tok, name="Whaling: CEO Fraud", category="phishing", difficulty="medium",
            description="Phishing attacks targeting executives.", xp_reward=75,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="What Is Whaling?", type="lesson", order=1, xp_reward=30,
      content=lesson(yt(BEC,"CEO fraud whaling")+"<p>Whaling targets C-suite executives. Attackers research the org chart and craft emails that appear to come from board members or regulators.</p>"))
    M(tok, cid, title="CEO Wire Transfer", type="scenario", order=2, xp_reward=45,
      content=scenario("You receive an email from the 'CEO': 'I need a $50k wire transfer for an urgent acquisition. Keep this confidential and do it now.'",
                       ("Process it — the CEO asked","You've enabled a wire fraud attack.",False),
                       ("Call the CEO on their known mobile number to verify",
                        "Correct. Verbal confirmation via a trusted channel stops wire fraud.",True),
                       ("Reply to the email asking for more details","The attacker controls that inbox.",False)))

    cid = C(tok, name="Phishing Simulation Awareness", category="phishing", difficulty="medium",
            description="Why companies run phishing simulations and what to do when you spot one.", xp_reward=75,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Phishing Tests at Work", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Security teams send simulated phishing emails to measure awareness. If you click, you'll be redirected to training — not punished. The goal is learning.</p>"))
    M(tok, cid, title="Simulation Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("You clicked a simulated phishing link. What should you do next?",
                     "Pretend it didn't happen","Complete the follow-up training",
                     "Report your IT team for tricking you","Forward the link to colleagues","b",
                     "Simulations are learning opportunities. Complete the training to reduce future risk.")))

    cid = C(tok, name="Business Email Compromise", category="phishing", difficulty="medium",
            description="How attackers hijack or impersonate business email accounts.", xp_reward=80,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="BEC Attack Patterns", type="lesson", order=1, xp_reward=35,
      content=lesson(yt(BEC,"Business email compromise")+"<p>BEC attackers either compromise a real account or spoof one to redirect payments, steal data, or gain access.</p>"))
    M(tok, cid, title="BEC Scenario", type="scenario", order=2, xp_reward=45,
      content=scenario("Your supplier emails: 'We changed our bank details, please update your records and send next payment to: [new account]'",
                       ("Update immediately — suppliers do change banks","Attackers frequently intercept supplier email to redirect payments.",False),
                       ("Call the supplier on a phone number from your existing records to verify",
                        "Correct. Always verify bank detail changes via a separate trusted channel.",True),
                       ("Email back asking for confirmation","The attacker controls the email thread.",False)))

    cid = C(tok, name="Phishing Indicators: Technical", category="phishing", difficulty="medium",
            description="Look under the hood — email headers, SPF, DKIM, and DMARC.", xp_reward=80,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Email Authentication Explained", type="lesson", order=1, xp_reward=35,
      content=warn("<p><strong>SPF</strong> — authorised sending servers. <strong>DKIM</strong> — cryptographic signature. <strong>DMARC</strong> — policy for failures. If these fail, the email is suspicious even if it looks legitimate.</p>",
                   "Modern email clients show authentication status. Look for the lock or warning icon."))
    M(tok, cid, title="Header Analysis Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("An email claims to be from bank.com but the SPF check says 'FAIL'. What does this mean?",
                     "The email server is temporarily down","The email was not sent from an authorised bank.com server",
                     "SPF failures are normal and safe to ignore","The email is definitely a phishing attempt","b",
                     "SPF FAIL means the sending server isn't authorised — treat with high suspicion.")))

    cid = C(tok, name="Phishing Response Playbook", category="phishing", difficulty="medium",
            description="Step-by-step: what to do when you receive a phishing email.", xp_reward=80,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="The 4-Step Response", type="lesson", order=1, xp_reward=35,
      content=lesson("<p>1. <strong>Don't click</strong> — not even to inspect. 2. <strong>Report</strong> via the built-in phishing report button or email security@. 3. <strong>Delete</strong> the message. 4. <strong>Warn</strong> colleagues if relevant. If you already clicked: isolate the device and call IT immediately.</p>"))
    M(tok, cid, title="Response Drill", type="scenario", order=2, xp_reward=45,
      content=scenario("You receive a suspicious email with an attachment claiming to be an invoice.",
                       ("Open the attachment to check if it's real","Malware executes on open.",False),
                       ("Report it to your security team, then delete it",
                        "Correct. Never open attachments from unexpected senders.",True),
                       ("Forward to a colleague to get a second opinion","You may spread the threat.",False)))

    cid = C(tok, name="Clone Phishing", category="phishing", difficulty="hard",
            description="Attackers duplicate legitimate emails to slip past your guard.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="What Is Clone Phishing?", type="lesson", order=1, xp_reward=40,
      content=warn(yt(PHI,"Clone phishing")+"<p>Clone phishing copies a legitimate email you already received, replaces links/attachments with malicious ones, and resends it appearing to come from the original sender.</p>",
                   "Be suspicious of duplicate emails — especially if links or attachments differ from the original."))
    M(tok, cid, title="Spot the Clone", type="quiz", order=2, xp_reward=60,
      content=quiz(q("You receive what looks like a re-sent version of a software update email. How do you verify it's safe?",
                     "It's the same email so it must be safe","Compare all URLs with the original using hover-preview",
                     "Open the attachment quickly before it expires","Reply asking the sender to confirm","b",
                     "Always hover-check links even in emails that look familiar.")))

    cid = C(tok, name="Angler Phishing on Social Media", category="phishing", difficulty="hard",
            description="Fake customer-service accounts harvesting credentials on social platforms.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Social Media Phishing", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Angler phishing: attackers monitor brand mentions on Twitter/X, LinkedIn, etc., then respond as fake support accounts offering to help — leading victims to credential-harvesting pages.</p>"))
    M(tok, cid, title="Verify the Account", type="scenario", order=2, xp_reward=60,
      content=scenario("You tweet about a billing issue. '@BankSupport_Help' DMs you a link to log in and resolve it.",
                       ("Click the link — they responded quickly","Fake support accounts reply within seconds.",False),
                       ("Go to the bank's official website or app directly",
                        "Correct. Never use links from unsolicited social media DMs.",True),
                       ("Reply with your account number so they can help","Never share account details in DMs.",False)))

    cid = C(tok, name="Pharming Attacks", category="phishing", difficulty="hard",
            description="DNS poisoning and local hosts-file manipulation to redirect traffic.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Pharming vs Phishing", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Phishing brings you to a fake site via a link. Pharming hijacks DNS so even typing the correct URL sends you to a fake site. Signs: invalid SSL cert, slight visual differences, login failing then re-prompting.</p>",
                   "Always check for valid HTTPS and the correct certificate issuer, even when you typed the URL yourself."))
    M(tok, cid, title="Pharming Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("You type your bank's URL correctly but see a 'certificate not trusted' warning. What should you do?",
                     "Click 'Proceed anyway' — you typed the URL correctly","Stop and call your bank directly",
                     "Clear cookies and try again","Use a different browser","b",
                     "A cert warning on a familiar site may indicate pharming or MITM. Don't proceed.")))

    cid = C(tok, name="QR Code Phishing (Quishing)", category="phishing", difficulty="hard",
            description="Malicious QR codes bypassing email security filters.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="The QR Code Threat", type="lesson", order=1, xp_reward=40,
      content=warn("<p>QR codes in emails bypass URL scanners because security tools can't easily read image-encoded URLs. Scanning with your phone takes you outside corporate network protection.</p>",
                   "Never scan QR codes received in unexpected emails, especially ones claiming urgency."))
    M(tok, cid, title="Quishing Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("An email from 'IT Security' says you must scan a QR code within 24 hours to re-verify your MFA device.",
                       ("Scan immediately — security re-verification is important","The urgency is a social engineering tactic.",False),
                       ("Go to the IT portal directly via browser and check for any required actions",
                        "Correct. Verify security actions through official channels, not QR codes.",True),
                       ("Forward to a colleague to see if they got it too","Don't spread potential quishing links.",False)))

    cid = C(tok, name="Voice Deepfake Phishing", category="phishing", difficulty="hard",
            description="AI-generated voice clones used in vishing attacks.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="AI Voice Cloning Threats", type="lesson", order=1, xp_reward=40,
      content=lesson(yt(SOC,"AI voice cloning vishing")+"<p>Attackers clone executive voices using AI tools trained on publicly available audio (interviews, podcasts). Establish a voice code word with your team for sensitive approvals.</p>"))
    M(tok, cid, title="Deepfake Call", type="scenario", order=2, xp_reward=60,
      content=scenario("A voice call sounds exactly like your CFO, asking you to approve an emergency wire transfer.",
                       ("Approve it — the voice is unmistakable","AI voice cloning is now near-perfect.",False),
                       ("Hang up and call the CFO back on a number from your company directory",
                        "Correct. Always re-establish contact through a trusted channel.",True),
                       ("Ask for their employee ID number","IDs can be researched via LinkedIn.",False)))

    cid = C(tok, name="OAuth Phishing", category="phishing", difficulty="hard",
            description="Consent phishing that hijacks OAuth app authorisation.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Malicious OAuth Apps", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Attackers create malicious OAuth apps with names like 'DocuSign' or 'Teams'. When you grant permissions, they get persistent access to your email, files, and contacts — no password needed.</p>",
                   "Only authorise OAuth apps you deliberately sought out. Review granted app permissions quarterly."))
    M(tok, cid, title="Suspicious OAuth Request", type="quiz", order=2, xp_reward=60,
      content=quiz(q("An OAuth consent screen asks for 'Read and write access to all your emails and files'. You don't recognise the app. What do you do?",
                     "Grant it — OAuth is secure","Deny and report to IT security",
                     "Grant read but not write access","Check the app's star rating","b",
                     "Unexpected OAuth requests for broad permissions are a major red flag.")))

    cid = C(tok, name="Phishing in Collaboration Tools", category="phishing", difficulty="hard",
            description="Teams, Slack, and SharePoint used to deliver phishing payloads.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Phishing Beyond Email", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Attackers now use compromised accounts in Teams or Slack to send malicious links from trusted contacts. SharePoint and OneDrive phishing pages look near-identical to Microsoft originals.</p>"))
    M(tok, cid, title="Teams Message Drill", type="scenario", order=2, xp_reward=60,
      content=scenario("A Teams message from a colleague (whose account was compromised) sends: 'Here's that doc you asked about [SharePoint link]'",
                       ("Open it — I know this person","Their account is compromised.",False),
                       ("Verify with the colleague via a phone call or video before clicking",
                        "Correct. Compromised accounts make trusted contacts dangerous.",True),
                       ("Reply asking what the doc is about","The attacker will provide a convincing answer.",False)))

    cid = C(tok, name="Advanced Phishing Detection Lab", category="phishing", difficulty="hard",
            description="Hands-on classification of advanced phishing techniques.", xp_reward=100,
            thumbnail_color="#f59e0b", is_published=True)
    M(tok, cid, title="Multi-Stage Phishing Chains", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Modern phishing chains use multiple stages: initial email → CAPTCHA page (bypasses sandboxes) → redirect → credential harvest page. Each stage filters out automated scanners.</p>",
                   "Legitimate services never chain you through multiple redirects to reach a login page."))
    M(tok, cid, title="Classify the Chain", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Assign each element to its role in a phishing chain",
                       ["Delivery","Evasion","Harvest"],
                       [("Spear phishing email with PDF","Delivery"),("CAPTCHA page to block scanners","Evasion"),
                        ("Redirect through geo-filter","Evasion"),("Fake Microsoft login page","Harvest"),
                        ("Malicious QR code in PDF","Delivery")]))

    # ── PASSWORDS (10) ────────────────────────────────────────────────────────
    print("\n── PASSWORDS ──")

    cid = C(tok, name="Password Basics", category="passwords", difficulty="easy",
            description="Why weak passwords fail and what makes a strong one.", xp_reward=50,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="Strong vs Weak Passwords", type="lesson", order=1, xp_reward=20,
      content=warn(yt(PWD,"Password security basics")+"<p>Length beats complexity. A 16-character passphrase is stronger than a 8-character mix of symbols.</p>",
                   "Never reuse passwords across sites. One breach exposes all accounts."))
    M(tok, cid, title="Rate the Password", type="quiz", order=2, xp_reward=30,
      content=quiz(q("Which password is strongest?",
                     "P@ssw0rd!","correct-horse-battery-staple",
                     "Admin123","qwerty2024","b",
                     "Length wins. A long passphrase is exponentially harder to crack than short complex strings.")))

    cid = C(tok, name="Password Managers", category="passwords", difficulty="easy",
            description="How password managers work and why you need one.", xp_reward=50,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="The Case for a Password Manager", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(PWD,"Password managers explained")+"<p>A password manager generates, stores, and auto-fills unique passwords. You remember one master password; it handles the rest.</p>"))
    M(tok, cid, title="Password Manager Myths", type="quiz", order=2, xp_reward=30,
      content=quiz(q("'Storing all passwords in one place is a single point of failure.' How do reputable managers address this?",
                     "They don't — it's a valid concern","Zero-knowledge encryption: even the provider can't read your vault",
                     "They back up passwords to email","They limit you to 20 passwords","b",
                     "Zero-knowledge architecture means your master password never leaves your device in readable form.")))

    cid = C(tok, name="Multi-Factor Authentication", category="passwords", difficulty="easy",
            description="Add a second layer: what MFA is and how to enable it.", xp_reward=60,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="MFA Explained", type="lesson", order=1, xp_reward=25,
      content=lesson(yt(MFA,"MFA multi-factor authentication")+"<p>MFA combines something you <em>know</em> (password) + something you <em>have</em> (phone/key) + something you <em>are</em> (biometric). Even a stolen password can't log in without the second factor.</p>"))
    M(tok, cid, title="Strongest MFA Type", type="quiz", order=2, xp_reward=35,
      content=quiz(q("Which MFA method is most resistant to phishing?",
                     "SMS one-time code","Hardware security key (FIDO2)",
                     "Email one-time code","Security questions","b",
                     "Hardware keys use cryptographic challenge-response tied to the real domain — phishing sites can't intercept them.")))

    cid = C(tok, name="Credential Stuffing", category="passwords", difficulty="easy",
            description="Why data breaches on one site threaten all your accounts.", xp_reward=60,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="How Credential Stuffing Works", type="lesson", order=1, xp_reward=25,
      content=warn("<p>Attackers take username/password pairs from one breach and try them on hundreds of other sites automatically. Unique passwords make this attack useless.</p>",
                   "Check haveibeenpwned.com to see if your email has appeared in known breaches."))
    M(tok, cid, title="Breach Response", type="scenario", order=2, xp_reward=35,
      content=scenario("You get an alert that your email appeared in a data breach from a shopping site you used.",
                       ("Ignore it — it was just a shopping site","Your password may be used on other sites.",False),
                       ("Change that password and any other accounts using the same password",
                        "Correct. Unique passwords limit breach blast radius.",True),
                       ("Delete the shopping account","Good, but still change any reused passwords.",False)))

    cid = C(tok, name="Password Spraying", category="passwords", difficulty="medium",
            description="Detect and defend against low-and-slow password attacks.", xp_reward=75,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="Spraying vs Brute Force", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Brute force tries many passwords on one account (locked out fast). Password spraying tries one common password (e.g. 'Summer2024!') across thousands of accounts — avoiding lockouts.</p>"))
    M(tok, cid, title="Spray Defence Drill", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Which controls defend against password spraying?",
                       ["Effective","Not Effective"],
                       [("Enforce MFA","Effective"),("Unique complex passwords","Effective"),
                        ("Account lockout after 3 attempts","Not Effective"),
                        ("Block common passwords at creation","Effective"),
                        ("Longer minimum password length","Effective")]))

    cid = C(tok, name="Passkeys: The Password Killer", category="passwords", difficulty="medium",
            description="How passkeys replace passwords using public-key cryptography.", xp_reward=75,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="How Passkeys Work", type="lesson", order=1, xp_reward=30,
      content=lesson(yt(MFA,"Passkeys explained")+"<p>Passkeys use a private key stored on your device and a public key on the server. Authentication proves possession of the private key — no password is ever transmitted or stored.</p>"))
    M(tok, cid, title="Passkey Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("If a server storing passkey data is breached, what can an attacker access?",
                     "Your password","Your private key",
                     "Only your public key — useless without the device","Your biometric data","c",
                     "Public keys can't authenticate without the corresponding private key on your device.")))

    cid = C(tok, name="Password Policy Design", category="passwords", difficulty="medium",
            description="For IT teams: writing effective password policies that users will follow.", xp_reward=80,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="NIST Password Guidelines", type="lesson", order=1, xp_reward=35,
      content=warn("<p>NIST SP 800-63B recommends: minimum 8 chars (15+ for admins), no forced rotation, block known-breached passwords, no complexity rules that encourage predictable substitutions (P@ssw0rd).</p>",
                   "Forced rotation makes passwords weaker — users predictably increment (Password1 → Password2)."))
    M(tok, cid, title="Policy Review", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Your current policy forces password change every 90 days. According to NIST, when should you force a change?",
                     "Every 30 days","Every 90 days",
                     "Only when a breach is suspected","Annually","c",
                     "NIST 800-63B: change only when compromise is suspected. Rotation fatigue weakens security.")))

    cid = C(tok, name="Hash Cracking & Rainbow Tables", category="passwords", difficulty="hard",
            description="How attackers crack stored passwords and how salting stops them.", xp_reward=100,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="Password Hashing Fundamentals", type="lesson", order=1, xp_reward=40,
      content=warn("<p>MD5/SHA1 are too fast for passwords — attackers crack billions/sec. Use bcrypt, scrypt, or Argon2. Salts ensure identical passwords hash differently, defeating rainbow tables.</p>",
                   "Never store passwords in plain text or with reversible encryption."))
    M(tok, cid, title="Hashing Concepts", type="quiz", order=2, xp_reward=60,
      content=quiz(q("Two users have the same password. With proper salting, their stored hashes should be:",
                     "Identical","Different",
                     "Both empty","Reversed","b",
                     "Unique salts per user ensure identical passwords produce different hashes, defeating precomputed attacks.")))

    cid = C(tok, name="Zero Trust Identity", category="passwords", difficulty="hard",
            description="Never trust, always verify — rethinking authentication in modern environments.", xp_reward=100,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="Zero Trust Auth Principles", type="lesson", order=1, xp_reward=40,
      content=lesson(yt(ZTR,"Zero trust security")+"<p>Zero Trust assumes breach: verify every user, every device, every time. Combine strong MFA with device health checks, least-privilege access, and continuous session monitoring.</p>"))
    M(tok, cid, title="Zero Trust Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("An employee connects from a personal laptop on public Wi-Fi and authenticates with MFA. Should they get full access?",
                       ("Yes — MFA passed, access granted","Device health and network context matter.",False),
                       ("Limited access — device isn't managed; apply conditional access policies",
                        "Correct. Zero Trust evaluates identity + device + network + behaviour.",True),
                       ("Block completely until they're in the office","Too restrictive; context-aware access is better.",False)))

    cid = C(tok, name="Account Takeover Response", category="passwords", difficulty="hard",
            description="Incident response when an account is compromised.", xp_reward=100,
            thumbnail_color="#3b82f6", is_published=True)
    M(tok, cid, title="Account Takeover Indicators", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Signs: unexpected password reset emails, login alerts from unknown locations, unfamiliar sent messages, contacts receiving odd messages from you.</p>",
                   "Act fast: attackers add forwarding rules and recovery email changes to maintain persistence."))
    M(tok, cid, title="ATO Response Order", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Order these ATO response steps correctly (drag to correct phase)",
                       ["Immediate","Short-term","Long-term"],
                       [("Change password immediately","Immediate"),("Revoke all active sessions","Immediate"),
                        ("Review forwarding rules and recovery info","Short-term"),
                        ("Enable MFA if not already on","Short-term"),
                        ("Audit what data the attacker accessed","Long-term")]))

    # ── SOCIAL ENGINEERING (10) ───────────────────────────────────────────────
    print("\n── SOCIAL ENGINEERING ──")

    cid = C(tok, name="The Art of Pretexting", category="social_engineering", difficulty="easy",
            description="How attackers build fake identities to manipulate targets.", xp_reward=50,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="What Is Pretexting?", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(SOC,"Social engineering pretexting")+"<p>Pretexting creates a fabricated scenario (pretext) to gain trust. Common pretexts: IT support, auditor, new employee, delivery driver, journalist.</p>"))
    M(tok, cid, title="Spot the Pretext", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Is this a legitimate request or a pretext?",
                       ["Legitimate","Pretext"],
                       [("IT sends a calendar invite for scheduled maintenance","Legitimate"),
                        ("Unknown caller claims to be from IT and needs your login to 'fix an issue'","Pretext"),
                        ("HR emails from the verified company domain about a policy update","Legitimate"),
                        ("'Auditor' arrives unannounced asking for server room access","Pretext")]))

    cid = C(tok, name="Tailgating & Piggybacking", category="social_engineering", difficulty="easy",
            description="Physical security breaches through social manipulation.", xp_reward=50,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Physical Social Engineering", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Tailgating: following an authorised person through a secure door without badging in. Piggybacking: doing the same with the person's knowledge/consent. Both bypass physical access controls.</p>",
                   "Hold the door for people — but never for secured areas. Every person must badge in."))
    M(tok, cid, title="Tailgating Response", type="scenario", order=2, xp_reward=30,
      content=scenario("Someone approaches behind you as you badge into the server room: 'I forgot my badge — can you hold it?'",
                       ("Hold the door — they work here","You cannot verify their access level.",False),
                       ("Politely decline and direct them to reception to get a temporary badge",
                        "Correct. Individual badge-in is non-negotiable for secure areas.",True),
                       ("Let them in but report it later","Reporting after is too late.",False)))

    cid = C(tok, name="Authority & Urgency Tactics", category="social_engineering", difficulty="easy",
            description="Why people comply with authoritative urgent requests — and how to resist.", xp_reward=50,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Cialdini's Influence Principles", type="lesson", order=1, xp_reward=20,
      content=lesson("<p>Attackers exploit cognitive biases: <strong>Authority</strong> (I'm from the FBI), <strong>Urgency</strong> (Act now or lose access), <strong>Social proof</strong> (Everyone else already did this), <strong>Scarcity</strong> (Only 2 slots left).</p>"))
    M(tok, cid, title="Influence Tactics Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("'URGENT: Your Microsoft 365 licence expires in 1 hour. Click here to renew immediately.' Which bias is being exploited?",
                     "Social proof","Scarcity","Urgency and authority","Reciprocity","c",
                     "Urgency + authority (Microsoft) override rational thinking. Verify through official channels.")))

    cid = C(tok, name="Insider Threat Awareness", category="social_engineering", difficulty="medium",
            description="Recognising and responding to malicious insider behaviour.", xp_reward=75,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Types of Insider Threats", type="lesson", order=1, xp_reward=30,
      content=warn(yt(INC,"Insider threat awareness")+"<p>Malicious insiders: deliberately steal or damage. Negligent insiders: careless with data. Compromised insiders: credentials stolen externally. Each needs different controls.</p>",
                   "Unusual access patterns (off-hours large downloads, accessing unfamiliar systems) are early indicators."))
    M(tok, cid, title="Classify the Threat", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Classify each insider scenario",
                       ["Malicious","Negligent","Compromised"],
                       [("Employee copies client database before resignation","Malicious"),
                        ("Employee clicks phishing link, credentials stolen","Compromised"),
                        ("Employee emails client data to personal account for home working","Negligent"),
                        ("Account logs in at 3am from overseas IP","Compromised"),
                        ("Employee deletes records to cover up errors","Malicious")]))

    cid = C(tok, name="Dumpster Diving & OSINT", category="social_engineering", difficulty="medium",
            description="How attackers harvest intelligence from physical and online sources.", xp_reward=75,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Open Source Intelligence", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Attackers use LinkedIn, job postings, company websites, and discarded documents to build target profiles. Job postings reveal tech stack; LinkedIn reveals org structure; discarded printouts reveal internal processes.</p>"))
    M(tok, cid, title="OSINT Risk Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Your company posts a job ad listing 'Must have experience with Cisco ASA firewalls, Splunk SIEM, and Windows Server 2022.' What risk does this create?",
                     "None — job ads are public","Reveals your exact tech stack to potential attackers",
                     "Makes you more attractive to talented candidates only","Violates GDPR","b",
                     "Tech stack disclosure in job ads gives attackers a targeted vulnerability research list.")))

    cid = C(tok, name="Social Engineering in the AI Age", category="social_engineering", difficulty="medium",
            description="How AI amplifies social engineering attacks at scale.", xp_reward=80,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="AI-Powered Social Engineering", type="lesson", order=1, xp_reward=35,
      content=warn("<p>AI enables: hyper-personalised spear phishing at scale, deepfake audio/video for impersonation, chatbots that pass as humans in support scams, automated OSINT to build target profiles.</p>",
                   "The barrier to sophisticated social engineering has collapsed. Treat all unexpected requests with elevated scepticism."))
    M(tok, cid, title="AI Attack Scenario", type="scenario", order=2, xp_reward=45,
      content=scenario("A video call shows your CEO requesting an urgent funds transfer. The video quality is slightly off.",
                       ("Proceed — I can see them on video","Deepfakes can produce convincing video.",False),
                       ("Hang up, call the CEO on a known number, and verify using your pre-agreed code word",
                        "Correct. Establish out-of-band verification for high-value requests.",True),
                       ("Ask them to wave at the camera","Deepfake models can handle simple movements.",False)))

    cid = C(tok, name="Red Team Social Engineering TTPs", category="social_engineering", difficulty="hard",
            description="Common TTP patterns from real red team engagements.", xp_reward=100,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="MITRE ATT&CK: Social Engineering", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>MITRE ATT&CK T1566 (Phishing), T1534 (Internal Spearphishing), T1598 (Phishing for Information). Red teamers chain: OSINT → pretext → phishing → initial access → privilege escalation.</p>"))
    M(tok, cid, title="TTP Classification", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Match each action to its MITRE ATT&CK phase",
                       ["Reconnaissance","Initial Access","Privilege Escalation"],
                       [("Scrape LinkedIn for org chart","Reconnaissance"),
                        ("Send spear phishing email","Initial Access"),
                        ("Call helpdesk pretending to be an exec to reset password","Privilege Escalation"),
                        ("Research tech stack from job postings","Reconnaissance"),
                        ("Deliver malicious macro document","Initial Access")]))

    cid = C(tok, name="Building a Human Firewall", category="social_engineering", difficulty="hard",
            description="Organisation-wide culture change to resist social engineering.", xp_reward=100,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Security Culture Principles", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Technical controls fail when people are manipulated. Human firewall = security awareness training + clear reporting culture + psychological safety to say no + regular simulations + leadership modelling.</p>"))
    M(tok, cid, title="Culture Assessment", type="quiz", order=2, xp_reward=60,
      content=quiz(q("An employee reports they clicked a phishing link. The best organisational response is:",
                     "Disciplinary action","Public shaming to deter others",
                     "Thank them for reporting, remediate, and use it as a training example","Terminate immediately","c",
                     "Blame culture suppresses reporting. Psychological safety is essential for early threat detection.")))

    cid = C(tok, name="Supply Chain Social Engineering", category="social_engineering", difficulty="hard",
            description="Targeting third-party vendors to reach the primary target.", xp_reward=100,
            thumbnail_color="#8b5cf6", is_published=True)
    M(tok, cid, title="Third-Party Attack Vectors", type="lesson", order=1, xp_reward=40,
      content=warn("<p>If your direct defences are strong, attackers target your less-secure suppliers, partners, or MSPs. They gain access to the supply chain and pivot to your environment through trusted connections.</p>",
                   "Audit your third-party vendors' security posture — your security is only as strong as your weakest supplier."))
    M(tok, cid, title="Supply Chain Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("Your IT managed service provider (MSP) calls to say they need to install an urgent security patch via remote access.",
                       ("Grant access immediately — patches are important","Verify the patch exists via the vendor's official site.",False),
                       ("Call the MSP back on their official number to verify the request before granting access",
                        "Correct. Attackers frequently impersonate MSPs for privileged remote access.",True),
                       ("Ask them to email the patch instead","Remote access requests need identity verification, not just email.",False)))

    # ── MALWARE (10) ──────────────────────────────────────────────────────────
    print("\n── MALWARE ──")

    cid = C(tok, name="Malware 101", category="malware", difficulty="easy",
            description="Types of malware and how they spread.", xp_reward=50,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Malware Types Explained", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(MAL,"Malware types explained")+"<p>Virus: attaches to files. Worm: self-propagates. Trojan: disguised as legitimate software. Ransomware: encrypts your files. Spyware: silently monitors. Rootkit: hides at OS level.</p>"))
    M(tok, cid, title="Match the Malware", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Match each behaviour to the malware type",
                       ["Ransomware","Trojan","Worm","Spyware"],
                       [("Encrypts files and demands payment","Ransomware"),
                        ("Disguised as a game download, steals passwords","Trojan"),
                        ("Spreads to every device on the network automatically","Worm"),
                        ("Silently records keystrokes and screenshots","Spyware")]))

    cid = C(tok, name="Safe Browsing Habits", category="malware", difficulty="easy",
            description="Avoid drive-by downloads and malicious websites.", xp_reward=50,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Drive-By Downloads", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Drive-by downloads install malware just by visiting a page — no click required. They exploit unpatched browser plugins (Flash, Java) or JavaScript vulnerabilities. Keep browsers and plugins updated.</p>",
                   "Enable automatic browser updates. Remove unused plugins entirely."))
    M(tok, cid, title="Safe Browsing Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("A pop-up says 'Your computer is infected! Download our cleaner now.' What should you do?",
                     "Download the cleaner immediately","Close the tab and run your real antivirus",
                     "Click the X to dismiss","Call the number shown on screen","b",
                     "Fake AV pop-ups are malware delivery mechanisms. Never download software from pop-ups.")))

    cid = C(tok, name="Ransomware Readiness", category="malware", difficulty="easy",
            description="Prevent, detect, and recover from ransomware attacks.", xp_reward=60,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="How Ransomware Works", type="lesson", order=1, xp_reward=25,
      content=warn(yt(MAL,"Ransomware prevention")+"<p>Ransomware encrypts your data and demands payment. Modern variants also exfiltrate data first (double extortion). The best defence: immutable offline backups, email filtering, and endpoint protection.</p>",
                   "The 3-2-1 backup rule: 3 copies, 2 media types, 1 offsite/offline."))
    M(tok, cid, title="Ransomware Response", type="scenario", order=2, xp_reward=35,
      content=scenario("You see a ransom note on your screen. Files appear encrypted.",
                       ("Pay the ransom to get files back","Payment doesn't guarantee decryption and funds more attacks.",False),
                       ("Immediately disconnect from the network and call IT",
                        "Correct. Isolate to stop spread, then follow your incident response plan.",True),
                       ("Restart the computer to clear it","Restarting may trigger additional encryption.",False)))

    cid = C(tok, name="Fileless Malware", category="malware", difficulty="medium",
            description="Attacks that live in memory and leave no files on disk.", xp_reward=75,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Living Off the Land", type="lesson", order=1, xp_reward=30,
      content=warn("<p>Fileless malware runs entirely in memory using legitimate tools (PowerShell, WMI, mshta). No files = traditional signature-based AV misses it. Detect via behaviour analysis and memory scanning.</p>",
                   "Restrict PowerShell execution policy and enable script block logging for detection."))
    M(tok, cid, title="Fileless Indicators", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Which log source is most useful for detecting fileless malware?",
                     "File system changes","PowerShell script block logs and process creation events",
                     "Network firewall logs","Antivirus scan results","b",
                     "Fileless attacks leave minimal disk artifacts — process and script logs are the primary detection source.")))

    cid = C(tok, name="Macro Malware in Office Files", category="malware", difficulty="medium",
            description="VBA macros as a malware delivery mechanism.", xp_reward=75,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Office Macro Attacks", type="lesson", order=1, xp_reward=30,
      content=warn("<p>Malicious Office documents prompt you to 'Enable Content' to view them. That macro then downloads and executes malware. Microsoft now blocks macros from internet-downloaded files by default.</p>",
                   "Never enable macros in documents received via email unless you explicitly requested the file."))
    M(tok, cid, title="Macro Scenario", type="scenario", order=2, xp_reward=45,
      content=scenario("An emailed Word document shows 'Enable Content to view this document' with a blurred preview.",
                       ("Enable it — the blurring is suspicious","Enabling executes the payload.",False),
                       ("Do not enable. Delete the email and report to IT",
                        "Correct. Legitimate documents don't require macros to display content.",True),
                       ("Save and scan with antivirus before opening","Some macros execute on scan.",False)))

    cid = C(tok, name="Spyware & Stalkerware", category="malware", difficulty="medium",
            description="Covert surveillance software on personal and corporate devices.", xp_reward=75,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="How Spyware Operates", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Spyware silently captures keystrokes, screenshots, clipboard, microphone, and location. Commercial stalkerware markets itself as parental controls but is used for domestic abuse. Corporate keyloggers require employee disclosure.</p>"))
    M(tok, cid, title="Spyware Detection Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Which indicator most suggests a device has spyware installed?",
                     "Slow internet connection","Unusual battery drain, elevated CPU when idle, unexpected data usage",
                     "Pop-up advertisements","Slow startup time","b",
                     "Background data exfiltration causes elevated resource usage and unusual network traffic.")))

    cid = C(tok, name="APT Malware Techniques", category="malware", difficulty="hard",
            description="Advanced persistent threat malware used in nation-state attacks.", xp_reward=100,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="APT Characteristics", type="lesson", order=1, xp_reward=40,
      content=warn(yt(MAL,"APT advanced persistent threats")+"<p>APTs prioritise stealth and persistence: custom malware, living-off-the-land, encrypted C2 over legitimate channels (HTTPS, DNS), rootkits, and lateral movement using stolen credentials.</p>",
                   "APTs may persist undetected for months. Assume breach and hunt for indicators."))
    M(tok, cid, title="APT Indicators", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Classify each as APT indicator or normal behaviour",
                       ["APT Indicator","Normal"],
                       [("PowerShell making DNS lookups to unusual domains","APT Indicator"),
                        ("Scheduled task running at 3am uploading data","APT Indicator"),
                        ("Antivirus updating at 2am","Normal"),
                        ("Admin account accessing HR systems outside business hours","APT Indicator"),
                        ("Nightly backup job running","Normal")]))

    cid = C(tok, name="Malware Analysis Basics", category="malware", difficulty="hard",
            description="Static and dynamic analysis techniques for suspicious files.", xp_reward=100,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Static vs Dynamic Analysis", type="lesson", order=1, xp_reward=40,
      content=lesson("<p><strong>Static</strong>: analyse without running (strings, hashes, PE headers, imports). Tools: Pestudio, FLOSS. <strong>Dynamic</strong>: run in isolated sandbox and observe behaviour. Tools: Any.run, Cuckoo. Start static to avoid triggering anti-sandbox checks.</p>"))
    M(tok, cid, title="Analysis Approach Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("A suspicious executable detects it's running in a VM and does nothing. What technique is it using?",
                     "Polymorphism","Anti-sandbox / VM evasion",
                     "Rootkit persistence","DLL injection","b",
                     "Many malware samples check for VM artifacts and stay dormant to defeat automated sandbox analysis.")))

    cid = C(tok, name="Ransomware Incident Response", category="malware", difficulty="hard",
            description="Enterprise-level ransomware response and recovery.", xp_reward=100,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Ransomware IR Playbook", type="lesson", order=1, xp_reward=40,
      content=warn("<p>1. Isolate affected systems. 2. Identify patient zero. 3. Determine ransomware family. 4. Check for decryptors (NoMoreRansom.org). 5. Restore from clean backups. 6. Rebuild and harden. Never pay without exhausting alternatives.</p>",
                   "Before restoration, confirm backups are clean — ransomware often infects backups before triggering."))
    M(tok, cid, title="IR Decision Tree", type="scenario", order=2, xp_reward=60,
      content=scenario("Ransomware hit 30% of your file servers. Backups exist but are 48 hours old.",
                       ("Pay the ransom for faster recovery","Payment funds future attacks and data may still leak.",False),
                       ("Isolate, identify scope, restore from 48h backup, accept data loss",
                        "Correct. Clean restoration is preferable to paying attackers.",True),
                       ("Do nothing and hope it resolves itself","Ransomware will continue spreading.",False)))

    cid = C(tok, name="Supply Chain Malware", category="malware", difficulty="hard",
            description="SolarWinds-style attacks through trusted software updates.", xp_reward=100,
            thumbnail_color="#ef4444", is_published=True)
    M(tok, cid, title="Software Supply Chain Attacks", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Attackers compromise build pipelines or update servers to distribute malware through legitimate software (SolarWinds SUNBURST, 3CX, XZ Utils). Victims install it themselves, trusting the vendor.</p>"))
    M(tok, cid, title="Supply Chain Defence", type="quiz", order=2, xp_reward=60,
      content=quiz(q("Which control best detects supply chain malware in a software update?",
                     "Antivirus scan of the installer","Code signing verification + hash comparison with vendor-published checksums",
                     "Running the installer in a VM first","Checking the file size","b",
                     "Code signing and checksum verification confirm integrity from the vendor's build process.")))

    # ── NETWORK SECURITY (20) ─────────────────────────────────────────────────
    print("\n── NETWORK SECURITY ──")

    cid = C(tok, name="Home Network Security", category="network_security", difficulty="easy",
            description="Secure your home router and Wi-Fi in 10 minutes.", xp_reward=50,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Router Security Basics", type="lesson", order=1, xp_reward=20,
      content=warn(yt(NET,"Home network security")+"<p>Change default admin credentials. Use WPA3 or WPA2. Disable WPS. Update firmware. Segment IoT devices on a guest network.</p>",
                   "Default router credentials are published online — attackers scan for them."))
    M(tok, cid, title="Router Config Checklist", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Essential or optional for home router security?",
                       ["Essential","Optional"],
                       [("Change default admin password","Essential"),("Enable WPA3","Essential"),
                        ("Disable WPS","Essential"),("Custom SSID name","Optional"),
                        ("Guest network for IoT","Essential"),("MAC address filtering","Optional")]))

    cid = C(tok, name="Public Wi-Fi Risks", category="network_security", difficulty="easy",
            description="Staying safe on café and airport networks.", xp_reward=50,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Public Wi-Fi Threats", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Risks: man-in-the-middle interception, evil twin APs mimicking legitimate hotspots, passive eavesdropping on unencrypted traffic. Mitigation: use a VPN, verify HTTPS, avoid sensitive transactions.</p>",
                   "'Free Airport Wi-Fi' could be an attacker's hotspot. Always confirm the official network name with staff."))
    M(tok, cid, title="Public Wi-Fi Scenario", type="scenario", order=2, xp_reward=30,
      content=scenario("You need to check work email at a coffee shop. Two networks appear: 'CoffeeShop_Free' and 'CoffeeShop_Guest'.",
                       ("Connect to the open one — it's faster","Could be an evil twin.",False),
                       ("Ask staff for the official network name, then use VPN once connected",
                        "Correct. Verify network identity and encrypt your traffic.",True),
                       ("Use mobile data instead","Good alternative if VPN isn't available.",False)))

    cid = C(tok, name="VPN Basics", category="network_security", difficulty="easy",
            description="What a VPN does, what it doesn't, and how to use one.", xp_reward=50,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="VPN Explained", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(VPN,"VPN explained")+"<p>A VPN encrypts your connection and routes traffic through a trusted server. It protects against eavesdropping on local networks. It does NOT make you anonymous or protect against malware.</p>"))
    M(tok, cid, title="VPN Myths Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("A VPN protects you from:",
                     "All malware","Phishing emails","Eavesdropping on public Wi-Fi","Website tracking cookies","c",
                     "VPNs encrypt traffic in transit. They don't block malware, phishing, or cookies.")))

    cid = C(tok, name="Firewall Fundamentals", category="network_security", difficulty="easy",
            description="How firewalls control network traffic.", xp_reward=60,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Firewall Types", type="lesson", order=1, xp_reward=25,
      content=lesson(yt(FWL,"Firewall types explained")+"<p>Packet filter: checks IP/port. Stateful: tracks connections. Application layer (NGFW): inspects payload content. Host-based: on the device. Network-based: at perimeter.</p>"))
    M(tok, cid, title="Firewall Rule Quiz", type="quiz", order=2, xp_reward=35,
      content=quiz(q("A next-generation firewall can block based on:",
                     "IP address and port only","Application type, user identity, and content",
                     "MAC address only","Time of day only","b",
                     "NGFWs add application awareness, user identity, and deep packet inspection to traditional port/IP rules.")))

    cid = C(tok, name="DNS Security", category="network_security", difficulty="easy",
            description="DNS attacks and how protective DNS services work.", xp_reward=60,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="DNS: The Internet's Phone Book", type="lesson", order=1, xp_reward=25,
      content=warn("<p>DNS translates domains to IPs. DNS attacks: cache poisoning (redirect to fake IPs), DNS hijacking, DNS tunnelling (data exfiltration via DNS queries). Protective DNS (Cisco Umbrella, Cloudflare Gateway) blocks malicious domains.</p>",
                   "Use DNSSEC and encrypted DNS (DoH/DoT) to prevent tampering and eavesdropping."))
    M(tok, cid, title="DNS Threat Quiz", type="quiz", order=2, xp_reward=35,
      content=quiz(q("An attacker corrupts a DNS resolver's cache so bank.com resolves to a malicious IP. This is:",
                     "DNS tunnelling","DNS cache poisoning","DNS amplification","DDoS","b",
                     "DNS cache poisoning injects false records, redirecting users to attacker-controlled servers.")))

    cid = C(tok, name="Network Segmentation", category="network_security", difficulty="medium",
            description="Contain breaches with VLANs and micro-segmentation.", xp_reward=75,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Why Segment Your Network?", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Flat networks let malware spread freely. Segmentation limits blast radius: separate VLANs for corporate, IoT, guests, servers, payment systems. East-west firewall rules restrict lateral movement.</p>"))
    M(tok, cid, title="Segmentation Scenario", type="scenario", order=2, xp_reward=45,
      content=scenario("Ransomware infects a laptop on your flat network. All file servers are encrypted within 20 minutes.",
                       ("This is unavoidable — ransomware is too fast","Segmentation would have contained it.",False),
                       ("With proper segmentation, the laptop VLAN can't reach file servers — blast radius contained",
                        "Correct. East-west controls prevent lateral movement.",True),
                       ("Better antivirus would have stopped it","Detection failures happen — segmentation limits damage.",False)))

    cid = C(tok, name="Wireless Security", category="network_security", difficulty="medium",
            description="Enterprise Wi-Fi security, 802.1X, and rogue AP detection.", xp_reward=75,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Enterprise Wi-Fi Security", type="lesson", order=1, xp_reward=30,
      content=warn("<p>WPA2-Enterprise uses 802.1X with individual credentials — a breach of one device doesn't expose the PSK. WPA2-PSK is a shared secret — if one person's device is compromised, change the password everywhere.</p>",
                   "Regularly scan for rogue APs with tools like Wireless IDS or Kismet."))
    M(tok, cid, title="Wi-Fi Security Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Why is WPA2-Enterprise preferred over WPA2-PSK for corporate networks?",
                     "It's faster","Individual credentials mean one compromised device doesn't expose all others",
                     "It doesn't require a password","It works without a router","b",
                     "Per-user credentials isolate compromise. PSK compromise requires changing credentials for all devices.")))

    cid = C(tok, name="Intrusion Detection Systems", category="network_security", difficulty="medium",
            description="IDS vs IPS — monitoring and blocking network threats.", xp_reward=75,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="IDS and IPS Explained", type="lesson", order=1, xp_reward=30,
      content=lesson(yt(NET,"IDS IPS network security")+"<p>IDS (Intrusion Detection System): monitors and alerts. IPS (Intrusion Prevention System): monitors and blocks. Signature-based: known attacks. Anomaly-based: deviations from baseline. NGFWs often include IPS capability.</p>"))
    M(tok, cid, title="IDS vs IPS Classification", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("IDS or IPS action?",
                       ["IDS","IPS"],
                       [("Sends alert when SQL injection detected","IDS"),
                        ("Automatically drops malicious packets","IPS"),
                        ("Logs suspicious port scan","IDS"),
                        ("Resets connection on exploit attempt","IPS"),
                        ("Generates SIEM event for unusual traffic","IDS")]))

    cid = C(tok, name="Zero Trust Networking", category="network_security", difficulty="medium",
            description="Replace implicit trust with verify-always access controls.", xp_reward=80,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Zero Trust Architecture", type="lesson", order=1, xp_reward=35,
      content=lesson(yt(ZTR,"Zero trust network architecture")+"<p>Zero Trust replaces the castle-and-moat model. Core principles: verify explicitly, least-privilege access, assume breach. Implemented via identity-aware proxies, microsegmentation, and continuous monitoring.</p>"))
    M(tok, cid, title="Zero Trust Components", type="quiz", order=2, xp_reward=45,
      content=quiz(q("In a Zero Trust model, an employee who authenticated this morning should:",
                     "Have access to everything until logout","Be continuously re-evaluated based on behaviour and context",
                     "Get a 24-hour token","Only be re-verified weekly","b",
                     "Zero Trust applies continuous evaluation — authentication is not a one-time gate.")))

    cid = C(tok, name="Network Traffic Analysis", category="network_security", difficulty="medium",
            description="Read packet captures to detect threats with Wireshark.", xp_reward=80,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Packet Capture Fundamentals", type="lesson", order=1, xp_reward=35,
      content=lesson("<p>Wireshark captures raw network traffic. Key protocols: DNS (port 53), HTTP (80), HTTPS (443), SMB (445). Look for: unusual ports, data leaving to unknown IPs, unencrypted credentials, port scans (sequential connection attempts).</p>"))
    M(tok, cid, title="Traffic Analysis Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("In a packet capture you see repeated DNS queries to random-looking subdomains of the same domain. This likely indicates:",
                     "Normal CDN traffic","DNS tunnelling or C2 beacon communication",
                     "Broken DNS resolver","DDoS attack","b",
                     "High-entropy random subdomains are a classic DNS tunnelling pattern for C2 or data exfiltration.")))

    cid = C(tok, name="Cloud Network Security", category="network_security", difficulty="medium",
            description="Security groups, NACLs, and private endpoints in cloud environments.", xp_reward=80,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Cloud Networking Controls", type="lesson", order=1, xp_reward=35,
      content=warn(yt(CLD,"Cloud network security AWS")+"<p>Security groups: stateful, per-resource. NACLs: stateless, per-subnet. Principle: default deny, least-privilege rules. Never expose databases or management ports to 0.0.0.0/0.</p>",
                   "Misconfigured security groups are the #1 cause of cloud breaches. Audit rules regularly."))
    M(tok, cid, title="Cloud Security Group Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("A security group rule allows SSH (port 22) inbound from 0.0.0.0/0. What is the risk?",
                     "No risk — SSH is encrypted","Any internet host can attempt SSH brute force attacks",
                     "Only users with the key can connect so it's fine","The server will run slowly","b",
                     "Exposing SSH to the internet enables brute force and exploit attempts from any attacker globally.")))

    cid = C(tok, name="TLS/SSL Security", category="network_security", difficulty="medium",
            description="Certificate management, TLS versions, and MITM attacks.", xp_reward=80,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="TLS Fundamentals", type="lesson", order=1, xp_reward=35,
      content=warn("<p>TLS encrypts data in transit. TLS 1.0/1.1 are deprecated — use TLS 1.2+ (TLS 1.3 preferred). Certificate validation prevents MITM. HSTS forces HTTPS. Certificate pinning prevents substitute cert attacks.</p>",
                   "Use tools like SSL Labs to test your TLS configuration. Aim for A+ grade."))
    M(tok, cid, title="TLS Scenario", type="scenario", order=2, xp_reward=45,
      content=scenario("Your monitoring shows corporate laptops are connecting to an internal 'proxy' that presents its own SSL certificate for all HTTPS sites.",
                       ("This is fine — IT manages the proxy","Unless authorised, this is a MITM device.",False),
                       ("Investigate — this may be a MITM device or rogue proxy intercepting encrypted traffic",
                        "Correct. Unexpected certificate substitution warrants investigation.",True),
                       ("Disable SSL inspection on all devices","Don't disable security controls without investigation.",False)))

    cid = C(tok, name="DDoS Attacks and Mitigation", category="network_security", difficulty="hard",
            description="Types of DDoS attacks and enterprise mitigation strategies.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="DDoS Attack Types", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Volumetric: flood bandwidth (UDP flood, amplification). Protocol: exhaust state tables (SYN flood). Application layer: target server resources (HTTP flood, Slowloris). Mitigations: CDN scrubbing centres, rate limiting, BGP blackholing, anycast.</p>"))
    M(tok, cid, title="DDoS Mitigation Match", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Match the mitigation to the DDoS type",
                       ["Volumetric","Protocol","Application Layer"],
                       [("Upstream scrubbing centre","Volumetric"),("SYN cookies","Protocol"),
                        ("Rate limiting per IP","Application Layer"),("BGP blackhole routing","Volumetric"),
                        ("Web Application Firewall","Application Layer"),("Firewall SYN flood protection","Protocol")]))

    cid = C(tok, name="Network Penetration Testing", category="network_security", difficulty="hard",
            description="Methodology for authorised network penetration tests.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Network Pentest Phases", type="lesson", order=1, xp_reward=40,
      content=warn("<p>1. Reconnaissance (Shodan, DNS enum). 2. Scanning (Nmap, Nessus). 3. Exploitation (Metasploit, manual). 4. Post-exploitation (lateral movement, persistence). 5. Reporting with CVSS scores and remediation steps.</p>",
                   "Always have written authorisation (Rules of Engagement) before any penetration testing."))
    M(tok, cid, title="Pentest Phase Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("Running 'nmap -sV -p- 192.168.1.0/24' without written authorisation is:",
                     "A standard IT task","Legal if you own the network","Potentially illegal unauthorised access","Only illegal if you find vulnerabilities","c",
                     "Unauthorised scanning is illegal in most jurisdictions regardless of intent or network ownership claim.")))

    cid = C(tok, name="SIEM and Log Management", category="network_security", difficulty="hard",
            description="Security Information and Event Management for threat detection.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="SIEM Architecture", type="lesson", order=1, xp_reward=40,
      content=lesson(yt(INC,"SIEM security operations")+"<p>SIEM aggregates logs from firewalls, endpoints, identity, cloud, and applications. Correlation rules detect patterns across sources. Key use cases: brute force detection, lateral movement, data exfiltration, impossible travel.</p>"))
    M(tok, cid, title="SIEM Use Case Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("A SIEM correlation rule fires when the same user authenticates from London and New York within 2 hours. This is called:",
                     "Password spraying","Credential stuffing","Impossible travel detection","Brute force detection","c",
                     "Impossible travel detects physically impossible login patterns indicating account compromise.")))

    cid = C(tok, name="SD-WAN Security", category="network_security", difficulty="hard",
            description="Software-defined WAN security controls for distributed organisations.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="SD-WAN Security Architecture", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>SD-WAN connects branch offices over internet links. Security considerations: encrypted overlays, integrated NGFW, cloud security broker integration (SASE), centralised policy management, microsegmentation between branches.</p>"))
    M(tok, cid, title="SD-WAN Controls Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("In an SD-WAN deployment, what prevents a compromised branch from attacking HQ directly?",
                     "Encryption alone","Microsegmentation policies with east-west inspection between branches",
                     "Higher bandwidth links","Physical distance","b",
                     "Microsegmentation applies security policy to east-west branch traffic, not just north-south internet traffic.")))

    cid = C(tok, name="BGP Security & Hijacking", category="network_security", difficulty="hard",
            description="How BGP hijacks work and RPKI as a defence.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="BGP Route Hijacking", type="lesson", order=1, xp_reward=40,
      content=warn("<p>BGP is the internet's routing protocol. BGP hijacking: an AS announces ownership of IP prefixes it doesn't own, redirecting traffic. RPKI (Resource Public Key Infrastructure) cryptographically validates route origins.</p>",
                   "Major cloud providers and ISPs now support RPKI — push your upstream to enable route origin validation."))
    M(tok, cid, title="BGP Hijack Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("Traffic to your company's IP range starts routing through an unknown AS in a foreign country.",
                       ("Monitor and wait — it may self-correct","BGP hijacks require immediate action.",False),
                       ("Contact your upstream ISP and relevant RIR immediately, and consider BGP RPKI validation",
                        "Correct. BGP hijacks require ISP coordination and ROA verification.",True),
                       ("Change all IP addresses","Impractical and doesn't address the route hijack.",False)))

    cid = C(tok, name="Network Forensics", category="network_security", difficulty="hard",
            description="Capture and analyse network evidence for incident response.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="Network Forensics Methodology", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Capture evidence with Wireshark/tcpdump (preserve chain of custody). Analyse: NetFlow for traffic patterns, full packet capture for payload inspection, DNS logs for C2 identification, proxy logs for web activity reconstruction.</p>"))
    M(tok, cid, title="Forensics Tool Match", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Match the tool to its forensics use case",
                       ["Traffic Capture","Flow Analysis","Log Analysis"],
                       [("Wireshark","Traffic Capture"),("tcpdump","Traffic Capture"),
                        ("ntopng","Flow Analysis"),("Zeek/Bro","Flow Analysis"),
                        ("Splunk","Log Analysis"),("Elastic SIEM","Log Analysis")]))

    cid = C(tok, name="IoT Network Security", category="network_security", difficulty="hard",
            description="Securing connected devices that can't run traditional security agents.", xp_reward=100,
            thumbnail_color="#10b981", is_published=True)
    M(tok, cid, title="IoT Attack Surface", type="lesson", order=1, xp_reward=40,
      content=warn(yt(IOT,"IoT security risks")+"<p>IoT devices: default credentials, unpatched firmware, no encryption, limited compute for security agents. Mitigations: network segmentation, NAC for device fingerprinting, firmware update management, traffic baselining to detect anomalies.</p>",
                   "A compromised IP camera can be a persistent foothold for lateral movement — never put IoT on your corporate VLAN."))
    M(tok, cid, title="IoT Security Controls", type="quiz", order=2, xp_reward=60,
      content=quiz(q("What is the most effective first step for securing newly deployed IoT devices?",
                     "Install antivirus on each device","Change default credentials and segment on isolated VLAN",
                     "Enable Bluetooth on all devices","Connect them directly to the internet for cloud management","b",
                     "Default credentials are the #1 IoT vulnerability. Segmentation contains compromise if they're exploited.")))

    # ── GENERAL (30) ──────────────────────────────────────────────────────────
    print("\n── GENERAL ──")

    cid = C(tok, name="Security Awareness Fundamentals", category="general", difficulty="easy",
            description="The five habits every employee needs for baseline security.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Your Security Responsibilities", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(GDP,"Security awareness")+"<p>Five habits: 1. Lock your screen when away. 2. Use unique passwords + MFA. 3. Report suspicious emails. 4. Keep software updated. 5. Encrypt sensitive data.</p>"))
    M(tok, cid, title="Habit Drill", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Essential habit or nice-to-have?",
                       ["Essential","Nice to Have"],
                       [("Lock screen when away","Essential"),("Unique passwords + MFA","Essential"),
                        ("Customising your desktop wallpaper","Nice to Have"),
                        ("Report suspicious emails","Essential"),("Keep software updated","Essential")]))

    cid = C(tok, name="Clean Desk Policy", category="general", difficulty="easy",
            description="Physical security for sensitive information at your workstation.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Why Physical Security Matters", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Visitors, contractors, and shoulder-surfers can photograph or photograph sensitive documents left on desks. Clean desk = lock papers away, lock screen, shred sensitive printouts, secure USB drives.</p>",
                   "One photograph of a credentials list can compromise your entire organisation."))
    M(tok, cid, title="Clean Desk Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("You're stepping away from your desk for a meeting. What should you do?",
                     "Leave everything — you'll be back in an hour","Lock your screen and put sensitive documents away",
                     "Ask a colleague to watch your desk","Log out completely only at end of day","b",
                     "Unattended unlocked screens and visible documents are physical security risks.")))

    cid = C(tok, name="GDPR & Data Privacy Basics", category="general", difficulty="easy",
            description="What every employee needs to know about handling personal data.", xp_reward=60,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="GDPR for Everyone", type="lesson", order=1, xp_reward=25,
      content=warn(yt(GDP,"GDPR explained simply")+"<p>GDPR: personal data must be collected lawfully, used only for stated purposes, kept no longer than necessary, secured, and not transferred without consent. Breaches must be reported within 72 hours.</p>",
                   "Personal data includes names, emails, IPs, location data — not just credit card numbers."))
    M(tok, cid, title="GDPR Scenario", type="scenario", order=2, xp_reward=35,
      content=scenario("A colleague asks you to email a customer database to their personal Gmail for backup.",
                       ("Do it — backing up data is good practice","Personal Gmail is outside authorised processing.",False),
                       ("Decline. Data must stay within authorised systems. Report the request.",
                        "Correct. Unauthorised data transfers violate GDPR and company policy.",True),
                       ("Ask IT to approve it first","Correct escalation, but also flag the GDPR concern.",False)))

    cid = C(tok, name="Incident Reporting", category="general", difficulty="easy",
            description="When and how to report a security incident.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Report First, Investigate Later", type="lesson", order=1, xp_reward=20,
      content=lesson("<p>Report immediately if you: clicked a suspicious link, received a phishing email, lost a device, saw unexpected account activity, or found a vulnerability. Speed is critical — early reporting limits damage.</p>"))
    M(tok, cid, title="What to Report", type="dragdrop", order=2, xp_reward=30,
      content=dragdrop("Reportable security incident or not?",
                       ["Report Immediately","Not Required"],
                       [("Clicked a phishing link","Report Immediately"),
                        ("Lost a company laptop","Report Immediately"),
                        ("Received an annoying spam email","Not Required"),
                        ("Found a USB drive in the car park","Report Immediately"),
                        ("Saw an unfamiliar login notification","Report Immediately")]))

    cid = C(tok, name="Acceptable Use Policy", category="general", difficulty="easy",
            description="What you can and cannot do with company IT resources.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="AUP Essentials", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Company devices are for business use. Prohibited: installing unauthorised software, using company email for personal services, sharing credentials, accessing inappropriate content, connecting to unknown USB devices.</p>",
                   "Your company can monitor activity on company devices. Don't use them for personal sensitive activities."))
    M(tok, cid, title="AUP Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("You find a USB drive in the car park labelled 'Salaries 2024'. What should you do?",
                     "Plug it in to identify the owner","Hand it to IT security without plugging it in",
                     "Put it in lost property","Throw it away","b",
                     "Unknown USB drives may contain autorun malware (Rubber Ducky attacks). Never plug in found drives.")))

    cid = C(tok, name="Remote Work Security", category="general", difficulty="easy",
            description="Staying secure when working from home or on the road.", xp_reward=60,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Remote Security Checklist", type="lesson", order=1, xp_reward=25,
      content=lesson("<p>Use company VPN. Lock screen in shared spaces. Use headphones for sensitive calls. Don't print sensitive documents on personal printers. Secure your home router. Keep personal and work devices separate.</p>"))
    M(tok, cid, title="Remote Work Scenario", type="scenario", order=2, xp_reward=35,
      content=scenario("You're working from a café and need to take a call about a client contract.",
                       ("Take the call at your table — it's a public place","Others can overhear client details.",False),
                       ("Move to a quiet private space or use headphones and speak quietly",
                        "Correct. Prevent shoulder-surfing and eavesdropping on sensitive calls.",True),
                       ("Wait until you're back in the office","If urgent, find a private space.",False)))

    cid = C(tok, name="Bring Your Own Device (BYOD)", category="general", difficulty="easy",
            description="Security considerations when using personal devices for work.", xp_reward=60,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="BYOD Risks and Controls", type="lesson", order=1, xp_reward=25,
      content=warn("<p>BYOD risks: personal device can be stolen/lost, personal apps may access work data, device may have malware. Controls: MDM (Mobile Device Management), containerisation, conditional access, device encryption requirement.</p>",
                   "Enrolling your device in MDM lets IT remotely wipe work data (but not personal data in a properly configured containerised solution)."))
    M(tok, cid, title="BYOD Quiz", type="quiz", order=2, xp_reward=35,
      content=quiz(q("What does MDM containerisation protect in a BYOD scenario?",
                     "The entire device","Only corporate data, leaving personal data separate and private",
                     "Nothing — MDM has full device access","Only email","b",
                     "Containerisation isolates corporate data so remote wipe affects only the work container, not personal data.")))

    cid = C(tok, name="Social Media & Oversharing", category="general", difficulty="easy",
            description="How social media posts can compromise personal and corporate security.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="What Not to Share Online", type="lesson", order=1, xp_reward=20,
      content=warn("<p>Avoid sharing: office photos showing screens or whiteboards, holiday dates (burglary risk), photos of ID or boarding passes, org chart details, tech stack in casual posts. Attackers scrape social media for OSINT.</p>",
                   "Your photo with a visitor badge visible reveals your building's badge format. Details matter."))
    M(tok, cid, title="Oversharing Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("A colleague posts a LinkedIn photo of their new office setup. The screen behind them shows an internal dashboard. What risk does this create?",
                     "No risk — the screen is blurry","Internal system names, data, and layout are visible to attackers",
                     "Only HR should care","Risk only exists if they tagged the company","b",
                     "Internal systems visible in photos provide valuable reconnaissance to attackers.")))

    cid = C(tok, name="Encryption Basics", category="general", difficulty="easy",
            description="What encryption is, how it works, and when to use it.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Encryption Explained", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(NET,"Encryption explained")+"<p>Encryption converts readable data into ciphertext. Symmetric (AES): same key encrypts/decrypts. Asymmetric (RSA): public key encrypts, private key decrypts. At-rest: protects stored data. In-transit: protects data over networks.</p>"))
    M(tok, cid, title="Encryption Scenario", type="scenario", order=2, xp_reward=30,
      content=scenario("You need to email a colleague a confidential salary spreadsheet.",
                       ("Attach it unencrypted — internal email is secure","Email is not end-to-end encrypted by default.",False),
                       ("Encrypt the file with a password and share the password via a different channel",
                        "Correct. Encrypt sensitive attachments and share passwords out-of-band.",True),
                       ("Put it on SharePoint — email is insecure","SharePoint with proper permissions is better; but encryption is still best practice for salary data.",False)))

    cid = C(tok, name="Two-Factor Authentication Setup", category="general", difficulty="easy",
            description="Enable and configure 2FA on your most important accounts.", xp_reward=50,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Setting Up 2FA", type="lesson", order=1, xp_reward=20,
      content=lesson(yt(MFA,"Setup 2FA tutorial")+"<p>Enable 2FA on: work accounts, email, banking, social media. Use an authenticator app (Google Authenticator, Authy, Microsoft Authenticator) over SMS when available. Save backup codes in your password manager.</p>"))
    M(tok, cid, title="2FA Priority Quiz", type="quiz", order=2, xp_reward=30,
      content=quiz(q("Which account should have 2FA enabled first?",
                     "Gaming account","Work email — it's the master key to most other accounts",
                     "Newsletter subscription","Streaming service","b",
                     "Work email can reset most other accounts. It's the highest-value target.")))

    cid = C(tok, name="Secure File Sharing", category="general", difficulty="medium",
            description="Share files safely without exposing sensitive data.", xp_reward=75,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Safe File Sharing Practices", type="lesson", order=1, xp_reward=30,
      content=warn("<p>Don't use personal cloud storage for work files. Use company-approved platforms. Set expiry dates on shared links. Never share 'Anyone with the link' for sensitive documents. Revoke access when no longer needed.</p>",
                   "Old shared links are a common data exposure source. Audit your shared links quarterly."))
    M(tok, cid, title="Sharing Permissions Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("You share a contract via SharePoint with 'Anyone with the link can view'. What is the risk?",
                     "No risk — view-only is safe","The link could be forwarded to anyone, including external parties",
                     "Viewing uses too much bandwidth","Only risk if they download it","b",
                     "'Anyone with the link' grants access to anyone who receives it through any channel, including phishing.")))

    cid = C(tok, name="Mobile Device Security", category="general", difficulty="medium",
            description="Secure your smartphone against physical and network threats.", xp_reward=75,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Smartphone Security Essentials", type="lesson", order=1, xp_reward=30,
      content=lesson(yt(MOB,"Mobile security tips")+"<p>Enable: screen lock (biometric + PIN), full disk encryption, remote wipe. Update OS promptly. Only install apps from official stores. Review app permissions — a torch app doesn't need contacts access.</p>"))
    M(tok, cid, title="App Permission Red Flags", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Reasonable permission or red flag?",
                       ["Reasonable","Red Flag"],
                       [("Navigation app needs location","Reasonable"),
                        ("Torch app needs contacts access","Red Flag"),
                        ("Camera app needs camera access","Reasonable"),
                        ("Calculator app needs microphone access","Red Flag"),
                        ("Banking app needs biometrics","Reasonable"),
                        ("Game app needs call logs","Red Flag")]))

    cid = C(tok, name="Patch Management Importance", category="general", difficulty="medium",
            description="Why keeping software updated is your most impactful security control.", xp_reward=75,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="The Patching Imperative", type="lesson", order=1, xp_reward=30,
      content=warn("<p>80%+ of successful attacks exploit known vulnerabilities with available patches. WannaCry exploited EternalBlue — a patch was available 2 months before the attack. Enable auto-updates and treat critical patches as urgent.</p>",
                   "Never delay a critical security patch. 'We'll patch it next maintenance window' loses the race."))
    M(tok, cid, title="Patch Priority Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("A critical CVSS 9.8 RCE vulnerability is disclosed for your web server software. When should you patch?",
                     "Next scheduled quarterly maintenance","Within the next few days — ASAP",
                     "Within 30 days","Only if actively exploited","b",
                     "CVSS 9.8 critical RCE means remote attackers can run arbitrary code. Patch within 24-72 hours.")))

    cid = C(tok, name="Secure Code Awareness", category="general", difficulty="medium",
            description="Non-developer security awareness for code-adjacent roles.", xp_reward=75,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Security Risks in Code", type="lesson", order=1, xp_reward=30,
      content=warn(yt(WEB,"Secure coding OWASP")+"<p>Common risks: hardcoded secrets in code (check git history), SQL injection (user input in queries), XSS (unescaped output), insecure dependencies (check npm audit/pip audit), missing authentication.</p>",
                   "Never commit API keys, passwords, or tokens to git — even in private repos. They're accessible to anyone with access."))
    M(tok, cid, title="Code Risk Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("A developer hardcodes an API key in Python source code pushed to a public GitHub repo. What is the immediate risk?",
                     "Nothing — it's just a key","Automated bots scan GitHub for secrets within seconds of push",
                     "Risk only if the key has admin access","Risk only if someone manually finds it","b",
                     "Tools like truffleHog and GitHub's secret scanning find exposed credentials almost instantly.")))

    cid = C(tok, name="Third-Party Risk Management", category="general", difficulty="medium",
            description="Assess and manage the security risk of your vendors and suppliers.", xp_reward=80,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Vendor Risk Assessment", type="lesson", order=1, xp_reward=35,
      content=lesson("<p>Before onboarding a vendor: request SOC 2 Type II report, check their breach history, review their data processing agreements (DPA), assess their access to your systems/data, define contractual security requirements.</p>"))
    M(tok, cid, title="Vendor Risk Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Your new SaaS vendor won't provide a SOC 2 report. The most appropriate response is:",
                     "Proceed — SaaS providers don't need audits","Request their alternative assurance documentation or escalate to a risk acceptance decision",
                     "Ask them to complete SOC 2 by next year and proceed now","Cancel immediately","b",
                     "No SOC 2 doesn't automatically disqualify — but it requires alternative assurance or formal risk acceptance.")))

    cid = C(tok, name="Security in the Software Development Lifecycle", category="general", difficulty="medium",
            description="Shift-left: embed security from design to deployment.", xp_reward=80,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="DevSecOps Principles", type="lesson", order=1, xp_reward=35,
      content=lesson("<p>Shift-left means catching security issues early (cheaper to fix). SDLC gates: threat modelling in design, SAST in dev, dependency scanning in CI, DAST against staging, pen test before launch, runtime monitoring post-launch.</p>"))
    M(tok, cid, title="SDLC Security Phase Match", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Match the security activity to its SDLC phase",
                       ["Design","Development","Deployment","Production"],
                       [("Threat modelling","Design"),("Static code analysis (SAST)","Development"),
                        ("Dependency vulnerability scan","Development"),("Dynamic testing (DAST)","Deployment"),
                        ("Runtime anomaly monitoring","Production"),("Penetration test","Deployment")]))

    cid = C(tok, name="Cloud Security Shared Responsibility", category="general", difficulty="medium",
            description="Who is responsible for what in AWS, Azure, and GCP.", xp_reward=80,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="The Shared Responsibility Model", type="lesson", order=1, xp_reward=35,
      content=warn(yt(CLD,"Cloud shared responsibility model")+"<p>Cloud provider secures: physical infrastructure, hypervisor, managed service software. Customer secures: data, IAM, OS patching (IaaS), application code, network configuration. Misconfiguration is the customer's responsibility.</p>",
                   "The #1 cloud breach cause is customer misconfiguration, not cloud provider failure."))
    M(tok, cid, title="Shared Responsibility Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("A developer accidentally makes an S3 bucket publicly accessible. Who is responsible for this breach?",
                     "AWS — they provided the service","The customer — misconfiguration is in the customer's security domain",
                     "Both equally","Neither — it was an accident","b",
                     "AWS secures the infrastructure. Customers are responsible for correct configuration of cloud resources.")))

    cid = C(tok, name="Data Classification", category="general", difficulty="medium",
            description="Label, handle, and protect data according to its sensitivity.", xp_reward=75,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Data Classification Tiers", type="lesson", order=1, xp_reward=30,
      content=lesson("<p>Typical classification: <strong>Public</strong> — freely shareable. <strong>Internal</strong> — employees only. <strong>Confidential</strong> — need-to-know, encrypted at rest. <strong>Restricted</strong> — highest sensitivity (health, legal, financial), strict access controls, mandatory encryption.</p>"))
    M(tok, cid, title="Classify the Data", type="dragdrop", order=2, xp_reward=45,
      content=dragdrop("Classify each data type",
                       ["Public","Internal","Confidential","Restricted"],
                       [("Company press release","Public"),("Internal IT policy","Internal"),
                        ("Employee salary data","Restricted"),("Customer contract","Confidential"),
                        ("Marketing brochure","Public"),("Patient medical records","Restricted")]))

    cid = C(tok, name="Business Continuity Planning", category="general", difficulty="medium",
            description="Prepare your organisation to operate through security incidents.", xp_reward=80,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="BCP and DR Fundamentals", type="lesson", order=1, xp_reward=35,
      content=warn("<p>BCP: keep the business running during an incident. DR: restore IT systems after. Key metrics: RTO (Recovery Time Objective) — how fast must you recover? RPO (Recovery Point Objective) — how much data can you lose?</p>",
                   "An untested plan is not a plan. Run tabletop exercises at least annually."))
    M(tok, cid, title="BCP Quiz", type="quiz", order=2, xp_reward=45,
      content=quiz(q("Your RPO is 4 hours. This means:",
                     "You must recover within 4 hours","You can afford to lose up to 4 hours of data",
                     "Backups run every 4 hours","Incidents are resolved in 4 hours","b",
                     "RPO is the maximum acceptable data loss window — backups must be frequent enough to meet it.")))

    cid = C(tok, name="Privacy by Design", category="general", difficulty="hard",
            description="Embed privacy into system design from the start.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Privacy by Design Principles", type="lesson", order=1, xp_reward=40,
      content=lesson(yt(GDP,"Privacy by design principles")+"<p>Ann Cavoukian's 7 principles: proactive not reactive, privacy as default, privacy embedded in design, full functionality (positive-sum), end-to-end security, visibility/transparency, respect for user privacy.</p>"))
    M(tok, cid, title="Privacy Design Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("Your team is building an analytics feature and wants to collect detailed user behaviour logs including names and emails for correlation.",
                       ("Collect everything — more data is more useful","Collecting more than needed violates data minimisation.",False),
                       ("Pseudonymise the data at collection — hash or tokenise identifiers",
                        "Correct. Privacy by design means collecting the minimum needed in the least identifying form.",True),
                       ("Collect it all but encrypt at rest","Encryption doesn't address unnecessary collection.",False)))

    cid = C(tok, name="Security Metrics & KPIs", category="general", difficulty="hard",
            description="Measure security programme effectiveness with meaningful metrics.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Measuring Security Outcomes", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Vanity metrics: number of scans run, emails filtered. Outcome metrics: mean time to detect (MTTD), mean time to respond (MTTR), patch compliance rate, phishing simulation click rate trend, critical vuln SLA adherence.</p>",
                   "If a metric doesn't drive a decision, it's not worth tracking."))
    M(tok, cid, title="Metrics Classification", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Outcome metric or vanity metric?",
                       ["Outcome","Vanity"],
                       [("Mean time to detect incidents","Outcome"),("Number of firewall rules created","Vanity"),
                        ("Critical patch compliance within SLA","Outcome"),("Antivirus scans run per month","Vanity"),
                        ("Phishing click rate reduction YoY","Outcome"),("Security emails sent to staff","Vanity")]))

    cid = C(tok, name="Threat Intelligence Fundamentals", category="general", difficulty="hard",
            description="Using threat intelligence feeds to prioritise defences.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Threat Intelligence Types", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Strategic: executive-level trends and threat landscape. Operational: upcoming attack campaigns. Tactical: IOCs (IPs, hashes, domains). Technical: TTPs and malware analysis. STIX/TAXII for sharing. Actionable TI drives detections, not reports.</p>"))
    M(tok, cid, title="TI Application Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("You receive a threat intelligence feed with malicious IP addresses. The most immediate action is:",
                     "Write a board report","Block the IPs in your firewall/proxy and add to SIEM watchlist",
                     "Email all staff","Archive for future reference","b",
                     "Tactical TI (IOCs) should be operationalised into blocking rules and detection immediately.")))

    cid = C(tok, name="Vulnerability Management Programme", category="general", difficulty="hard",
            description="Build a continuous vulnerability identification and remediation programme.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Vulnerability Management Lifecycle", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>1. Asset inventory (you can't protect what you don't know). 2. Continuous scanning (Nessus, Qualys). 3. Risk-based prioritisation (CVSS + context). 4. Remediation SLAs (critical: 24h, high: 7d, medium: 30d). 5. Verification. 6. Reporting.</p>"))
    M(tok, cid, title="Vuln Management Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("Two vulnerabilities both have CVSS 7.5 (High). One is on an internet-facing payment server, one on an internal dev laptop. How should you prioritise?",
                     "Patch both at the same time","Prioritise the payment server — context elevates risk",
                     "Prioritise the laptop — it's easier to patch","Patch neither until monthly window","b",
                     "CVSS is a base score. Asset criticality and exposure context must adjust prioritisation.")))

    cid = C(tok, name="Security Architecture Review", category="general", difficulty="hard",
            description="Evaluate system designs for security risk before building.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Security Architecture Principles", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>Core principles: defence in depth (multiple layers), least privilege, fail secure, separation of duties, attack surface reduction, security by default. Threat model every new system: who are the adversaries, what are the assets, what are the attack paths?</p>"))
    M(tok, cid, title="Architecture Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("A new internal app will store PII. The developer suggests a single-tier design: web app directly connected to database, no WAF, accessible from internet.",
                       ("Approve it — it's internal","It stores PII and is internet-accessible — high risk.",False),
                       ("Require: WAF, separate app/db tiers, private DB subnet, MFA for admin access",
                        "Correct. Defence in depth for PII-holding systems is non-negotiable.",True),
                       ("Approve with note to add WAF later","Security controls shouldn't be deferred for PII systems.",False)))

    cid = C(tok, name="Red Team vs Blue Team", category="general", difficulty="hard",
            description="Understand adversarial testing and how it improves defences.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Red, Blue, and Purple Teams", type="lesson", order=1, xp_reward=40,
      content=lesson(yt(INC,"Red team blue team purple team")+"<p>Red team: offensive — test defences by simulating real attacks. Blue team: defensive — detect and respond. Purple team: collaborative — red shares TTPs with blue in real time to improve detection. Tabletop exercises simulate without live attack.</p>"))
    M(tok, cid, title="Team Role Classification", type="dragdrop", order=2, xp_reward=60,
      content=dragdrop("Red team or blue team activity?",
                       ["Red Team","Blue Team"],
                       [("Simulating a ransomware attack","Red Team"),
                        ("Writing SIEM detection rules","Blue Team"),
                        ("Social engineering employees","Red Team"),
                        ("Incident response and containment","Blue Team"),
                        ("Discovering unpatched systems via scanning","Red Team"),
                        ("Threat hunting for IOCs","Blue Team")]))

    cid = C(tok, name="Security Compliance Frameworks", category="general", difficulty="hard",
            description="ISO 27001, SOC 2, NIST CSF — what they are and why they matter.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Compliance Framework Overview", type="lesson", order=1, xp_reward=40,
      content=lesson("<p>ISO 27001: international ISMS standard, certification via audit. SOC 2: US-focused, Type I (design) vs Type II (operating effectiveness). NIST CSF: Identify, Protect, Detect, Respond, Recover. PCI DSS: payment card data. HIPAA: US healthcare.</p>"))
    M(tok, cid, title="Framework Match Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("A UK fintech handling payment card data needs to comply with which framework?",
                     "HIPAA only","PCI DSS (payment cards) and likely ISO 27001 for enterprise customers",
                     "SOC 2 only","GDPR only","b",
                     "PCI DSS is mandatory for card data. ISO 27001 is typically required by enterprise B2B customers.")))

    cid = C(tok, name="Cyber Insurance Basics", category="general", difficulty="hard",
            description="What cyber insurance covers and how to minimise premiums.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Cyber Insurance Essentials", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Cyber insurance covers: breach response costs, legal fees, regulatory fines, ransom payments, business interruption. Insurers now require: MFA on all remote access, EDR, patch management, backups tested. Failing controls = claim denied.</p>",
                   "Cyber insurers audit your controls. A ransomware claim on an unpatched system may be rejected."))
    M(tok, cid, title="Insurance Requirement Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("A company pays ransomware but their insurer denies the claim. The most likely reason is:",
                     "Ransomware isn't covered","They didn't have MFA on remote access — a required control",
                     "They reported it too slowly","Claims over $1M are always denied","b",
                     "Insurers now explicitly require MFA, EDR, and backups. Missing controls void coverage.")))

    cid = C(tok, name="AI & Security: Opportunities and Risks", category="general", difficulty="hard",
            description="How AI is changing both attack and defence in cybersecurity.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="AI in Cybersecurity", type="lesson", order=1, xp_reward=40,
      content=lesson("<p><strong>Defence:</strong> AI-powered anomaly detection, automated threat hunting, intelligent SOAR playbooks, faster vulnerability triage. <strong>Offence:</strong> AI-generated phishing, voice/video deepfakes, automated vulnerability discovery, LLM prompt injection attacks.</p>"))
    M(tok, cid, title="AI Security Scenario", type="scenario", order=2, xp_reward=60,
      content=scenario("Your security team wants to feed your SIEM logs to an AI assistant for analysis. What risk must be addressed first?",
                       ("No risk — AI is a security tool","AI tools may send logs to external servers.",False),
                       ("Ensure the AI tool is on-premise or the vendor has signed a DPA for log data",
                        "Correct. Security logs contain sensitive data — data residency and processing agreements are essential.",True),
                       ("Only use AI for low-sensitivity logs","All logs contain operationally sensitive patterns.",False)))

    cid = C(tok, name="Secure Disposal of Data and Devices", category="general", difficulty="hard",
            description="Properly destroy data on decommissioned equipment.", xp_reward=100,
            thumbnail_color="#6366f1", is_published=True)
    M(tok, cid, title="Data Destruction Methods", type="lesson", order=1, xp_reward=40,
      content=warn("<p>Deleting files ≠ erasing data. Methods by strength: Logical deletion (weakest) → Secure overwrite (DoD 5220.22-M) → Cryptographic erasure (destroy encryption key) → Degaussing → Physical destruction (shredding). Match method to data sensitivity.</p>",
                   "Sold or donated devices with inadequately wiped drives are a major data breach source."))
    M(tok, cid, title="Disposal Method Quiz", type="quiz", order=2, xp_reward=60,
      content=quiz(q("An SSD containing restricted financial data is being decommissioned. The most reliable disposal method is:",
                     "Format and reuse","Cryptographic erasure (destroy the encryption key) + physical shredding",
                     "Standard delete and empty recycle bin","Run disk cleanup utility","b",
                     "SSDs can't be reliably overwritten due to wear levelling. Cryptographic erasure + physical destruction is the gold standard.")))

print("\n✔ All 100 courses seeded successfully.")

if __name__ == "__main__":
    tok = login()
    seed(tok)
