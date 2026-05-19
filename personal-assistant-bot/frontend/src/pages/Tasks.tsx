import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTasks, createTask, markTaskDone, deleteTask, getBusinesses } from "../api/client";
import Modal from "../components/Modal";
import { Plus, Check, Trash2 } from "lucide-react";
import clsx from "clsx";

const PRIORITY_COLOR: Record<string, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  normal: "bg-blue-100 text-blue-700 border-blue-200",
  low: "bg-gray-100 text-gray-600 border-gray-200",
};

const STATUS_FILTER = ["all", "pending", "done", "cancelled"];

export default function Tasks() {
  const qc = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("pending");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ title: "", business_id: "", due_date: "", priority: "normal", description: "" });

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks", statusFilter],
    queryFn: () => getTasks(statusFilter !== "all" ? { status: statusFilter } : {}).then((r) => r.data),
  });

  const { data: businesses = [] } = useQuery({
    queryKey: ["businesses"],
    queryFn: () => getBusinesses({ active: true }).then((r) => r.data),
  });

  const doneMut = useMutation({
    mutationFn: (id: number) => markTaskDone(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteTask(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });

  const createMut = useMutation({
    mutationFn: () =>
      createTask({
        title: form.title,
        business_id: form.business_id ? Number(form.business_id) : null,
        due_date: form.due_date || null,
        priority: form.priority,
        description: form.description || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tasks"] });
      setShowModal(false);
      setForm({ title: "", business_id: "", due_date: "", priority: "normal", description: "" });
    },
  });

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Tarefas</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <Plus size={16} /> Nova tarefa
        </button>
      </div>

      <div className="flex gap-2">
        {STATUS_FILTER.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={clsx(
              "px-3 py-1 rounded-full text-sm font-medium capitalize transition-colors",
              statusFilter === s ? "bg-slate-800 text-white" : "bg-white border text-gray-600 hover:bg-gray-50"
            )}
          >
            {s === "all" ? "Todas" : s === "pending" ? "Pendentes" : s === "done" ? "Concluídas" : "Canceladas"}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-400">Carregando...</p>
      ) : tasks.length === 0 ? (
        <p className="text-gray-400">Nenhuma tarefa.</p>
      ) : (
        <ul className="space-y-2">
          {tasks.map((t: Record<string, string>) => (
            <li key={t.id} className="bg-white border rounded-xl px-4 py-3 flex items-center gap-3">
              <span className={clsx("px-2 py-0.5 rounded-full text-xs font-medium border", PRIORITY_COLOR[t.priority])}>
                {t.priority === "high" ? "Alta" : t.priority === "low" ? "Baixa" : "Normal"}
              </span>
              <div className="flex-1 min-w-0">
                <p className={clsx("font-medium truncate", t.status === "done" && "line-through text-gray-400")}>
                  {t.title}
                </p>
                <p className="text-xs text-gray-400">
                  {t.business_emoji} {t.business_name ?? "Pessoal"}
                  {t.due_date && ` · ${new Date(t.due_date + "T00:00").toLocaleDateString("pt-BR")}`}
                </p>
              </div>
              {t.status === "pending" && (
                <button onClick={() => doneMut.mutate(Number(t.id))} className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg">
                  <Check size={16} />
                </button>
              )}
              <button onClick={() => deleteMut.mutate(Number(t.id))} className="p-1.5 text-red-400 hover:bg-red-50 rounded-lg">
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}

      {showModal && (
        <Modal title="Nova tarefa" onClose={() => setShowModal(false)}>
          <div className="space-y-3">
            <input
              placeholder="Título *"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={form.business_id}
              onChange={(e) => setForm({ ...form, business_id: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="">Pessoal</option>
              {businesses.map((b: Record<string, string>) => (
                <option key={b.id} value={b.id}>{b.emoji} {b.name}</option>
              ))}
            </select>
            <input
              type="date"
              value={form.due_date}
              onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="low">Baixa</option>
              <option value="normal">Normal</option>
              <option value="high">Alta</option>
            </select>
            <textarea
              placeholder="Descrição (opcional)"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm h-20 resize-none"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
                Cancelar
              </button>
              <button
                onClick={() => createMut.mutate()}
                disabled={!form.title || createMut.isPending}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Criar
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
