# ─── Cell 11: Node 9 — finalize ──────────────────────────────
from states.state import BankState
from models.llms import llm_primary

def finalize(state: BankState) -> BankState:
    """
    Node 9 — finalize
    - Out-of-scope → polite Persian rejection
    - Valid → translate approved English draft to professional Persian
    """
    if not state.get("is_relevant", True):
        state["final_answer"] = (
            "با عرض پوزش، این سامانه تنها برای پاسخ به سوالات مرتبط با خدمات بانکی طراحی شده است.\n"
            "لطفاً سوال خود را درباره یکی از موضوعات زیر مطرح فرمایید:\n"
            "• افتتاح حساب و خدمات سپرده‌گذاری\n"
            "• انتقال وجه و تراکنش‌های بانکی\n"
            "• کارت‌های بانکی (فعال‌سازی، مسدودسازی، رمز)\n"
            "• وام و تسهیلات\n"
            "• گزارش تراکنش مشکوک یا کارت مفقودی\n"
            "• سایر خدمات بانکی\n\n"
            "آیا می‌توانم در یکی از موضوعات بالا راهنمایی‌تان کنم؟"
        )
        state["audit_log"] += "\n[finalize] out-of-scope rejection delivered"
        return state

    prompt = """You are a professional Persian-language banking communications specialist.

Translate the following English banking response into natural, formal, and compliant Persian (Farsi).

══════════════════════════════════════════════
TRANSLATION RULES — follow all of them:
══════════════════════════════════════════════
[T1] Use formal register throughout — address the customer as "شما" never "تو"
[T2] Keep all numbers, codes, reference numbers, and app names exactly as-is
     (e.g., "شماره ۲۴۴۴"، "My Bank App"، "*1234#")
[T3] Preserve ALL specific details: amounts, timeframes, step numbers, URLs
[T4] Make it sound natural to an Iranian bank customer — avoid word-for-word translation
[T5] Use proper Persian punctuation: ،  ؛  .  and line breaks between steps
[T6] For high-urgency topics (fraud, lost card), begin with an empathetic opening sentence
[T7] End with a professional closing: "آیا سوال دیگری دارید؟" or "در صورت نیاز به راهنمایی بیشتر در کنار شما هستیم."
[T8] Do NOT add information that was not in the English original
══════════════════════════════════════════════

--- EXAMPLE ---

English:
"We understand this is urgent. To immediately block your lost card, open the mobile app, go to Cards > Block Card, or call our 24/7 hotline at 2444. Please also change your online banking password right away. For the replacement card, visit any branch with your national ID. Investigation of any unauthorized transactions takes 5-7 business days."

Persian:
"متوجه فوریت این موضوع هستیم و از نگرانی شما کاملاً آگاهیم.
برای مسدودسازی فوری کارت مفقودی، وارد اپلیکیشن موبایل شوید و از مسیر کارت‌ها ← مسدودسازی کارت اقدام فرمایید؛ یا با خط ویژه ۲۴ ساعته ما به شماره ۲۴۴۴ تماس بگیرید.
همچنین توصیه می‌شود رمز اینترنتی حساب خود را فوری تغییر دهید.
برای دریافت کارت المثنی، با کارت ملی به هر یک از شعب بانک مراجعه فرمایید.
بررسی هرگونه تراکنش غیرمجاز بین ۵ تا ۷ روز کاری زمان می‌برد.
آیا سوال دیگری دارید؟"

--- END EXAMPLE ---

English response to translate:
{draft}

Write the final Persian response:"""

    state["final_answer"] = llm_primary.invoke(
        prompt.format(draft=state["draft"])
    ).content.strip()

    state["audit_log"] += "\n[finalize] Persian response delivered"
    return state
