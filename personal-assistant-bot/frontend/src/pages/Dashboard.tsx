import { useQuery } from "@tanstack/react-query";
import { getStats, getTasks, getRoutines } from "../api/client";
import { CheckSquare, RefreshCw, Briefcase, AlertTriangle } from "lucide-react";
import clsx from "clsx";

function StatCard({ icon: Icon, label, value, color }: {
  icon: React.ElementType; label: string; value: number; color: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4">
      <div className={clsx("p-3 rounded-lg", color)}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-gray-500 text-sm">{label}</p>
      </div>
    </div>
  );
}

const PRIORITY_COLOR: Record<string, string> = {
  high: "bg-red-100 text-red-700",
  normal: "bg-blue-100 text-blue-700",
  low: "bg-gray-100 text-gray-600",
};

export default function Dashboard() {
  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: () => getStats().then((r) => r.data) });
  const { data: tasks } = useQuery({
    queryKey: ["tasks", "pending"],
    queryFn: () => getTasks({ status: "pending" }).then((r) => r.data),
  });
  const { data: routines } = useQuery({
    queryKey: ["routines", "active"],
    queryFn: () => getRoutines({ active: true }).then((r) => r.data),
  });

  const overdueTasks = tasks?.filter((t: Record<string, string>) =>
    t.due_date && new Date(t.due_date) < new Date(new Date().toDateString())
  ) ?? [];

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          {new Date().toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" })}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={CheckSquare} label="Tarefas pendentes" value={stats?.tasks?.pending ?? 0} color="bg-blue-500" />
        <StatCard icon={AlertTriangle} label="Atrasadas" value={stats?.tasks?.overdue ?? 0} color="bg-red-500" />
        <StatCard icon={RefreshCw} label="Rotinas hoje" value={stats?.routines?.today ?? 0} color="bg-green-500" />
        <StatCard icon={Briefcase} label="Negócios ativos" value={stats?.businesses ?? 0} color="bg-purple-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tarefas urgentes */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" />
            Atrasadas / Alta prioridade
          </h2>
          {overdueTasks.length === 0 && tasks?.filter((t: Record<string, string>) => t.priority === "high").length === 0 ? (
            <p className="text-gray-400 text-sm">Nenhuma tarefa urgente</p>
          ) : (
            <ul className="space-y-2">
              {[...overdueTasks, ...(tasks?.filter((t: Record<string, string>) => t.priority === "high") ?? [])]
                .filter((t, i, arr) => arr.findIndex((x: Record<string, string>) => x.id === t.id) === i)
                .slice(0, 6)
                .map((t: Record<string, string>) => (
                  <li key={t.id} className="flex items-center gap-2 text-sm">
                    <span className={clsx("px-2 py-0.5 rounded-full text-xs font-medium", PRIORITY_COLOR[t.priority])}>
                      {t.priority}
                    </span>
                    <span className="truncate">{t.title}</span>
                    {t.business_name && (
                      <span className="ml-auto text-gray-400 text-xs whitespace-nowrap">
                        {t.business_emoji} {t.business_name}
                      </span>
                    )}
                  </li>
                ))}
            </ul>
          )}
        </div>

        {/* Rotinas de hoje */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <RefreshCw size={16} className="text-green-500" />
            Rotinas de hoje
          </h2>
          {!routines?.length ? (
            <p className="text-gray-400 text-sm">Nenhuma rotina para hoje</p>
          ) : (
            <ul className="space-y-2">
              {routines.slice(0, 6).map((r: Record<string, string>) => {
                const doneToday = r.last_done === new Date().toISOString().split("T")[0];
                return (
                  <li key={r.id} className="flex items-center gap-2 text-sm">
                    <span>{doneToday ? "✅" : "⏳"}</span>
                    <span className={clsx("truncate", doneToday && "line-through text-gray-400")}>{r.title}</span>
                    {r.business_name && (
                      <span className="ml-auto text-gray-400 text-xs whitespace-nowrap">
                        {r.business_emoji} {r.business_name}
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
