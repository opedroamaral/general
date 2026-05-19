"""Handlers para botões inline do Telegram."""
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from db.session import get_db_session
from db.queries.tasks import create_task, mark_task_done, update_task
from db.queries.routines import mark_routine_done
from db.queries.notes import create_note


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("Cancelado.")
        return

    parts = data.split(":", 3)
    action = parts[0]

    if action == "biz":
        # biz:<type>:<business_id>:<title>
        _, item_type, biz_id_str, title = parts
        biz_id = int(biz_id_str) if biz_id_str != "0" else None
        await _create_from_biz_selection(query, context, item_type, biz_id, title)

    elif action == "done":
        # done:task:<id> or done:routine:<id>
        _, item_type, item_id = parts[0], parts[1], int(parts[2])
        db = get_db_session()
        try:
            if item_type == "task":
                task = mark_task_done(db, item_id)
                await query.edit_message_text(f"✅ Tarefa *{task.title}* concluída!", parse_mode="Markdown")
            elif item_type == "routine":
                routine = mark_routine_done(db, item_id)
                await query.edit_message_text(f"✅ Rotina *{routine.title}* feita hoje!", parse_mode="Markdown")
        finally:
            db.close()

    elif action == "cancel" and len(parts) == 3:
        # cancel:task:<id>
        _, item_type, item_id = parts[0], parts[1], int(parts[2])
        if item_type == "task":
            db = get_db_session()
            try:
                update_task(db, item_id, status="cancelled")
                await query.edit_message_text(f"🗑 Tarefa #{item_id} cancelada.")
            finally:
                db.close()

    elif action == "priority":
        # priority:<value>:<context_data>
        _, priority, ctx_data = parts[0], parts[1], parts[2]
        pending = context.user_data.get("pending", {})
        pending["priority"] = priority
        context.user_data["pending"] = pending
        await query.edit_message_text(f"Prioridade definida: {priority}. Confirma criação?")


async def _create_from_biz_selection(query, context, item_type, biz_id, title):
    db = get_db_session()
    try:
        if item_type == "task":
            pending = context.user_data.get("pending", {})
            entities = pending.get("entities", {})

            due_date = None
            if entities.get("due_date"):
                try:
                    due_date = datetime.strptime(entities["due_date"], "%Y-%m-%d").date()
                except ValueError:
                    pass

            task = create_task(
                db,
                title=title,
                business_id=biz_id,
                due_date=due_date,
                priority=entities.get("priority") or "normal",
            )
            context.user_data.clear()
            await query.edit_message_text(f"✅ Tarefa *#{task.id} {task.title}* criada!", parse_mode="Markdown")

        elif item_type == "note":
            pending = context.user_data.get("pending", {})
            content = pending.get("content", title)
            note = create_note(db, content=content, business_id=biz_id)
            context.user_data.clear()
            await query.edit_message_text(f"📝 Nota #{note.id} salva!")
    finally:
        db.close()
