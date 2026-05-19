"""APScheduler: lembretes proativos."""
import asyncio
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings
from ai.context_builder import build_context
from ai.assistant import generate_proactive_alert
from db.session import get_db_session
from db.queries.tasks import get_overdue_tasks
from db.queries.ai_messages import clear_old_messages


def setup_scheduler(bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    async def send(text: str):
        await bot.send_message(chat_id=settings.telegram_allowed_user_id, text=text)

    async def morning_briefing():
        ctx = build_context()
        msg = await generate_proactive_alert(ctx, "morning")
        await send(msg)

    async def evening_checkin():
        ctx = build_context()
        msg = await generate_proactive_alert(ctx, "evening")
        await send(msg)

    async def week_preview():
        ctx = build_context()
        msg = await generate_proactive_alert(ctx, "week_preview")
        await send(msg)

    async def overdue_alert():
        db = get_db_session()
        try:
            overdue = get_overdue_tasks(db)
            if not overdue:
                return
            ctx = build_context()
            msg = await generate_proactive_alert(ctx, "overdue")
            await send(msg)
        finally:
            db.close()

    async def cleanup():
        db = get_db_session()
        try:
            clear_old_messages(db)
        finally:
            db.close()

    scheduler.add_job(morning_briefing, "cron", hour=7, minute=0, id="morning")
    scheduler.add_job(evening_checkin, "cron", hour=19, minute=0, id="evening")
    scheduler.add_job(week_preview, "cron", day_of_week="sun", hour=18, minute=0, id="week_preview")
    scheduler.add_job(overdue_alert, "cron", hour=9, minute=0, id="overdue")
    scheduler.add_job(cleanup, "cron", hour=3, minute=0, id="cleanup")

    return scheduler
