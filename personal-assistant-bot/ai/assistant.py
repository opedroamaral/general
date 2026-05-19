"""Claude Sonnet: análise complexa, /ia, /resumo, insights proativos."""
import anthropic
from config import settings
from db.session import get_db_session
from db.queries.ai_messages import get_recent_messages, add_message

claude = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_BASE = f"""Você é o assistente pessoal e executivo de {settings.user_name}.
Você conhece todos os seus negócios, tarefas, rotinas e notas.
Seja direto, prático e proativo. Responda em português.
Quando identificar padrões ou riscos, mencione.
Não repita o contexto de volta, apenas use-o para responder.

CONTEXTO ATUAL:
{{context}}"""


async def ask(user_message: str, context: str) -> str:
    db = get_db_session()
    try:
        history = get_recent_messages(db, limit=20)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": user_message})

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_BASE.format(context=context),
            messages=messages,
        )
        reply = response.content[0].text

        add_message(db, "user", user_message)
        add_message(db, "assistant", reply)

        return reply
    finally:
        db.close()


async def generate_executive_summary(context: str) -> str:
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_BASE.format(context=context),
        messages=[{
            "role": "user",
            "content": (
                "Gere um resumo executivo semanal completo. Inclua:\n"
                "1. Estado geral dos negócios\n"
                "2. Tarefas críticas e atrasadas\n"
                "3. Rotinas que não foram feitas\n"
                "4. Insights e alertas proativos\n"
                "5. Recomendações de prioridade para a próxima semana"
            ),
        }],
    )
    return response.content[0].text


async def generate_proactive_alert(context: str, alert_type: str) -> str:
    prompts = {
        "morning": "Gere uma mensagem de bom dia com as prioridades do dia. Seja motivador e direto.",
        "evening": "Faça um check-in noturno: o que foi feito, o que ficou pendente, e o que é urgente amanhã.",
        "overdue": "Liste as tarefas atrasadas com urgência e sugira como priorizar.",
        "week_preview": "Prévia da semana seguinte: quais compromissos e rotinas estão agendados.",
    }
    prompt = prompts.get(alert_type, "Dê uma atualização geral.")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        system=SYSTEM_BASE.format(context=context),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
