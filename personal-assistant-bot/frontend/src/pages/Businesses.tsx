import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBusinesses, createBusiness, updateBusiness, deleteBusiness } from "../api/client";
import Modal from "../components/Modal";
import { Plus, Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react";

export default function Businesses() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Record<string, string> | null>(null);
  const [form, setForm] = useState({ name: "", emoji: "", description: "" });

  const { data: businesses = [] } = useQuery({
    queryKey: ["businesses", "all"],
    queryFn: () => getBusinesses().then((r) => r.data),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteBusiness(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["businesses"] }),
  });

  const toggleMut = useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      updateBusiness(id, { active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["businesses"] }),
  });

  const saveMut = useMutation({
    mutationFn: () => {
      const payload = { name: form.name, emoji: form.emoji || null, description: form.description || null };
      return editing
        ? updateBusiness(Number(editing.id), payload)
        : createBusiness(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["businesses"] });
      setShowModal(false);
      setEditing(null);
      setForm({ name: "", emoji: "", description: "" });
    },
  });

  const openEdit = (b: Record<string, string>) => {
    setEditing(b);
    setForm({ name: b.name, emoji: b.emoji ?? "", description: b.description ?? "" });
    setShowModal(true);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Negócios</h1>
        <button
          onClick={() => { setEditing(null); setForm({ name: "", emoji: "", description: "" }); setShowModal(true); }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          <Plus size={16} /> Novo negócio
        </button>
      </div>

      {businesses.length === 0 ? (
        <p className="text-gray-400">Nenhum negócio cadastrado.</p>
      ) : (
        <ul className="space-y-3">
          {businesses.map((b: Record<string, string>) => (
            <li key={b.id} className="bg-white border rounded-xl px-5 py-4 flex items-center gap-4">
              <span className="text-3xl">{b.emoji || "💼"}</span>
              <div className="flex-1">
                <p className="font-semibold">{b.name}</p>
                {b.description && <p className="text-sm text-gray-500">{b.description}</p>}
                <p className="text-xs text-gray-400 mt-0.5">
                  Criado em {new Date(b.created_at).toLocaleDateString("pt-BR")}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => toggleMut.mutate({ id: Number(b.id), active: !b.active })} className="p-2 rounded-lg hover:bg-gray-100">
                  {b.active ? <ToggleRight size={20} className="text-green-500" /> : <ToggleLeft size={20} className="text-gray-400" />}
                </button>
                <button onClick={() => openEdit(b)} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
                  <Pencil size={16} />
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Excluir "${b.name}"?`)) deleteMut.mutate(Number(b.id));
                  }}
                  className="p-2 rounded-lg hover:bg-red-50 text-red-400"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {showModal && (
        <Modal title={editing ? "Editar negócio" : "Novo negócio"} onClose={() => { setShowModal(false); setEditing(null); }}>
          <div className="space-y-3">
            <input
              placeholder="Nome *"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <input
              placeholder="Emoji (ex: 🏪 💻 🎨)"
              value={form.emoji}
              onChange={(e) => setForm({ ...form, emoji: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
            <textarea
              placeholder="Descrição (opcional)"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm h-20 resize-none"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => { setShowModal(false); setEditing(null); }} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
                Cancelar
              </button>
              <button
                onClick={() => saveMut.mutate()}
                disabled={!form.name || saveMut.isPending}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {editing ? "Salvar" : "Criar"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
