"""GPT-4o-mini: classifica intenção e extrai entidades de mensagens livres."""
import json
from datetime import date
from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = f"""Você é um classificador de intenções para um assistente pessoal.
Data de hoje: {date.today().isoformat()}

Analise a mensagem e retorne JSON com:
{{
  "intent": "create_task" | "create_routine" | "create_note" | "question" | "mark_done" | "other",
  "entities": {{
    "title": str | null,
    "business_name": str | null,
    "due_date": "YYYY-MM-DD" | null,
    "due_time": "HH:MM" | null,
    "priority": "low" | "normal" | "high" | null,
    "description": str | null,
    "frequency": "daily" | "weekly" | "monthly" | null,
    "weekdays": "1,2,3,4,5" | null,
    "remind_time": "HH:MM" | null,
    "content": str | null,
    "tags": ["tag1", "tag2"] | null,
    "task_id": int | null
  }},
  "ambiguous_business": bool,
  "confidence": float
}}

Regras:
- "amanhã" = data de hoje + 1 dia
- "hoje" = data de hoje
- "próxima semana" = data de hoje + 7 dias
- Se mencionar negócio/empresa/projeto, extraia em business_name
- Para rotinas: "todo dia" = daily, "toda semana" = weekly, "todo mês" = monthly
- Se intent = create_note, o conteúdo completo vai em "content"
- ambiguous_business = true se o negócio mencionado pode corresponder a múltiplos
- Retorne APENAS o JSON, sem markdown ou explicação"""


async def classify(message: str) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, KeyError):
        return {"intent": "other", "entities": {}, "ambiguous_business": False, "confidence": 0}
