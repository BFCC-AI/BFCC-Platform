"""
OMEGA PRIME backend skeleton — OpenAI Agents SDK
Run after installing requirements and setting OPENAI_API_KEY.
This file is intentionally separate from the local MVP, which works without an API key.
"""
from agents import Agent, Runner, handoff

research = Agent(
    name="CSRO AI",
    instructions="حلل السوق والفرص القريبة والمتوسطة والبعيدة، وفرص الدخل وDRIP. أخرج JSON موجزًا."
)
risk = Agent(
    name="CRO AI",
    instructions="راجع التركّز والسيولة والوقف والسيناريوهات. لا توافق على مخاطرة غير محددة."
)
capital = Agent(
    name="CIO AI",
    instructions="اختر أفضل استخدام لرأس المال وحدد مصدر التمويل وخطة إعادة التدوير."
)
ceo = Agent(
    name="CEO AI",
    instructions="اجمع تقارير المديرين وأصدر أمرًا تنفيذيًا منظمًا. لا تنفذ صفقة حقيقية.",
    handoffs=[research, risk, capital],
)

def run_board(portfolio_text: str) -> str:
    result = Runner.run_sync(
        ceo,
        f"شغّل اجتماع OMEGA على بيانات المحفظة التالية:\n{portfolio_text}"
    )
    return str(result.final_output)

if __name__ == "__main__":
    print(run_board("ضع بيانات المحفظة هنا"))
