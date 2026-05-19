import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getRoutines, createRoutine, markRoutineDone, deleteRoutine, getBusinesses } from "../api/client";
import Modal from "../components/Modal";
import { Plus, Check, Trash2 } from "lucide-react";
import clsx from "clsx";

const FREQ_LABEL: Record<string, string> = { daily: "Diária", weekly: "Semanal", monthly: "Mensal" };

export default function Routines() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    title: "", business_id: "", frequency: "daily", weekdays: "", remind_time: "",
  });

  const { data: routines = [] } = useQuery({
    queryKey: ["routines"],
    queryFn: () => getRoutines({ active: true }).then((r) => r.data),
  });

  const { data: businesses = [] } = useQuery({
    queryKey: ["businesses"],
    queryFn: () => getBusinesses({ active: true }).then((r) => r.data),
  });

  const doneMut = useMutation({
    mutationFn: (id: number) => markRoutineDone(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["routines"] }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteRoutine(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["routines"] }),
  });

  const createMut = useMutation({
    mutationFn: () =>
      createRoutine({
        title: form.title,
        frequency: form.frequency,
        business_id: form.business_id ? Number(form.business_id) : null,
        weekdays: form.weekdays || null,
        remind_time: form.remind_time || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["routines"] });
      setShowModal(false);
      setForm({ title: "", business_id: "", frequency: "daily", weekdays: "", remind_time: "" });
    },
  });

  const today = new Date().toISOString().split("T")[0];

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Rotinas</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <Plus size={16} /> Nova rotina
        </button>
      </div>

      {routines.length === 0 ? (
        <p className="text-gray-400">Nenhuma rotina cadastrada.</p>
      ) : (
        <ul className="space-y-2">
          {routines.map((r: Record<string, string>) => {
            const doneToday = r.last_done === today;
            return (
              <li key={r.id} className={clsx("bg-white border rounded-xl px-4 py-3 flex items-center gap-3", doneToday && "opacity-60")}>
                <span className="text-lg">{doneToday ? "✅" : "⏳"}</span>
                <div className="flex-1 min-w-0">
                  <p className={clsx("font-medium truncate", doneToday && "line-through text-gray-400")}>{r.title}</p>
                  <p className="text-xs text-gray-400">
                    {FREQ_LABEL[r.frequency]}
                    {r.remind_time && ` às ${r.remind_time.slice(0, 5)}`}
                    {r.business_name && ` · ${r.business_emoji} ${r.business_name}`}
                    {r.last_done && ` · última: ${new Date(r.last_done + "T00:00").toLocaleDateString("pt-BR")}`}
                  </p>
                </div>
                {!doneToday && (
                  <button onClick={() => doneMut.mutate(Number(r.id))} className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg">
                    <Check size={16} />
                  </button>
                )}
                <button onClick={() => deleteMut.mutate(Number(r.id))} className="p-1.5 text-red-400 hover:bg-red-50 rounded-lg">
                  <Trash2 size={16} />
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {showModal && (
        <Modal title="Nova rotina" onClose={() => setShowModal(false)}>
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
            <select
              value={form.frequency}
              onChange={(e) => setForm({ ...form, frequency: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="daily">Diária</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensal</option>
            </select>
            {form.frequency === "weekly" && (
              <input
                placeholder="Dias da semana (ex: 1,3,5 = seg/qua/sex)"
                value={form.weekdays}
                onChange={(e) => setForm({ ...form, weekdays: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            )}
            <input
              type="time"
              value={form.remind_time}
              onChange={(e) => setForm({ ...form, remind_time: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
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
