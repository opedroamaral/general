"""Monta contexto dinâmico com dados do banco para enviar à IA."""
from datetime import date
from db.session import get_db_session
from db.queries.tasks import get_tasks, get_overdue_tasks
from db.queries.routines import get_routines, get_routines_for_today
from db.queries.notes import get_notes
from db.queries.businesses import get_businesses


def build_context() -> str:
    db = get_db_session()
    try:
        today = date.today()
        businesses = get_businesses(db, active=True)
        pending_tasks = get_tasks(db, status="pending")
        overdue = get_overdue_tasks(db)
        today_routines = get_routines_for_today(db)
        recent_notes = get_notes(db, limit=10)

        lines = [f"DATA ATUAL: {today.strftime('%d/%m/%Y (%A)')}"]

        # Negócios
        if businesses:
            lines.append("\nNEGÓCIOS ATIVOS:")
            for b in businesses:
                emoji = b.emoji or "•"
                desc = f" — {b.description}" if b.description else ""
                lines.append(f"  {emoji} {b.name} (ID:{b.id}){desc}")

        # Tarefas pendentes
        if pending_tasks:
            lines.append(f"\nTAREFAS PENDENTES ({len(pending_tasks)}):")
            for t in pending_tasks:
                biz = f"[{t.business.name}] " if t.business else "[Pessoal] "
                due = f" — prazo: {t.due_date.strftime('%d/%m')}" if t.due_date else ""
                overdue_flag = " ⚠️ ATRASADA" if t in overdue else ""
                prio = f" ({t.priority})" if t.priority != "normal" else ""
                lines.append(f"  #{t.id} {biz}{t.title}{due}{prio}{overdue_flag}")
        else:
            lines.append("\nTAREFAS PENDENTES: nenhuma")

        if overdue:
            lines.append(f"\n⚠️ TAREFAS ATRASADAS: {len(overdue)}")

        # Rotinas de hoje
        if today_routines:
            lines.append(f"\nROTINAS DE HOJE ({len(today_routines)}):")
            for r in today_routines:
                done_today = r.last_done == today if r.last_done else False
                status = "✅ feita" if done_today else "⏳ pendente"
                biz = f"[{r.business.name}] " if r.business else "[Pessoal] "
                lines.append(f"  #{r.id} {biz}{r.title} — {status}")

        # Notas recentes
        if recent_notes:
            lines.append(f"\nNOTAS RECENTES ({len(recent_notes)}):")
            for n in recent_notes:
                biz = f"[{n.business.name}] " if n.business else "[Pessoal] "
                snippet = n.content[:80] + "..." if len(n.content) > 80 else n.content
                lines.append(f"  #{n.id} {biz}{snippet}")

        return "\n".join(lines)
    finally:
        db.close()
