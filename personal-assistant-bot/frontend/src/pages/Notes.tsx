import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotes, createNote, deleteNote, getBusinesses } from "../api/client";
import Modal from "../components/Modal";
import { Plus, Trash2 } from "lucide-react";

export default function Notes() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ content: "", business_id: "", tags: "" });

  const { data: notes = [] } = useQuery({
    queryKey: ["notes"],
    queryFn: () => getNotes({ limit: 50 }).then((r) => r.data),
  });

  const { data: businesses = [] } = useQuery({
    queryKey: ["businesses"],
    queryFn: () => getBusinesses({ active: true }).then((r) => r.data),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteNote(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notes"] }),
  });

  const createMut = useMutation({
    mutationFn: () =>
      createNote({
        content: form.content,
        business_id: form.business_id ? Number(form.business_id) : null,
        tags: form.tags ? form.tags.split(",").map((t) => t.trim()).filter(Boolean) : [],
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes"] });
      setShowModal(false);
      setForm({ content: "", business_id: "", tags: "" });
    },
  });

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notas</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          <Plus size={16} /> Nova nota
        </button>
      </div>

      {notes.length === 0 ? (
        <p className="text-gray-400">Nenhuma nota cadastrada.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {notes.map((n: Record<string, unknown>) => (
            <div key={n.id as number} className="bg-white border rounded-xl p-4 relative group">
              <button
                onClick={() => deleteMut.mutate(n.id as number)}
                className="absolute top-3 right-3 p-1 text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-50 rounded"
              >
                <Trash2 size={14} />
              </button>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{n.content as string}</p>
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                {n.business_name && (
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                    {n.business_emoji as string} {n.business_name as string}
                  </span>
                )}
                {(n.tags as string[])?.map((tag) => (
                  <span key={tag} className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                    #{tag}
                  </span>
                ))}
                <span className="ml-auto text-xs text-gray-400">
                  {new Date(n.created_at as string).toLocaleDateString("pt-BR")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <Modal title="Nova nota" onClose={() => setShowModal(false)}>
          <div className="space-y-3">
            <textarea
              placeholder="Conteúdo *"
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm h-28 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
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
              placeholder="Tags separadas por vírgula (ex: ideia, campanha)"
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
                Cancelar
              </button>
              <button
                onClick={() => createMut.mutate()}
                disabled={!form.content || createMut.isPending}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Salvar
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
