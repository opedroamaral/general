"""GPT-4o: resumos leves para /hoje, /semana e lembretes diários."""
from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def summarize(prompt: str, context: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Você é o assistente pessoal de {settings.user_name}. "
                    "Seja direto, prático e use bullet points. Responda em português. "
                    "Não use emojis em excesso.\n\n"
                    f"CONTEXTO ATUAL:\n{context}"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
