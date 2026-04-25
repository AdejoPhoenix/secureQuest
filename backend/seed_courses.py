#!/usr/bin/env python3
"""Seed 10 information security training courses — not published."""
import sys
import requests

BASE = "http://localhost:8000/api/v1"


def login():
    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "admin@securequest.local", "password": "Admin1234!"})
    if not r.ok:
        print(f"Login failed: {r.status_code} {r.text}")
        sys.exit(1)
    print("Logged in.\n")
    return r.json()["access_token"]


def api(method, path, token, **kwargs):
    r = getattr(requests, method)(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        **kwargs,
    )
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    return r.json()


def course(token, **kw):
    c = api("post", "/admin/courses/", token, json=kw)
    print(f"  ✓ Course: {c['name']}  (id={c['id']})")
    return c["id"]


def module(token, cid, **kw):
    m = api("post", f"/admin/courses/{cid}/modules", token, json=kw)
    print(f"      • {m['type'].upper()}: {m['title']}")
    return m["id"]


def vid(video_id, title):
    """Returns a Bootstrap 16:9 YouTube embed iframe."""
    return (
        f'<div class="ratio ratio-16x9 mb-4 rounded overflow-hidden border border-secondary">'
        f'<iframe src="https://www.youtube.com/embed/{video_id}" title="{title}" '
        f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
        f'encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        f'</div>\n'
    )


# ──────────────────────────────────────────────────────────────────────────────
token = login()

# ══════════════════════════════════════════════════════════════════════════════
# 1 · PHISHING AWARENESS
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Phishing Awareness Fundamentals",
    description="Learn to identify and avoid phishing attacks — the #1 cause of data breaches worldwide.",
    category="phishing", difficulty="easy",
    thumbnail_color="#dc3545", xp_reward=150)

module(token, cid,
    title="What is Phishing?", type="lesson",
    order=0, xp_reward=20, is_required=True, pass_score=70,
    content={
        "body": vid("b3DNc4QE1Sg", "Phishing Attacks Explained") + """
<h3>What is Phishing?</h3>
<p>Phishing is a type of <strong>social engineering attack</strong> where cybercriminals impersonate trusted organisations to steal sensitive information — passwords, credit card numbers, or login credentials.</p>

<h3>How Phishing Works</h3>
<ul>
  <li>An attacker crafts an email that looks like it's from a legitimate source (your bank, Microsoft, Amazon)</li>
  <li>The email creates urgency: <em>"Your account will be suspended!"</em></li>
  <li>The victim clicks a malicious link leading to a convincing fake website</li>
  <li>Credentials or personal data are silently harvested</li>
</ul>

<h3>Types of Phishing</h3>
<ul>
  <li><strong>Email Phishing</strong> — Mass emails sent to thousands of recipients</li>
  <li><strong>Spear Phishing</strong> — Targeted attacks using personal information about the victim</li>
  <li><strong>Whaling</strong> — Attacks targeting executives or high-value individuals</li>
  <li><strong>Smishing</strong> — Phishing via SMS text messages</li>
  <li><strong>Vishing</strong> — Phishing via phone calls</li>
</ul>

<h3>Red Flags to Watch For</h3>
<ul>
  <li>Unexpected urgency or threats of account closure</li>
  <li>Mismatched or misspelled domains: <code>support@amaz0n.com</code></li>
  <li>Generic greetings like "Dear Customer" instead of your name</li>
  <li>Requests for sensitive information via email</li>
  <li>Suspicious attachments or unexpected links</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "91% of all cyberattacks begin with a phishing email. Recognising them is your first and most important line of defence."},
            {"type": "tip", "text": "Always hover over links before clicking — verify the destination URL matches the sender's claimed domain."}
        ]
    })

module(token, cid,
    title="Spot the Phish: Email Classifier", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "Drag each email subject line into the correct category — Phishing or Legitimate.",
        "categories": ["Phishing", "Legitimate"],
        "items": [
            {"text": "URGENT: Your account has been compromised — verify now", "category": "Phishing"},
            {"text": "Your Amazon order has shipped — track your package", "category": "Legitimate"},
            {"text": "You have won £500 — click to claim your prize!", "category": "Phishing"},
            {"text": "Meeting invite: Q3 planning session at 2pm Thursday", "category": "Legitimate"},
            {"text": "Immediate action required: unusual sign-in from Russia", "category": "Phishing"},
            {"text": "Your monthly bank statement is ready to view", "category": "Legitimate"},
            {"text": "Verify your PayPal account or it will be permanently closed", "category": "Phishing"},
            {"text": "Password reset link you requested for your account", "category": "Legitimate"},
        ]
    })

module(token, cid,
    title="Phishing Knowledge Check", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "What is the primary goal of a phishing attack?",
         "options": {"a": "To crash your computer", "b": "To steal sensitive information", "c": "To slow down your internet", "d": "To display advertisements"},
         "correct": "b", "explanation": "Phishing tricks victims into revealing passwords, credit card numbers, or personal data."},
        {"text": "Which email sender should raise suspicion?",
         "options": {"a": "support@microsoft.com", "b": "security@yourbank.co.uk", "c": "admin@micros0ft-support.net", "d": "noreply@amazon.com"},
         "correct": "c", "explanation": "'micros0ft-support.net' uses a zero instead of 'o' — classic domain spoofing."},
        {"text": "What type of phishing specifically targets senior executives?",
         "options": {"a": "Spear phishing", "b": "Whaling", "c": "Smishing", "d": "Vishing"},
         "correct": "b", "explanation": "Whaling targets high-value individuals like CEOs, as compromising their accounts yields far greater rewards."},
        {"text": "You receive a suspicious email asking for your password. You should:",
         "options": {"a": "Reply with your password if the email looks official", "b": "Click the link to verify it's legitimate", "c": "Delete it and report to your IT/security team", "d": "Forward it to colleagues to warn them"},
         "correct": "c", "explanation": "Never provide credentials via email. Report suspicious emails to your security team immediately."},
    ]})

module(token, cid,
    title="Scenario: The IT Helpdesk Email", type="scenario",
    order=3, xp_reward=35, is_required=True, pass_score=70,
    content={
        "description": "You receive this email:\n\nFrom: itsupport@company-it-helpdesk.support\nSubject: URGENT: Unauthorised access detected\n\n\"We've detected unauthorised access to your account. Verify your credentials within 2 hours or your account will be locked permanently.\n\nClick here: http://company-it-helpdesk-portal.support/verify\"\n\nYour real IT helpdesk is at helpdesk@yourcompany.com. What do you do?",
        "choices": [
            {"text": "Click the link immediately — I don't want my account locked", "outcome": "You clicked a phishing link and entered credentials on a fake page. The attacker now has your username and password — your account and potentially your organisation is compromised.", "is_correct": False},
            {"text": "Reply to the email asking for more information", "outcome": "Replying confirms your address is active and may trigger more targeted attacks. The sender is not the real IT team.", "is_correct": False},
            {"text": "Contact IT support directly using the known, verified helpdesk email or phone number", "outcome": "Excellent! You verified through an independent, trusted channel. IT confirms this was a phishing attempt. Your vigilance protected the organisation.", "is_correct": True},
            {"text": "Ignore it completely", "outcome": "Ignoring is better than clicking, but you should still report it. Your security team needs to know to warn others and investigate.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 2 · PASSWORD SECURITY
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Password Security Mastery",
    description="Master password hygiene, multi-factor authentication, and password managers to secure every account.",
    category="passwords", difficulty="easy",
    thumbnail_color="#198754", xp_reward=120)

module(token, cid,
    title="Password Security Fundamentals", type="lesson",
    order=0, xp_reward=20, is_required=True, pass_score=70,
    content={
        "body": vid("aEmgNkxUcVQ", "Password Security Best Practices") + """
<h3>Why Password Security Matters</h3>
<p>Weak or reused passwords are responsible for <strong>80% of hacking-related data breaches</strong>. A strong password policy is one of the simplest yet most effective security controls available.</p>

<h3>What Makes a Strong Password?</h3>
<ul>
  <li><strong>Length</strong> — At least 12–16 characters; longer is exponentially stronger</li>
  <li><strong>Complexity</strong> — Mix of uppercase, lowercase, numbers, and symbols</li>
  <li><strong>Uniqueness</strong> — Never reuse passwords across accounts</li>
  <li><strong>Unpredictability</strong> — Avoid dictionary words, names, dates, or patterns</li>
</ul>

<h3>Common Password Attacks</h3>
<ul>
  <li><strong>Brute Force</strong> — Trying every possible combination</li>
  <li><strong>Dictionary Attack</strong> — Testing common words and known passwords</li>
  <li><strong>Credential Stuffing</strong> — Using leaked username/password pairs from previous breaches</li>
  <li><strong>Shoulder Surfing</strong> — Watching you type your password in public</li>
</ul>

<h3>Password Managers</h3>
<p>A password manager generates, stores, and auto-fills strong unique passwords for every site. You only need to remember one master password. Reputable options: Bitwarden (free, open source), 1Password, Dashlane.</p>

<h3>Multi-Factor Authentication (MFA)</h3>
<p>MFA adds a second verification layer beyond your password:</p>
<ul>
  <li><strong>Something you know</strong> — password or PIN</li>
  <li><strong>Something you have</strong> — phone/authenticator app/hardware key</li>
  <li><strong>Something you are</strong> — fingerprint or face recognition</li>
</ul>""",
        "callouts": [
            {"type": "danger", "text": "'123456', 'password', and 'qwerty' top the list of most used passwords globally — they're the first ones attackers try."},
            {"type": "tip", "text": "Enable MFA on every account that supports it, especially email, banking, and social media — it blocks 99.9% of automated attacks."}
        ]
    })

module(token, cid,
    title="Strong vs Weak: Password Classifier", type="dragdrop",
    order=1, xp_reward=25, is_required=True, pass_score=70,
    content={
        "instruction": "Drag each password into the correct strength category.",
        "categories": ["Strong Password", "Weak Password"],
        "items": [
            {"text": "password123", "category": "Weak Password"},
            {"text": "Tr0ub4dor&3#mK!", "category": "Strong Password"},
            {"text": "qwerty", "category": "Weak Password"},
            {"text": "J7$nPx@2mQkL9!", "category": "Strong Password"},
            {"text": "john1990", "category": "Weak Password"},
            {"text": "correct-horse-battery-staple-77!", "category": "Strong Password"},
            {"text": "111111", "category": "Weak Password"},
            {"text": "V#8fGzR$2pLn@qW3", "category": "Strong Password"},
        ]
    })

module(token, cid,
    title="Password Best Practices Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "What is the minimum recommended password length?",
         "options": {"a": "6 characters", "b": "8 characters", "c": "12 characters", "d": "4 characters"},
         "correct": "c", "explanation": "NIST guidelines recommend at least 12 characters. Passphrases of 16+ are even better."},
        {"text": "What is credential stuffing?",
         "options": {"a": "Using the same password everywhere", "b": "Using leaked username/password pairs from other breaches", "c": "Stuffing random characters into a password", "d": "Using a password manager"},
         "correct": "b", "explanation": "Credential stuffing exploits password reuse by testing leaked credentials from previous breaches on other services."},
        {"text": "The best way to manage many unique strong passwords is to:",
         "options": {"a": "Write them in a notebook", "b": "Use the same strong password for everything", "c": "Use a reputable password manager", "d": "Use your name with numbers at the end"},
         "correct": "c", "explanation": "Password managers securely generate and store unique strong passwords, requiring you to remember only one master password."},
    ]})

module(token, cid,
    title="Scenario: Suspicious Login Alert", type="scenario",
    order=3, xp_reward=30, is_required=True, pass_score=70,
    content={
        "description": "You receive a genuine notification from your email provider:\n\n\"Sign-in detected from a new device in Lagos, Nigeria at 3:42 AM. If this wasn't you, secure your account immediately.\"\n\nYou did NOT sign in from Nigeria. Your current password is 'Sarah1990' — which you use on several other sites.",
        "choices": [
            {"text": "Change just my email password to 'Sarah1991'", "outcome": "Only incrementing the number is insufficient. Attackers try variations. You're also still using a weak personal pattern across other accounts.", "is_correct": False},
            {"text": "Change email password to a strong unique one, enable MFA, and update reused passwords on other sites", "outcome": "Perfect! Secured the breached account, added MFA, and addressed the credential stuffing risk by changing reused passwords elsewhere.", "is_correct": True},
            {"text": "Ignore it — it might be a phishing email", "outcome": "While phishing caution is good, an actual unauthorised login requires immediate action. Ignoring gives the attacker full access to your email.", "is_correct": False},
            {"text": "Reply to the notification email asking for details", "outcome": "Never reply to security notification emails. Log in directly via your browser and review security settings from within your account.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 3 · SOCIAL ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Social Engineering Defence",
    description="Understand how attackers manipulate human psychology to bypass technical controls — and learn to resist it.",
    category="social_engineering", difficulty="medium",
    thumbnail_color="#6f42c1", xp_reward=175)

module(token, cid,
    title="The Art of Social Engineering", type="lesson",
    order=0, xp_reward=25, is_required=True, pass_score=70,
    content={
        "body": vid("lc7scxvKQOo", "Social Engineering Attacks Explained") + """
<h3>What is Social Engineering?</h3>
<p>Social engineering is the art of <strong>manipulating people</strong> into performing actions or divulging confidential information. Unlike technical hacking, it targets the human element — our trust, fear, desire to help, and tendency to act under urgency.</p>

<h3>Core Psychological Triggers Used</h3>
<ul>
  <li><strong>Authority</strong> — Impersonating managers, IT staff, or government officials</li>
  <li><strong>Urgency</strong> — Creating time pressure to prevent careful thinking</li>
  <li><strong>Social Proof</strong> — "Everyone else has already done this"</li>
  <li><strong>Reciprocity</strong> — Doing a favour first to create a sense of obligation</li>
  <li><strong>Liking</strong> — Building rapport before making a request</li>
  <li><strong>Scarcity</strong> — "This is a limited-time opportunity"</li>
</ul>

<h3>Common Attack Techniques</h3>
<ul>
  <li><strong>Pretexting</strong> — Creating a fabricated scenario (fake IT support call)</li>
  <li><strong>Baiting</strong> — Leaving infected USB drives in accessible areas</li>
  <li><strong>Quid Pro Quo</strong> — Offering help in exchange for credentials</li>
  <li><strong>Tailgating/Piggybacking</strong> — Following authorised staff through secure doors</li>
  <li><strong>Impersonation</strong> — Pretending to be a vendor, auditor, or executive</li>
</ul>

<h3>How to Defend Against It</h3>
<ul>
  <li>Always verify identities through independent channels before acting</li>
  <li>Be suspicious of unexpected requests, even from apparent colleagues</li>
  <li>Follow the principle: <strong>"If in doubt, don't"</strong></li>
  <li>Never let urgency override security procedures</li>
  <li>Report all suspicious interactions to your security team</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "Kevin Mitnick, one of history's most famous hackers, said: 'The human element is the weakest link in security.'"},
            {"type": "info", "text": "Legitimate organisations will NEVER pressure you to bypass security procedures, no matter how urgent the situation appears."}
        ]
    })

module(token, cid,
    title="Attack Type Identifier", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "Match each attack description to the correct social engineering technique.",
        "categories": ["Pretexting", "Baiting", "Tailgating", "Impersonation"],
        "items": [
            {"text": "Caller claims to be from Microsoft support and says your PC has a virus", "category": "Pretexting"},
            {"text": "USB drive labelled 'Salary Information Q4' left in the office lobby", "category": "Baiting"},
            {"text": "Person in a delivery uniform follows staff through a secure door", "category": "Tailgating"},
            {"text": "Email appears to come from the CEO requesting an urgent wire transfer", "category": "Impersonation"},
            {"text": "Caller invents a story about needing server access for maintenance", "category": "Pretexting"},
            {"text": "Free promotional CD left in the car park installs malware when inserted", "category": "Baiting"},
            {"text": "Attacker holds the door open and enters without badging in", "category": "Tailgating"},
            {"text": "Caller pretends to be a new IT vendor needing network credentials", "category": "Impersonation"},
        ]
    })

module(token, cid,
    title="Social Engineering Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "An attacker leaves USB drives in a company car park hoping employees plug them in. This is called:",
         "options": {"a": "Pretexting", "b": "Baiting", "c": "Vishing", "d": "Tailgating"},
         "correct": "b", "explanation": "Baiting exploits curiosity by leaving physical media in accessible areas to get victims to introduce malware themselves."},
        {"text": "'Your account will be deleted in 24 hours!' — which psychological trigger does this exploit?",
         "options": {"a": "Authority", "b": "Reciprocity", "c": "Urgency", "d": "Social Proof"},
         "correct": "c", "explanation": "Urgency prevents careful thinking. Attackers create artificial deadlines to make victims act before they can properly evaluate the request."},
        {"text": "Someone calls claiming to be IT support and asks for your password to fix an issue. You should:",
         "options": {"a": "Give it — IT needs it to fix the problem", "b": "Ask them to email you instead", "c": "Refuse and verify their identity through official channels", "d": "Ask for their name then give the password"},
         "correct": "c", "explanation": "Legitimate IT staff will NEVER ask for your password. Verify unusual requests by calling the IT helpdesk directly on a known number."},
    ]})

module(token, cid,
    title="Scenario: The Friendly New Contractor", type="scenario",
    order=3, xp_reward=40, is_required=True, pass_score=70,
    content={
        "description": "A friendly person approaches your desk and introduces himself as James, a new IT contractor starting today. He says he's been asked to check all workstations for a critical security update but doesn't have his access badge yet. He asks if you could log him in with your credentials 'just for 10 minutes' while he sorts out his badge with HR. He seems genuine, knows some people's names, and says your manager approved it.",
        "choices": [
            {"text": "Log him in — he seems genuine and my manager approved it", "outcome": "You fell for a social engineering attack. A real contractor would have their own credentials from HR/IT before starting work. Sharing login credentials is a serious security violation.", "is_correct": False},
            {"text": "Offer to walk him to HR/IT yourself to get proper credentials sorted", "outcome": "Excellent! You're being helpful while maintaining security. If he's genuine, he'll appreciate it. If he's an attacker, this removes his opportunity entirely.", "is_correct": True},
            {"text": "Quickly message your manager via Slack to confirm before acting", "outcome": "Good instinct, but a quick message may not be reliable. A sophisticated attacker could have already compromised messaging. A voice call or in-person verification is stronger.", "is_correct": False},
            {"text": "Ask him to show you the approval email from your manager", "outcome": "Checking documentation is better than nothing, but emails can be spoofed. The safest action is to accompany him to HR/IT for proper credential issuance.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 4 · MALWARE & RANSOMWARE
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Malware & Ransomware Protection",
    description="Identify malicious software types, understand how they spread, and learn how to protect your systems.",
    category="malware", difficulty="medium",
    thumbnail_color="#fd7e14", xp_reward=160)

module(token, cid,
    title="Understanding Malware", type="lesson",
    order=0, xp_reward=20, is_required=True, pass_score=70,
    content={
        "body": vid("n8mbzU0X2nQ", "Types of Malware Explained") + """
<h3>What is Malware?</h3>
<p><strong>Malware</strong> (malicious software) is any software intentionally designed to cause disruption, steal data, or gain unauthorised access to systems. It's an umbrella term covering many types of malicious code.</p>

<h3>Types of Malware</h3>
<ul>
  <li><strong>Virus</strong> — Attaches to legitimate files; spreads when the file is executed</li>
  <li><strong>Worm</strong> — Self-replicates and spreads across networks without user action</li>
  <li><strong>Trojan</strong> — Disguises itself as legitimate software to gain entry</li>
  <li><strong>Ransomware</strong> — Encrypts files and demands payment for decryption keys</li>
  <li><strong>Spyware</strong> — Silently monitors activity and exfiltrates data</li>
  <li><strong>Adware</strong> — Displays unwanted advertisements, often bundled with free software</li>
  <li><strong>Rootkit</strong> — Hides deep in the OS, granting persistent unauthorised access</li>
  <li><strong>Keylogger</strong> — Records every keystroke to capture passwords and sensitive data</li>
</ul>

<h3>How Malware Spreads</h3>
<ul>
  <li>Phishing email attachments (.exe, .doc, .zip files)</li>
  <li>Malicious websites and drive-by downloads</li>
  <li>Infected USB drives left in accessible areas</li>
  <li>Unpatched software vulnerabilities</li>
  <li>Pirated software, games, or media</li>
</ul>

<h3>Ransomware: The Growing Crisis</h3>
<p>Ransomware attacks have cost organisations <strong>billions annually</strong>. The average ransom demand now exceeds $200,000. Key defences:</p>
<ul>
  <li>Regular offline backups using the <strong>3-2-1 rule</strong></li>
  <li>Keep all systems patched and up-to-date</li>
  <li>Never pay the ransom — it doesn't guarantee file recovery</li>
  <li>Report immediately to your security team and authorities</li>
</ul>""",
        "callouts": [
            {"type": "danger", "text": "Ransomware attacks increased by 150% in 2023. Healthcare, education, and local government are among the most targeted sectors."},
            {"type": "tip", "text": "3-2-1 backup rule: 3 copies of data, on 2 different media types, with 1 copy stored offline or offsite — immune to ransomware."}
        ]
    })

module(token, cid,
    title="Malware Type Classifier", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "Drag each description to the correct malware type.",
        "categories": ["Ransomware", "Trojan", "Worm", "Spyware"],
        "items": [
            {"text": "Encrypts all files and demands Bitcoin payment for decryption", "category": "Ransomware"},
            {"text": "Disguised as a free video game but steals your banking details", "category": "Trojan"},
            {"text": "Spreads automatically across the network without any user action", "category": "Worm"},
            {"text": "Silently records your keystrokes and sends them to an attacker", "category": "Spyware"},
            {"text": "Locks your screen showing a fake 'police' message demanding a fine", "category": "Ransomware"},
            {"text": "A fake antivirus tool that actually installs more malware", "category": "Trojan"},
            {"text": "Exploits a vulnerability to copy itself to thousands of connected devices", "category": "Worm"},
            {"text": "Tracks your browsing history and sends it to advertisers without consent", "category": "Spyware"},
        ]
    })

module(token, cid,
    title="Malware Identification Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "Which type of malware encrypts your files and demands payment?",
         "options": {"a": "Spyware", "b": "Adware", "c": "Ransomware", "d": "Worm"},
         "correct": "c", "explanation": "Ransomware encrypts victim files and demands payment (usually cryptocurrency) for decryption keys. Paying does not guarantee recovery."},
        {"text": "What is the 3-2-1 backup rule?",
         "options": {"a": "3 passwords, 2 accounts, 1 email", "b": "3 copies, 2 media types, 1 offsite", "c": "Back up 3 times a day", "d": "3 antivirus tools, 2 firewalls, 1 VPN"},
         "correct": "b", "explanation": "3-2-1: three copies of data, on two different media types, with one copy kept offsite or offline — surviving even if ransomware strikes."},
        {"text": "A Trojan horse differs from a virus because it:",
         "options": {"a": "Is more destructive", "b": "Only attacks Macs", "c": "Disguises itself as legitimate software", "d": "Spreads automatically via network"},
         "correct": "c", "explanation": "Trojans masquerade as legitimate software. Unlike viruses, they don't self-replicate — they rely on the user to install them willingly."},
    ]})

module(token, cid,
    title="Scenario: The Suspicious Attachment", type="scenario",
    order=3, xp_reward=35, is_required=True, pass_score=70,
    content={
        "description": "You receive an email from HR@yourcompany.com with subject: 'Q4 Salary Review — Action Required'. It asks you to open the attached file 'Salary_Review_2024.exe' to see your updated compensation package.\n\nYour company does use this email for HR communications. However, HR typically shares documents as PDFs, never as .exe files.",
        "choices": [
            {"text": "Open the attachment — it's from the official HR email", "outcome": "The email spoofed the HR address. The .exe was a Trojan installing ransomware. Your department's file server is now encrypted. Always be suspicious of unexpected executables.", "is_correct": False},
            {"text": "Do not open it. Contact HR directly via phone or internal chat to verify", "outcome": "Correct! You verified through an independent channel. HR confirms they never sent this — it was a spoofed address. Your caution prevented a ransomware attack.", "is_correct": True},
            {"text": "Forward it to a personal email to open safely at home", "outcome": "Opening malware on your home computer still infects that device and can compromise personal banking and credentials. Never forward suspected malware.", "is_correct": False},
            {"text": "Open it briefly and then close it quickly", "outcome": "Executables run the moment they are opened — there is no 'brief' window. Ransomware begins encrypting files immediately upon execution.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 5 · NETWORK SECURITY
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Network Security Essentials",
    description="Understand how networks are attacked and the controls that keep your data safe in transit.",
    category="network_security", difficulty="medium",
    thumbnail_color="#0dcaf0", xp_reward=165)

module(token, cid,
    title="Network Security Fundamentals", type="lesson",
    order=0, xp_reward=25, is_required=True, pass_score=70,
    content={
        "body": vid("ZxL4UPCm4WY", "Network Security Fundamentals") + """
<h3>What is Network Security?</h3>
<p>Network security encompasses the policies, practices, and technologies that <strong>prevent and monitor unauthorised access, misuse, or modification</strong> of a computer network and its resources.</p>

<h3>Common Network Attacks</h3>
<ul>
  <li><strong>Man-in-the-Middle (MitM)</strong> — Intercepting communications between two parties</li>
  <li><strong>Packet Sniffing</strong> — Capturing unencrypted network traffic</li>
  <li><strong>DNS Spoofing</strong> — Redirecting traffic to malicious websites</li>
  <li><strong>DDoS</strong> — Flooding a network to disrupt availability</li>
  <li><strong>Evil Twin</strong> — Creating a fake WiFi hotspot to intercept traffic</li>
</ul>

<h3>Key Security Controls</h3>
<ul>
  <li><strong>Firewall</strong> — Controls traffic based on security rules</li>
  <li><strong>VPN</strong> — Encrypts all traffic between your device and destination</li>
  <li><strong>HTTPS/TLS</strong> — Encrypts web traffic; always check for the padlock</li>
  <li><strong>Network Segmentation</strong> — Dividing networks to contain breaches</li>
  <li><strong>IDS/IPS</strong> — Intrusion Detection/Prevention monitors for threats</li>
  <li><strong>WPA3</strong> — Latest and strongest WiFi encryption standard</li>
</ul>

<h3>Public WiFi Risks</h3>
<ul>
  <li>Always use a VPN on public networks</li>
  <li>Never access banking or sensitive accounts without a VPN</li>
  <li>Verify the network name with staff before connecting</li>
  <li>Prefer mobile data over unknown public WiFi</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "43% of public WiFi networks have no security. Attackers set up 'Evil Twin' hotspots named 'Starbucks_Free_WiFi' to intercept all your traffic."},
            {"type": "tip", "text": "A VPN encrypts all your traffic, making any interception on public WiFi completely useless to the attacker."}
        ]
    })

module(token, cid,
    title="Safe vs Unsafe Network Behaviours", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "Classify each network behaviour as a Safe Practice or a Risky Practice.",
        "categories": ["Safe Practice", "Risky Practice"],
        "items": [
            {"text": "Using a VPN when working from a coffee shop", "category": "Safe Practice"},
            {"text": "Connecting to 'FREE_Airport_WiFi' without verification", "category": "Risky Practice"},
            {"text": "Accessing bank accounts only on your secured home network", "category": "Safe Practice"},
            {"text": "Using the same WiFi password since 2015 without changing it", "category": "Risky Practice"},
            {"text": "Checking for HTTPS padlock before entering card details", "category": "Safe Practice"},
            {"text": "Accepting an unknown device's Bluetooth pairing request", "category": "Risky Practice"},
            {"text": "Keeping your home router firmware updated", "category": "Safe Practice"},
            {"text": "Working with sensitive documents on unencrypted public WiFi", "category": "Risky Practice"},
        ]
    })

module(token, cid,
    title="Network Security Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "What does a VPN primarily protect you from?",
         "options": {"a": "Viruses and malware", "b": "Traffic interception on untrusted networks", "c": "Phishing emails", "d": "Weak passwords"},
         "correct": "b", "explanation": "A VPN encrypts your internet traffic, making it unreadable to anyone intercepting it on untrusted networks like public WiFi."},
        {"text": "What is an 'Evil Twin' attack?",
         "options": {"a": "When malware copies itself", "b": "A rogue WiFi point that mimics a legitimate one", "c": "A twin virus that doubles in size", "d": "An attack targeting two people simultaneously"},
         "correct": "b", "explanation": "An Evil Twin is a rogue WiFi access point mimicking a legitimate one to intercept traffic. Victims connect thinking it's the real network."},
        {"text": "HTTPS on a website indicates:",
         "options": {"a": "The site is trustworthy", "b": "It's government approved", "c": "Traffic between you and the site is encrypted", "d": "The site contains no malware"},
         "correct": "c", "explanation": "HTTPS means the connection is encrypted (TLS). It does NOT mean the site itself is trustworthy — phishing sites also use HTTPS."},
    ]})

module(token, cid,
    title="Scenario: The Café Deadline", type="scenario",
    order=3, xp_reward=35, is_required=True, pass_score=70,
    content={
        "description": "You're working remotely from a café and need to send a sensitive contract to a client urgently. The café WiFi is available. Your company laptop has a VPN installed but it takes 3 minutes to connect. The client is waiting and you're running late.",
        "choices": [
            {"text": "Send the contract immediately without the VPN — it'll be fine just this once", "outcome": "On an unencrypted public network, a MitM attacker could intercept the contract. The sensitive client data is now potentially compromised — 'just this once' is how most breaches happen.", "is_correct": False},
            {"text": "Use your mobile phone as a personal hotspot instead of the café WiFi", "outcome": "Excellent alternative! Your mobile data creates a private encrypted connection. This is a solid secure workaround when a VPN isn't immediately available.", "is_correct": True},
            {"text": "Connect to the VPN first, wait for it to connect, then send the contract", "outcome": "The best approach. Three minutes is absolutely worth it. With the VPN active, traffic is encrypted and any interception is useless. Never compromise security for speed.", "is_correct": True},
            {"text": "Connect to the staff WiFi instead — it sounds more secure", "outcome": "Using a network you're not authorised to access is both a security risk and potentially illegal. Use the VPN on the guest network or use mobile hotspot.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 6 · SAFE WEB BROWSING
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Safe Web Browsing & Online Safety",
    description="Navigate the web safely — understand browser security, URL inspection, and web-based threats.",
    category="general", difficulty="easy",
    thumbnail_color="#20c997", xp_reward=110)

module(token, cid,
    title="Staying Safe Online", type="lesson",
    order=0, xp_reward=20, is_required=True, pass_score=70,
    content={
        "body": vid("JV-PGJ2ArEY", "Safe Browsing Tips and Web Security") + """
<h3>Reading URLs Safely</h3>
<ul>
  <li>The <strong>real domain</strong> is the part just before the final <code>.com</code>/<code>.co.uk</code> etc.</li>
  <li><code>http://paypal.com.verify-account.net/login</code> — real domain is <code>verify-account.net</code></li>
  <li>Watch for typosquatting: <code>g00gle.com</code>, <code>paypa1.com</code>, <code>amazon-support.net</code></li>
  <li>Subdomains ≠ domain: <code>microsoft.com.attacker.net</code> belongs to <code>attacker.net</code></li>
</ul>

<h3>Browser Security Features</h3>
<ul>
  <li><strong>Safe Browsing</strong> — Chrome/Firefox/Edge warn about known malicious sites</li>
  <li><strong>Certificate errors</strong> — If your browser warns, leave the site immediately</li>
  <li><strong>Incognito mode</strong> — Does NOT protect from malware or network surveillance; only prevents local history</li>
  <li><strong>Extensions</strong> — Install only from trusted sources; malicious extensions can steal all your data</li>
</ul>

<h3>Common Web Threats</h3>
<ul>
  <li><strong>Drive-by downloads</strong> — Malware that downloads automatically just by visiting a page</li>
  <li><strong>Fake update popups</strong> — "Your browser is outdated!" — classic malware delivery</li>
  <li><strong>Cryptojacking</strong> — Websites using your CPU to mine cryptocurrency without consent</li>
  <li><strong>Malvertising</strong> — Malicious code embedded in legitimate-looking online advertisements</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "Never trust a padlock icon alone — it only means the connection is encrypted, not that the site is legitimate. Phishing sites use HTTPS too."},
            {"type": "tip", "text": "The uBlock Origin browser extension blocks malicious ads and trackers, significantly reducing exposure to malvertising and drive-by downloads."}
        ]
    })

module(token, cid,
    title="Safe vs Suspicious URLs", type="dragdrop",
    order=1, xp_reward=25, is_required=True, pass_score=70,
    content={
        "instruction": "Classify each URL as Safe or Suspicious.",
        "categories": ["Safe", "Suspicious"],
        "items": [
            {"text": "https://www.amazon.co.uk/orders", "category": "Safe"},
            {"text": "http://amazon.co.uk.verify-order.net/login", "category": "Suspicious"},
            {"text": "https://accounts.google.com/signin", "category": "Safe"},
            {"text": "https://g00gle-account-verify.com", "category": "Suspicious"},
            {"text": "https://www.gov.uk/tax-returns", "category": "Safe"},
            {"text": "http://gov-uk-tax-refund.info/claim", "category": "Suspicious"},
            {"text": "https://www.paypal.com/uk/home", "category": "Safe"},
            {"text": "https://paypal.com.account-suspended.net", "category": "Suspicious"},
        ]
    })

module(token, cid,
    title="Web Security Quiz", type="quiz",
    order=2, xp_reward=20, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "In 'http://paypal.com.verify.attacker.net', what is the REAL domain?",
         "options": {"a": "paypal.com", "b": "verify.attacker.net", "c": "attacker.net", "d": "paypal.com.verify"},
         "correct": "c", "explanation": "The real domain is the part just before the TLD (.net): attacker.net. 'paypal.com' here is merely a subdomain of attacker.net."},
        {"text": "What does incognito/private browsing actually protect you from?",
         "options": {"a": "Malware", "b": "Employer monitoring traffic", "c": "Local browsing history being saved", "d": "Hackers intercepting your traffic"},
         "correct": "c", "explanation": "Incognito only prevents your browser saving history, cookies, and form data locally. It provides no protection against network surveillance or malware."},
        {"text": "A popup says 'Your browser is outdated — update now'. You should:",
         "options": {"a": "Click it — updating is important", "b": "Update through the browser's official settings menu instead", "c": "Run a virus scan first", "d": "Allow it if the site has HTTPS"},
         "correct": "b", "explanation": "Fake update popups are a common malware vector. Always update browsers through their built-in update mechanism, never via a website popup."},
    ]})

# ══════════════════════════════════════════════════════════════════════════════
# 7 · DATA PRIVACY & GDPR
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Data Privacy & GDPR Compliance",
    description="Understand data protection principles, GDPR obligations, and how to handle personal data responsibly.",
    category="general", difficulty="medium",
    thumbnail_color="#0d6efd", xp_reward=155)

module(token, cid,
    title="Data Privacy Fundamentals", type="lesson",
    order=0, xp_reward=25, is_required=True, pass_score=70,
    content={
        "body": vid("4p4y1C2YL7Q", "GDPR and Data Privacy Explained") + """
<h3>What is Personal Data?</h3>
<p>Personal data is any information relating to an <strong>identified or identifiable natural person</strong>. This includes obvious identifiers like names and email addresses, but also IP addresses, cookie identifiers, and location data.</p>

<h3>GDPR Data Categories</h3>
<ul>
  <li><strong>Standard personal data</strong> — Name, address, email, phone number, IP address</li>
  <li><strong>Special category (sensitive)</strong> — Health data, biometrics, racial/ethnic origin, religious beliefs, sexual orientation, political opinions, trade union membership</li>
</ul>

<h3>The 6 GDPR Principles</h3>
<ul>
  <li><strong>Lawfulness, Fairness & Transparency</strong> — Process data lawfully; tell people how it's used</li>
  <li><strong>Purpose Limitation</strong> — Only collect for specified, explicit purposes</li>
  <li><strong>Data Minimisation</strong> — Collect only what is necessary</li>
  <li><strong>Accuracy</strong> — Keep data accurate and up-to-date</li>
  <li><strong>Storage Limitation</strong> — Don't retain data longer than necessary</li>
  <li><strong>Integrity & Confidentiality</strong> — Protect data from unauthorised access or loss</li>
</ul>

<h3>Data Breach Response</h3>
<p>If a breach involves personal data, GDPR requires notification to the supervisory authority (ICO in the UK) within <strong>72 hours</strong> of becoming aware of it.</p>""",
        "callouts": [
            {"type": "danger", "text": "GDPR fines can reach €20 million or 4% of global annual turnover. British Airways was fined £20m for a 2018 breach affecting 400,000 customers."},
            {"type": "info", "text": "Every employee who handles personal data is responsible under GDPR — not just IT or the Data Protection Officer."}
        ]
    })

module(token, cid,
    title="Personal Data Classification", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "Classify each piece of information under the correct GDPR data category.",
        "categories": ["Standard Personal Data", "Special Category Data", "Not Personal Data"],
        "items": [
            {"text": "A customer's full name and home address", "category": "Standard Personal Data"},
            {"text": "A patient's HIV diagnosis", "category": "Special Category Data"},
            {"text": "Total number of website visitors this month", "category": "Not Personal Data"},
            {"text": "An employee's trade union membership", "category": "Special Category Data"},
            {"text": "A user's email address and login timestamps", "category": "Standard Personal Data"},
            {"text": "Aggregated sales figures for a product category", "category": "Not Personal Data"},
            {"text": "A person's religious beliefs noted in HR records", "category": "Special Category Data"},
            {"text": "A customer's IP address and browsing cookies", "category": "Standard Personal Data"},
        ]
    })

module(token, cid,
    title="GDPR Compliance Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "Within how many hours must a personal data breach be reported under GDPR?",
         "options": {"a": "24 hours", "b": "48 hours", "c": "72 hours", "d": "7 days"},
         "correct": "c", "explanation": "GDPR Article 33 requires notification to the supervisory authority within 72 hours of becoming aware of a personal data breach."},
        {"text": "Which is classified as 'special category' data under GDPR?",
         "options": {"a": "Email address", "b": "Postal address", "c": "IP address", "d": "Biometric data"},
         "correct": "d", "explanation": "Biometric data processed to uniquely identify a person is special category data under GDPR Article 9, requiring heightened protection."},
        {"text": "The data minimisation principle means:",
         "options": {"a": "Store as little data as possible to save storage", "b": "Only collect data adequate, relevant, and limited to what is necessary", "c": "Delete all data after 30 days", "d": "Minimise the number of people with data access"},
         "correct": "b", "explanation": "Data minimisation means collecting only what's necessary for the specified purpose — not more, even if more might be useful."},
    ]})

module(token, cid,
    title="Scenario: The Accidental Disclosure", type="scenario",
    order=3, xp_reward=35, is_required=True, pass_score=70,
    content={
        "description": "While preparing a spreadsheet for an external marketing agency, you accidentally include a hidden tab containing 1,200 customers' full names, email addresses, and purchase history — data not part of the intended brief. You notice this only after the file has already been sent.",
        "choices": [
            {"text": "Say nothing and hope the agency deletes the data without looking", "outcome": "This is a GDPR breach. Hoping it goes unnoticed doesn't remove your legal obligation to report it. Covering it up makes the situation far worse and increases organisational liability.", "is_correct": False},
            {"text": "Immediately contact your manager and DPO, then ask the agency in writing to delete the file and confirm deletion", "outcome": "Correct response. You escalated immediately, limited the breach by requesting deletion in writing, and created an audit trail. The DPO can assess whether a 72-hour ICO report is required.", "is_correct": True},
            {"text": "Call the agency informally and ask them to ignore that tab", "outcome": "Informal verbal requests are insufficient. You need written confirmation of deletion, and the incident must be reported internally for proper GDPR breach assessment.", "is_correct": False},
            {"text": "Delete the original sent email to remove evidence", "outcome": "Deleting evidence is a serious offence. Regulators and courts take a significantly harsher view of cover-ups than of the original breach itself.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 8 · INCIDENT RESPONSE
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Incident Response Fundamentals",
    description="Learn the structured approach to detecting, containing, and recovering from cybersecurity incidents.",
    category="general", difficulty="hard",
    thumbnail_color="#dc3545", xp_reward=200)

module(token, cid,
    title="The Incident Response Lifecycle", type="lesson",
    order=0, xp_reward=30, is_required=True, pass_score=70,
    content={
        "body": vid("bzNADLfFo2Q", "Incident Response Process Explained") + """
<h3>What is Incident Response?</h3>
<p>Incident Response (IR) is a structured methodology for <strong>handling security breaches and cyberattacks</strong>. The goal is to limit damage, reduce recovery time and costs, and learn from events to prevent recurrence.</p>

<h3>The NIST IR Lifecycle</h3>
<ul>
  <li><strong>1. Preparation</strong> — Build IR capability: create plans, train teams, deploy tools, establish communication channels</li>
  <li><strong>2. Detection & Analysis</strong> — Identify incidents via monitoring, alerts, and user reports; confirm and assess scope</li>
  <li><strong>3. Containment</strong> — Isolate affected systems to prevent spread; implement temporary fixes</li>
  <li><strong>4. Eradication</strong> — Remove the root cause: delete malware, patch vulnerabilities, remove attacker access</li>
  <li><strong>5. Recovery</strong> — Restore systems to normal; monitor closely for signs of re-infection</li>
  <li><strong>6. Post-Incident Activity</strong> — Lessons-learned review; update IR plans; share indicators of compromise (IoCs)</li>
</ul>

<h3>What YOU Should Do as a First Responder</h3>
<ul>
  <li><strong>DO NOT</strong> turn off or reboot a compromised system — destroys forensic evidence</li>
  <li><strong>DO</strong> disconnect from the network (unplug LAN / disable WiFi)</li>
  <li><strong>DO</strong> immediately report to your manager and IT/security team</li>
  <li><strong>DO</strong> document everything you see and every action you take</li>
  <li><strong>DO NOT</strong> attempt to investigate or clean the infection yourself</li>
</ul>""",
        "callouts": [
            {"type": "danger", "text": "The average time to identify a breach is 207 days. Fast detection and response dramatically reduces the total cost and damage."},
            {"type": "warning", "text": "NEVER turn off a compromised computer before notifying security — RAM contents including encryption keys and running processes will be permanently lost."}
        ]
    })

module(token, cid,
    title="IR Lifecycle: Sort the Steps", type="dragdrop",
    order=1, xp_reward=35, is_required=True, pass_score=70,
    content={
        "instruction": "Sort each action into the correct phase of the NIST Incident Response lifecycle.",
        "categories": ["Detection", "Containment", "Eradication", "Recovery"],
        "items": [
            {"text": "SIEM alert fires: unusual data exfiltration detected at 2am", "category": "Detection"},
            {"text": "Disconnect the infected server from the network immediately", "category": "Containment"},
            {"text": "Remove the rootkit and patch the exploited vulnerability", "category": "Eradication"},
            {"text": "Restore systems from verified clean backups and monitor closely", "category": "Recovery"},
            {"text": "Security analyst confirms ransomware is actively spreading across shares", "category": "Detection"},
            {"text": "Isolate the affected network segment via firewall rule changes", "category": "Containment"},
            {"text": "Delete all attacker persistence mechanisms and backdoors", "category": "Eradication"},
            {"text": "Bring services back online and validate with business users", "category": "Recovery"},
        ]
    })

module(token, cid,
    title="Incident Response Quiz", type="quiz",
    order=2, xp_reward=30, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "Your computer has hundreds of encrypted files and a ransom note. Your FIRST action is:",
         "options": {"a": "Pay the ransom to recover files quickly", "b": "Shut the computer down immediately", "c": "Disconnect from the network and report to IT/security", "d": "Try to decrypt the files yourself"},
         "correct": "c", "explanation": "Disconnect from network to stop ransomware spreading to other systems, then report immediately. Don't shut down — this destroys forensic evidence."},
        {"text": "Which IR phase involves removing malware and patching vulnerabilities?",
         "options": {"a": "Containment", "b": "Recovery", "c": "Detection", "d": "Eradication"},
         "correct": "d", "explanation": "Eradication eliminates the root cause — removing malware, closing backdoors, and patching the exploited vulnerability to prevent recurrence."},
        {"text": "Why should you NOT turn off a compromised computer before the security team arrives?",
         "options": {"a": "It might cause hardware damage", "b": "Forensic evidence in RAM is lost on shutdown", "c": "It could spread the malware faster", "d": "The attacker might cover their tracks"},
         "correct": "b", "explanation": "RAM contents — running processes, encryption keys, network connections — are lost on shutdown. Forensic investigators need this data to understand and attribute the attack."},
    ]})

module(token, cid,
    title="Scenario: Active Ransomware Attack", type="scenario",
    order=3, xp_reward=50, is_required=True, pass_score=70,
    content={
        "description": "It's 9:15 AM Monday. You sit down at your desk and notice the computer is slow. A colleague shouts that her files are encrypted with a $50,000 ransom message. You look at your screen — the same message is appearing on yours too.\n\nYou still have network connectivity. The IT helpdesk number is on a card in your desk drawer.",
        "choices": [
            {"text": "Disconnect from the network immediately (unplug LAN / disable WiFi) then call IT", "outcome": "Excellent first response! Disconnecting stops ransomware spreading to network shares and other systems. Calling IT immediately activates the incident response process.", "is_correct": True},
            {"text": "Shut down your computer to stop the encryption", "outcome": "Shutdown destroys forensic evidence and may not stop encryption already in progress. Some ransomware corrupts files further on shutdown. Disconnect from network instead.", "is_correct": False},
            {"text": "Log into the backup system to restore your files", "outcome": "If your backup is on the same network, ransomware may encrypt those too. Your priority is containment — disconnect from the network, then call IT.", "is_correct": False},
            {"text": "Search for ransomware decryption tools while your colleague calls IT", "outcome": "Every second counts in containing ransomware. Your priority is to disconnect from the network immediately — not research.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 9 · CLOUD SECURITY
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Cloud Security Best Practices",
    description="Understand shared responsibility, cloud misconfigurations, and how to work securely in cloud environments.",
    category="network_security", difficulty="medium",
    thumbnail_color="#6610f2", xp_reward=170)

module(token, cid,
    title="Cloud Security Fundamentals", type="lesson",
    order=0, xp_reward=25, is_required=True, pass_score=70,
    content={
        "body": vid("M988_fsOSWo", "Cloud Security Best Practices") + """
<h3>The Shared Responsibility Model</h3>
<p>Security responsibilities are <strong>split between the cloud provider and the customer</strong>:</p>
<ul>
  <li><strong>Cloud Provider:</strong> Physical security, hardware, hypervisors, network backbone, the cloud platform itself</li>
  <li><strong>Customer:</strong> Data protection, user access (IAM), application security, OS configuration, network controls you configure</li>
</ul>

<h3>Most Common Cloud Security Failures</h3>
<ul>
  <li><strong>Misconfiguration</strong> — S3 buckets set to public, open security groups, unrestricted ports</li>
  <li><strong>Excessive IAM permissions</strong> — Granting admin access instead of least-privilege roles</li>
  <li><strong>Unencrypted storage</strong> — Sensitive data stored without encryption at rest</li>
  <li><strong>Exposed credentials</strong> — API keys hardcoded in code repositories</li>
  <li><strong>No monitoring</strong> — Cloud-native logging and alerting not enabled</li>
</ul>

<h3>Cloud Security Best Practices</h3>
<ul>
  <li>Apply the <strong>Principle of Least Privilege</strong> — grant minimum necessary permissions</li>
  <li>Enable <strong>MFA</strong> for all cloud console accounts</li>
  <li>Encrypt data at rest and in transit</li>
  <li>Enable <strong>audit logging</strong> (AWS CloudTrail, Azure Monitor, GCP Cloud Audit Logs)</li>
  <li>Never hardcode credentials — use secrets managers (AWS Secrets Manager, Azure Key Vault)</li>
  <li>Regularly audit permissions and resource configurations</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "Misconfiguration is the #1 cloud security risk. Gartner predicts that through 2025, 99% of cloud security failures will be the customer's fault."},
            {"type": "info", "text": "Over 33 billion records were exposed in 2023 due to misconfigured cloud storage buckets — most were accidentally set to public."}
        ]
    })

module(token, cid,
    title="Shared Responsibility Matrix", type="dragdrop",
    order=1, xp_reward=30, is_required=True, pass_score=70,
    content={
        "instruction": "In an IaaS model, who is responsible for securing each component?",
        "categories": ["Cloud Provider", "Customer"],
        "items": [
            {"text": "Physical data centre security and hardware", "category": "Cloud Provider"},
            {"text": "User account access management and IAM policies", "category": "Customer"},
            {"text": "Hypervisor and virtualisation infrastructure", "category": "Cloud Provider"},
            {"text": "Encrypting sensitive data stored in cloud storage buckets", "category": "Customer"},
            {"text": "Network hardware and global backbone infrastructure", "category": "Cloud Provider"},
            {"text": "Configuring firewall rules and security groups", "category": "Customer"},
            {"text": "Physical cables and routers inside the data centre facility", "category": "Cloud Provider"},
            {"text": "Patching the operating system on virtual machines", "category": "Customer"},
        ]
    })

module(token, cid,
    title="Cloud Security Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "What is the 'Principle of Least Privilege'?",
         "options": {"a": "Use the cheapest cloud tier", "b": "Grant users only the minimum permissions needed", "c": "Store the least data in the cloud", "d": "Use private cloud instead of public"},
         "correct": "b", "explanation": "Least Privilege means granting exactly the permissions needed — nothing more. This limits the blast radius if credentials are compromised."},
        {"text": "A developer commits an AWS access key to a public GitHub repo. What happens IMMEDIATELY?",
         "options": {"a": "Delete the commit and hope no one saw it", "b": "Revoke the exposed key immediately and review access logs", "c": "Change the account password", "d": "Make the repo private"},
         "correct": "b", "explanation": "Exposed credentials must be revoked immediately. Bots scan GitHub for exposed keys within minutes of publication. Deleting the commit doesn't help — it's already scanned."},
        {"text": "Which is the customer's responsibility in the shared responsibility model?",
         "options": {"a": "Physical data centre access controls", "b": "Hypervisor security patching", "c": "Data encryption and access management", "d": "Network backbone reliability"},
         "correct": "c", "explanation": "Customers are responsible for their own data security, identity management, application security, and network configurations they control."},
    ]})

module(token, cid,
    title="Scenario: The Public S3 Bucket", type="scenario",
    order=3, xp_reward=40, is_required=True, pass_score=70,
    content={
        "description": "A junior developer messages you: 'I set up an S3 bucket to share our client analytics reports with the marketing team — easiest to just make it public so everyone can access the links. The bucket contains monthly analytics with aggregated customer data and internal revenue figures. Should I send out the link?'",
        "choices": [
            {"text": "Yes — it's just analytics, not passwords or credit cards", "outcome": "Internal revenue figures and aggregated customer data are commercially sensitive and may include personal data under GDPR. Public S3 buckets have caused massive data breaches at major companies.", "is_correct": False},
            {"text": "Tell them to make the bucket private, use IAM roles for marketing team access, and use pre-signed URLs for specific sharing", "outcome": "Perfect! Private bucket + least-privilege IAM + pre-signed URLs is the correct, secure architecture. Controlled access with no public exposure.", "is_correct": True},
            {"text": "Add passwords to the files before sharing the link", "outcome": "Files inside S3 buckets don't natively support password protection. The bucket itself needs proper IAM access controls — file-level passwords are not a substitute.", "is_correct": False},
            {"text": "Rename the bucket to something less obvious before sharing", "outcome": "Security through obscurity is never a valid control. Automated scanners discover public buckets regardless of their name within hours of creation.", "is_correct": False},
        ]
    })

# ══════════════════════════════════════════════════════════════════════════════
# 10 · MOBILE DEVICE SECURITY
# ══════════════════════════════════════════════════════════════════════════════
cid = course(token,
    name="Mobile Device Security",
    description="Protect smartphones and tablets from mobile threats — cover app security, MDM policies, and safe mobile habits.",
    category="general", difficulty="easy",
    thumbnail_color="#ffc107", xp_reward=130)

module(token, cid,
    title="Securing Your Mobile Devices", type="lesson",
    order=0, xp_reward=20, is_required=True, pass_score=70,
    content={
        "body": vid("3GmCLlMkFno", "Mobile Device Security Best Practices") + """
<h3>Why Mobile Security Matters</h3>
<p>Smartphones now hold more sensitive information than ever — emails, banking apps, two-factor authentication codes, corporate data, and personal files. Yet most users apply far less security discipline to phones than to computers.</p>

<h3>Mobile Threat Landscape</h3>
<ul>
  <li><strong>Malicious Apps</strong> — Apps disguised as tools that steal credentials or data</li>
  <li><strong>Smishing</strong> — SMS phishing with malicious links</li>
  <li><strong>Unsecured WiFi</strong> — MitM attacks on public networks</li>
  <li><strong>Physical theft</strong> — Unlocked, unencrypted devices expose everything</li>
  <li><strong>Jailbreaking/Rooting</strong> — Removes OS security controls entirely</li>
  <li><strong>Spyware</strong> — Commercial spyware (e.g., Pegasus) silently monitors all activity</li>
</ul>

<h3>Mobile Security Best Practices</h3>
<ul>
  <li><strong>Device lock</strong> — Use a strong PIN (6+ digits), biometrics, or passphrase</li>
  <li><strong>Auto-lock</strong> — Set screen timeout to 1–2 minutes maximum</li>
  <li><strong>OS updates</strong> — Apply updates promptly; they contain critical security patches</li>
  <li><strong>App sources</strong> — Only install apps from official stores (App Store, Google Play)</li>
  <li><strong>App permissions</strong> — Review permissions; deny anything not needed for the app's function</li>
  <li><strong>Remote wipe</strong> — Enable Find My iPhone or Android Device Manager</li>
  <li><strong>MDM</strong> — If using your device for work, follow your organisation's Mobile Device Management policy</li>
</ul>""",
        "callouts": [
            {"type": "warning", "text": "Over 3 million malicious apps were removed from Google Play and Apple App Store in 2023 — official stores aren't foolproof. Always check permissions."},
            {"type": "tip", "text": "Enable remote wipe on all devices. If lost or stolen, you can erase all data before it reaches the wrong hands."}
        ]
    })

module(token, cid,
    title="Safe vs Risky Mobile Behaviours", type="dragdrop",
    order=1, xp_reward=25, is_required=True, pass_score=70,
    content={
        "instruction": "Classify each mobile behaviour as Safe or Risky.",
        "categories": ["Safe Behaviour", "Risky Behaviour"],
        "items": [
            {"text": "Enabling biometric lock with a 6-digit PIN fallback", "category": "Safe Behaviour"},
            {"text": "Installing an APK file sent via WhatsApp from an unknown contact", "category": "Risky Behaviour"},
            {"text": "Keeping iOS/Android updated to the latest version promptly", "category": "Safe Behaviour"},
            {"text": "Using 1234 as your PIN to save time unlocking", "category": "Risky Behaviour"},
            {"text": "Enabling remote wipe via Find My Phone", "category": "Safe Behaviour"},
            {"text": "Granting a torch app access to your contacts and microphone", "category": "Risky Behaviour"},
            {"text": "Only installing apps from the official App Store or Google Play", "category": "Safe Behaviour"},
            {"text": "Jailbreaking your phone to install unofficial apps", "category": "Risky Behaviour"},
        ]
    })

module(token, cid,
    title="Mobile Security Quiz", type="quiz",
    order=2, xp_reward=25, is_required=True, pass_score=75,
    content={"questions": [
        {"text": "You receive an SMS from your bank saying your account is locked — click the link to verify. This is most likely:",
         "options": {"a": "A genuine alert — banks use SMS", "b": "A smishing (SMS phishing) attack", "c": "A test from your bank's security team", "d": "An automated fraud alert"},
         "correct": "b", "explanation": "This is a classic smishing attack. Banks never ask you to verify credentials via an SMS link. Go directly to your bank's official app or website."},
        {"text": "What does jailbreaking an iPhone do to its security?",
         "options": {"a": "Improves battery performance", "b": "Removes Apple's security controls and sandboxing", "c": "Adds extra encryption", "d": "Makes it harder to track if stolen"},
         "correct": "b", "explanation": "Jailbreaking removes iOS security controls, sandboxing, and code signing — allowing apps to access other apps' data and install unvetted software."},
        {"text": "A new flashlight app requests access to contacts, microphone, and location. You should:",
         "options": {"a": "Grant all permissions — it needs them", "b": "Only grant location since flashlights might need GPS", "c": "Deny all — a flashlight only needs camera/torch access", "d": "Uninstall and reinstall"},
         "correct": "c", "explanation": "Excessive permissions are a major red flag for data-harvesting malware. A legitimate flashlight app has no need for contacts, microphone, or location."},
    ]})

module(token, cid,
    title="Scenario: The Lost Company Phone", type="scenario",
    order=3, xp_reward=35, is_required=True, pass_score=70,
    content={
        "description": "You've just realised you left your company-issued smartphone on the train 45 minutes ago. The phone contains work emails, the company VPN app, and an authenticator app used for accessing company systems. It has a 6-digit PIN lock.\n\nYou're now back at the office.",
        "choices": [
            {"text": "Wait until tonight to check lost and found before doing anything", "outcome": "45 minutes is enough time for a determined attacker to attempt PIN bypass or extract data. Corporate data is at risk — you must report this immediately and not wait.", "is_correct": False},
            {"text": "Immediately report to IT/security, request remote wipe, and inform your manager", "outcome": "Correct! Immediate reporting activates the lost device procedure. IT can issue a remote wipe before data is compromised. Your manager needs to know as MFA codes may need to be migrated to a new device.", "is_correct": True},
            {"text": "Change your email password to prevent email access from the lost device", "outcome": "A good partial step, but insufficient. The device still has locally cached data, the authenticator app, and possibly stored credentials. Remote wipe is the essential action.", "is_correct": False},
            {"text": "Call the train company's lost property and wait to hear back before acting", "outcome": "Contacting lost property is a secondary action. You must immediately report to IT security and initiate a remote wipe — every minute of delay increases the risk.", "is_correct": False},
        ]
    })

print("\n✅  All 10 courses created successfully — none published.")
print("    Visit /admin/courses to review, edit, and publish when ready.\n")
