import asyncio
import os
import uvicorn
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import settings
from db.session import engine
from db.models import Base
from bot.handlers.commands import (
    start, hoje, semana, tarefas, rotinas, notas,
    negocios, novo_negocio, feito, ia_command, resumo, ajuda,
)
from bot.handlers.messages import handle_message
from bot.handlers.callbacks import handle_callback
from bot.scheduler import setup_scheduler
from api.main import app as fastapi_app


def setup_handlers(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hoje", hoje))
    application.add_handler(CommandHandler("semana", semana))
    application.add_handler(CommandHandler("tarefas", tarefas))
    application.add_handler(CommandHandler("rotinas", rotinas))
    application.add_handler(CommandHandler("notas", notas))
    application.add_handler(CommandHandler("negocios", negocios))
    application.add_handler(CommandHandler("novo_negocio", novo_negocio))
    application.add_handler(CommandHandler("pular", lambda u, c: None))  # wizard skip
    application.add_handler(CommandHandler("feito", feito))
    application.add_handler(CommandHandler("ia", ia_command))
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


async def main():
    Base.metadata.create_all(bind=engine)

    application = Application.builder().token(settings.telegram_bot_token).build()
    setup_handlers(application)

    scheduler = setup_scheduler(application.bot)
    scheduler.start()

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)

    try:
        await server.serve()
    finally:
        scheduler.shutdown(wait=False)
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
