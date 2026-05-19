import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, CheckSquare, RefreshCw, FileText, Briefcase, LogOut } from "lucide-react";
import clsx from "clsx";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/tasks", label: "Tarefas", icon: CheckSquare },
  { to: "/routines", label: "Rotinas", icon: RefreshCw },
  { to: "/notes", label: "Notas", icon: FileText },
  { to: "/businesses", label: "Negócios", icon: Briefcase },
];

export default function Sidebar() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <aside className="w-56 bg-slate-800 text-white flex flex-col">
      <div className="px-6 py-5 border-b border-slate-700">
        <span className="text-lg font-bold tracking-tight">🗂 Gestor</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon: Icon, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-700 hover:text-white"
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-slate-700">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
        >
          <LogOut size={16} />
          Sair
        </button>
      </div>
    </aside>
  );
}
