"""
Seed script — creates an admin user and a sample tournament with challenges.
Run: python seed.py
"""
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, SSOProvider
from app.models.tournament import Tournament, Challenge, Difficulty, ChallengeType
from app.auth.jwt import hash_password
import app.models  # noqa

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Admin user
if not db.query(User).filter(User.email == "admin@securequest.local").first():
    admin = User(
        email="admin@securequest.local",
        username="admin",
        hashed_password=hash_password("Admin1234!"),
        role=UserRole.admin,
        sso_provider=SSOProvider.local,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("Created admin@securequest.local / Admin1234!")
else:
    admin = db.query(User).filter(User.email == "admin@securequest.local").first()
    print("Admin already exists")

# Sample tournament
if not db.query(Tournament).filter(Tournament.name == "Phishing Awareness 101").first():
    t = Tournament(
        name="Phishing Awareness 101",
        description="Learn to identify phishing emails, suspicious links, and social engineering tactics.",
        difficulty=Difficulty.easy,
        timer_seconds=180,
        total_timer_seconds=1800,
        is_active=True,
        max_participants=200,
        created_by=admin.id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    challenges = [
        Challenge(
            tournament_id=t.id, order=0,
            title="Spot the Phishing Email",
            description=(
                "From: support@paypa1.com\n"
                "Subject: Urgent: Your account has been suspended\n\n"
                "Dear valued customer,\n\n"
                "We have detected suspicious activity on your PayPal account. "
                "Your account has been temporarily suspended. Please verify your information "
                "immediately by clicking the link below to restore access:\n\n"
                "→ http://paypa1.com/verify-account?token=abc123\n\n"
                "Failure to verify within 24 hours will result in permanent closure.\n\n"
                "PayPal Security Team"
            ),
            type=ChallengeType.phishing, points=10, difficulty_level=Difficulty.easy,
            options={
                "a": "Click the link and enter your credentials",
                "b": "Report it as phishing and delete it",
                "c": "Forward it to colleagues to warn them",
                "d": "Reply asking for more verification details"
            },
            correct_answer="b",
            explanation="Misspelled domains (paypa1 vs paypal) are a classic phishing indicator. Urgency tactics ('24 hours') are also red flags. Always report and delete.",
            hints=["Look very carefully at the sender's email domain.", "Compare the domain letter-by-letter to the real company name."],
        ),
        Challenge(
            tournament_id=t.id, order=1,
            title="Suspicious Link Check",
            description="You receive a message with a link that displays as 'www.yourbank.com/login' but you're unsure if it's legitimate. Before clicking, what is the SAFEST verification step?",
            type=ChallengeType.quiz, points=10, difficulty_level=Difficulty.easy,
            options={
                "a": "Click quickly — it probably loads the right site",
                "b": "Hover over the link to see the real destination URL in the status bar",
                "c": "Copy the display text and paste it into your browser",
                "d": "Trust it — the display text shows the correct bank URL"
            },
            correct_answer="b",
            explanation="Hovering reveals the actual underlying URL. Display text can show anything — attackers routinely mask malicious URLs with legitimate-looking text.",
            hints=["The link's visible text and its actual destination can be completely different.", "Your browser shows the real URL at the bottom when you hover."],
        ),
        Challenge(
            tournament_id=t.id, order=2,
            title="The IT Support Call",
            description=(
                "SCENARIO: It's Monday morning. Your phone rings — it's someone claiming to be from IT support.\n\n"
                "Caller: 'Hi, this is Jake from IT. We've detected a breach on your account and need to "
                "verify your identity RIGHT NOW. Can you read me the 6-digit code that just appeared on your authenticator app?'\n\n"
                "What do you do?"
            ),
            type=ChallengeType.scenario, points=15, difficulty_level=Difficulty.medium,
            options={
                "a": "Give them the code — it's a security emergency",
                "b": "Refuse, hang up, then call IT's official number to verify",
                "c": "Ask them to email you the request first",
                "d": "Give only the first 3 digits to partially verify"
            },
            correct_answer="b",
            explanation="This is vishing (voice phishing). Legitimate IT will NEVER ask for your 2FA code. Always hang up and call IT back on a number you already know.",
            hints=["Ask yourself: who initiated this call?", "Legitimate security teams verify YOUR identity, not the other way around."],
        ),
        Challenge(
            tournament_id=t.id, order=3,
            title="Password Strength Challenge",
            description="Your company requires you to set a new password. Which of the following is the STRONGEST choice?",
            type=ChallengeType.password, points=10, difficulty_level=Difficulty.easy,
            options={
                "a": "Password123!",
                "b": "P@$$w0rd",
                "c": "correct-horse-battery-staple-42",
                "d": "Tr0ub4dor&3"
            },
            correct_answer="c",
            explanation="Long passphrases (correct-horse-battery-staple-42) are the strongest — length beats complexity. A 30-character phrase is exponentially harder to crack than a short complex password.",
            hints=["Password length has the biggest impact on cracking time.", "Think about entropy: more characters = more combinations."],
        ),
        Challenge(
            tournament_id=t.id, order=4,
            title="The USB Drop Attack",
            description=(
                "SCENARIO: Walking to your car after work, you spot a USB drive on the ground. "
                "It's labelled 'Q4 Salary Data — Confidential' in handwriting.\n\n"
                "Several colleagues have gathered around it, curious. One suggests plugging it in "
                "to a spare laptop 'just to see what's on it'.\n\n"
                "What is the CORRECT action?"
            ),
            type=ChallengeType.scenario, points=20, difficulty_level=Difficulty.medium,
            options={
                "a": "Plug it in to a spare/isolated laptop — that's safe enough",
                "b": "Hand it directly to IT Security without plugging it in anywhere",
                "c": "Leave it where it is — not your problem",
                "d": "Take it home and check it on your personal computer"
            },
            correct_answer="b",
            explanation="USB drops are deliberate attacks. Even 'isolated' machines can be compromised. BadUSB attacks execute the moment a drive is inserted — no files need to be opened. Always hand unknown drives to IT Security.",
            hints=["USB drives can run code the instant they're plugged in — no files need opening.", "This is a well-documented attack technique used by real hackers."],
        ),
    ]
    db.add_all(challenges)
    db.commit()
    print(f"Created tournament '{t.name}' with {len(challenges)} challenges")
else:
    # Update existing challenges to add hints if missing
    existing = db.query(Tournament).filter(Tournament.name == "Phishing Awareness 101").first()
    print(f"Sample tournament already exists (id={existing.id})")

db.close()
print("Seed complete.")
