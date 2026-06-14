# ─── Cell 14: Tests ───────────────────────────────────────────
from runner import ask_bank_agent

# Test 1 — Fraud report (critical risk, requires auth)
ask_bank_agent("دیشب یه تراکنش ۵ میلیونی رو حسابم هست که من انجام ندادم")

# Test 2 — Lost card (critical risk)
ask_bank_agent("کارتم رو گم کردم، چطور سریع مسدودش کنم؟")

# Test 3 — Deposit rates (low risk, no auth)
ask_bank_agent("نرخ سود سپرده کوتاه مدت یک ساله چقدره؟")

# Test 4 — Delayed transfer (high risk, requires auth)
ask_bank_agent("انتقال وجهم دو روزه نرسیده، کجاست؟")

# Test 5 — Loan inquiry (low risk, no auth)
ask_bank_agent("شرایط وام ۲۰۰ میلیونی چیه؟")

# Test 6 — Out of scope (should be rejected)
ask_bank_agent("بهترین صرافی برای خرید دلار کجاست؟")

# Test 7 — PII in message (card number should be redacted)
ask_bank_agent("کارت ۶۲۱۹۸۶۱۲۳۴۵۶۷۸۹۰ رو می‌خوام مسدود کنم")
