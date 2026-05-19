from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def business_selection_keyboard(businesses, action: str, extra: str = ""):
    """Keyboard para selecionar negócio. action = 'task'|'note'|'routine'."""
    buttons = []
    for biz in businesses:
        emoji = biz.emoji or ""
        label = f"{emoji} {biz.name}".strip()
        buttons.append([InlineKeyboardButton(label, callback_data=f"biz:{action}:{biz.id}:{extra}")])
    buttons.append([InlineKeyboardButton("👤 Pessoal", callback_data=f"biz:{action}:0:{extra}")])
    buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard(action: str, data: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm:{action}:{data}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ]
    ])


def priority_keyboard(context_data: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴 Alta", callback_data=f"priority:high:{context_data}"),
            InlineKeyboardButton("🟡 Normal", callback_data=f"priority:normal:{context_data}"),
            InlineKeyboardButton("🟢 Baixa", callback_data=f"priority:low:{context_data}"),
        ],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")],
    ])


def task_actions_keyboard(task_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Feito", callback_data=f"done:task:{task_id}"),
            InlineKeyboardButton("🗑 Cancelar", callback_data=f"cancel:task:{task_id}"),
        ]
    ])


def routine_done_keyboard(routine_id: int):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Marcar como feita", callback_data=f"done:routine:{routine_id}")
    ]])
