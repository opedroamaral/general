"""Handler de mensagens livres: classifica intenção e age."""
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from db.session import get_db_session
from db.queries.businesses import get_businesses, get_business_by_name
from db.queries.tasks import create_task
from db.queries.routines import create_routine
from db.queries.notes import create_note
from ai.classifier import classify
from ai.context_builder import build_context
from ai.assistant import ask
from bot.keyboards import business_selection_keyboard


def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != settings.telegram_allowed_user_id:
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Handle wizard flows
    wizard = context.user_data.get("wizard")
    if wizard:
        await _handle_wizard(update, context, wizard, text)
        return

    # Handle pending confirmation
    pending = context.user_data.get("pending")
    if pending and text.lower() in ("sim", "s", "yes"):
        await _execute_pending(update, context)
        return
    elif pending and text.lower() in ("não", "nao", "n", "no"):
        context.user_data.clear()
        await update.message.reply_text("Cancelado.")
        return

    # Classify intent
    await update.message.reply_text("...")
    result = await classify(text)
    intent = result.get("intent", "other")
    entities = result.get("entities", {})

    if intent == "create_task":
        await _handle_create_task(update, context, entities, text)
    elif intent == "create_routine":
        await _handle_create_routine(update, context, entities, text)
    elif intent == "create_note":
        await _handle_create_note(update, context, entities, text)
    elif intent in ("question",):
        ctx = build_context()
        resp = await ask(text, ctx)
        await update.message.reply_text(resp)
    else:
        ctx = build_context()
        resp = await ask(text, ctx)
        await update.message.reply_text(resp)


async def _resolve_business(db, business_name: str):
    """Retorna (business, is_ambiguous). None = pessoal."""
    if not business_name:
        return None, False
    biz = get_business_by_name(db, business_name)
    return biz, False


async def _handle_create_task(update, context, entities, original_text):
    db = get_db_session()
    try:
        biz, ambiguous = await _resolve_business(db, entities.get("business_name"))
        title = entities.get("title") or original_text[:100]

        if entities.get("ambiguous_business") or (entities.get("business_name") and not biz):
            businesses = get_businesses(db, active=True)
            context.user_data["pending"] = {
                "type": "task",
                "title": title,
                "entities": entities,
            }
            from bot.keyboards import business_selection_keyboard
            kb = business_selection_keyboard(businesses, "task", title[:50])
            await update.message.reply_text(
                f"Qual negócio para a tarefa *{title}*?",
                reply_markup=kb,
                parse_mode="Markdown",
            )
            return

        due_date = None
        if entities.get("due_date"):
            try:
                due_date = datetime.strptime(entities["due_date"], "%Y-%m-%d").date()
            except ValueError:
                pass

        task = create_task(
            db,
            title=title,
            business_id=biz.id if biz else None,
            description=entities.get("description"),
            due_date=due_date,
            priority=entities.get("priority") or "normal",
        )

        biz_str = f" [{biz.name}]" if biz else " [Pessoal]"
        due_str = f"\nPrazo: {due_date.strftime('%d/%m/%Y')}" if due_date else ""
        await update.message.reply_text(
            f"✅ Tarefa criada!\n*#{task.id} {task.title}*{biz_str}{due_str}",
            parse_mode="Markdown",
        )
    finally:
        db.close()


async def _handle_create_routine(update, context, entities, original_text):
    db = get_db_session()
    try:
        biz, _ = await _resolve_business(db, entities.get("business_name"))
        title = entities.get("title") or original_text[:100]
        frequency = entities.get("frequency") or "daily"

        remind_time = None
        if entities.get("remind_time"):
            try:
                remind_time = datetime.strptime(entities["remind_time"], "%H:%M").time()
            except ValueError:
                pass

        routine = create_routine(
            db,
            title=title,
            frequency=frequency,
            business_id=biz.id if biz else None,
            weekdays=entities.get("weekdays"),
            remind_time=remind_time,
        )

        freq_map = {"daily": "Diária", "weekly": "Semanal", "monthly": "Mensal"}
        biz_str = f" [{biz.name}]" if biz else " [Pessoal]"
        time_str = f" às {remind_time.strftime('%H:%M')}" if remind_time else ""
        await update.message.reply_text(
            f"🔄 Rotina criada!\n*#{routine.id} {routine.title}*{biz_str}\n"
            f"Frequência: {freq_map.get(frequency, frequency)}{time_str}",
            parse_mode="Markdown",
        )
    finally:
        db.close()


async def _handle_create_note(update, context, entities, original_text):
    db = get_db_session()
    try:
        biz, _ = await _resolve_business(db, entities.get("business_name"))
        content = entities.get("content") or original_text

        note = create_note(
            db,
            content=content,
            business_id=biz.id if biz else None,
            tags=entities.get("tags") or [],
        )

        biz_str = f" [{biz.name}]" if biz else " [Pessoal]"
        await update.message.reply_text(
            f"📝 Nota salva!{biz_str}\n_{content[:100]}_",
            parse_mode="Markdown",
        )
    finally:
        db.close()


async def _handle_wizard(update, context, wizard, text):
    db = get_db_session()
    try:
        if wizard == "business_name":
            context.user_data["new_business"] = {"name": text}
            context.user_data["wizard"] = "business_emoji"
            await update.message.reply_text(
                "Qual emoji representa este negócio? (ex: 🏪 💻 🎨)\nOu envie /pular para nenhum."
            )
        elif wizard == "business_emoji":
            emoji = None if text.startswith("/pular") else text.strip()
            context.user_data["new_business"]["emoji"] = emoji
            context.user_data["wizard"] = "business_desc"
            await update.message.reply_text("Descrição breve do negócio? (ou /pular)")
        elif wizard == "business_desc":
            desc = None if text.startswith("/pular") else text
            data = context.user_data["new_business"]
            from db.queries.businesses import create_business
            biz = create_business(db, name=data["name"], emoji=data.get("emoji"), description=desc)
            context.user_data.clear()
            emoji = biz.emoji or ""
            await update.message.reply_text(
                f"🎉 Negócio criado!\n{emoji} *{biz.name}* (ID:{biz.id})",
                parse_mode="Markdown",
            )
    finally:
        db.close()


async def _execute_pending(update, context):
    pending = context.user_data.pop("pending", {})
    context.user_data.clear()

    if pending.get("type") == "task":
        db = get_db_session()
        try:
            task = create_task(db, title=pending["title"], business_id=pending.get("business_id"))
            await update.message.reply_text(f"✅ Tarefa *#{task.id} {task.title}* criada!", parse_mode="Markdown")
        finally:
            db.close()
