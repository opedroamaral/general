from datetime import date, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from db.session import get_db_session
from db.queries.tasks import get_tasks, get_tasks_due_today, mark_task_done, get_task
from db.queries.routines import get_routines, get_routines_for_today
from db.queries.notes import get_notes
from db.queries.businesses import get_businesses, create_business
from ai.context_builder import build_context
from ai.summarizer import summarize
from ai.assistant import ask, generate_executive_summary
from bot.keyboards import business_selection_keyboard


def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != settings.telegram_allowed_user_id:
            await update.message.reply_text("⛔ Acesso não autorizado.")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


def fmt_task(t) -> str:
    biz = f"[{t.business.name}] " if t.business else ""
    due = f" · {t.due_date.strftime('%d/%m')}" if t.due_date else ""
    prio = {"high": "🔴", "low": "🟢"}.get(t.priority, "🟡")
    return f"{prio} #{t.id} {biz}{t.title}{due}"


@authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Olá, {settings.user_name}! Sou seu assistente pessoal.\n\n"
        "Pode me mandar qualquer coisa em linguagem natural ou usar os comandos:\n"
        "/ajuda — lista completa de comandos"
    )


@authorized
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Comandos disponíveis:*\n\n"
        "/hoje — visão do dia\n"
        "/semana — resumo semanal\n"
        "/tarefas — tarefas pendentes\n"
        "/tarefas [negócio] — filtrar por negócio\n"
        "/rotinas — rotinas ativas\n"
        "/notas — últimas notas\n"
        "/negocios — negócios cadastrados\n"
        "/novo\\_negocio — cadastrar negócio\n"
        "/feito [id] — marcar tarefa como feita\n"
        "/ia [pergunta] — consulta à IA\n"
        "/resumo — análise executiva semanal\n\n"
        "Ou simplesmente escreva o que quiser! Ex:\n"
        "• _Ligar pro fornecedor amanhã_\n"
        "• _Anota: ideia de campanha_\n"
        "• _Como está minha semana?_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


@authorized
async def hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ctx = build_context()
    resp = await summarize("Mostre o panorama do dia: rotinas de hoje e tarefas com prazo hoje.", ctx)
    await update.message.reply_text(resp)


@authorized
async def semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ctx = build_context()
    resp = await summarize(
        "Mostre o resumo da semana: tarefas pendentes agrupadas por negócio, rotinas e prazos próximos.", ctx
    )
    await update.message.reply_text(resp)


@authorized
async def tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db_session()
    try:
        filter_name = " ".join(context.args) if context.args else None
        business_id = None

        if filter_name:
            from db.queries.businesses import get_business_by_name
            biz = get_business_by_name(db, filter_name)
            if biz:
                business_id = biz.id
            else:
                await update.message.reply_text(f"Negócio '{filter_name}' não encontrado.")
                return

        tasks = get_tasks(db, business_id=business_id, status="pending")
        if not tasks:
            await update.message.reply_text("Nenhuma tarefa pendente. 🎉")
            return

        lines = ["*Tarefas pendentes:*"]
        for t in tasks:
            lines.append(fmt_task(t))
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        db.close()


@authorized
async def rotinas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db_session()
    try:
        items = get_routines(db, active=True)
        if not items:
            await update.message.reply_text("Nenhuma rotina cadastrada.")
            return

        lines = ["*Rotinas ativas:*"]
        for r in items:
            biz = f"[{r.business.name}] " if r.business else ""
            freq = {"daily": "Diária", "weekly": "Semanal", "monthly": "Mensal"}.get(r.frequency, r.frequency)
            time_str = f" às {r.remind_time.strftime('%H:%M')}" if r.remind_time else ""
            last = f" · última: {r.last_done.strftime('%d/%m')}" if r.last_done else ""
            lines.append(f"• #{r.id} {biz}{r.title} ({freq}{time_str}){last}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        db.close()


@authorized
async def notas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db_session()
    try:
        items = get_notes(db, limit=10)
        if not items:
            await update.message.reply_text("Nenhuma nota cadastrada.")
            return

        lines = ["*Últimas notas:*"]
        for n in items:
            biz = f"[{n.business.name}] " if n.business else ""
            snippet = n.content[:100] + "..." if len(n.content) > 100 else n.content
            lines.append(f"• #{n.id} {biz}{snippet}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        db.close()


@authorized
async def negocios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db_session()
    try:
        items = get_businesses(db, active=True)
        if not items:
            await update.message.reply_text("Nenhum negócio cadastrado. Use /novo_negocio")
            return

        lines = ["*Negócios ativos:*"]
        for b in items:
            emoji = b.emoji or "•"
            desc = f"\n  _{b.description}_" if b.description else ""
            lines.append(f"{emoji} *{b.name}* (ID:{b.id}){desc}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        db.close()


@authorized
async def novo_negocio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wizard"] = "business_name"
    await update.message.reply_text("Qual é o nome do negócio?")


@authorized
async def feito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /feito [id da tarefa]")
        return

    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return

    db = get_db_session()
    try:
        task = mark_task_done(db, task_id)
        if not task:
            await update.message.reply_text("Tarefa não encontrada.")
        else:
            await update.message.reply_text(f"✅ *{task.title}* marcada como concluída!", parse_mode="Markdown")
    finally:
        db.close()


@authorized
async def ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args) if context.args else None
    if not question:
        await update.message.reply_text("Use: /ia [sua pergunta]")
        return

    await update.message.reply_text("Consultando IA...")
    ctx = build_context()
    resp = await ask(question, ctx)
    await update.message.reply_text(resp)


@authorized
async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gerando análise executiva...")
    ctx = build_context()
    resp = await generate_executive_summary(ctx)
    await update.message.reply_text(resp)
