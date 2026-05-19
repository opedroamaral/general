import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/client";

export default function Login() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await login(password);
      localStorage.setItem("token", res.data.access_token);
      navigate("/");
    } catch {
      setError("Senha incorreta.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-800">
      <div className="bg-white rounded-2xl shadow-xl p-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🗂</div>
          <h1 className="text-2xl font-bold">Gestor Pessoal</h1>
          <p className="text-gray-500 text-sm mt-1">Acesso restrito</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading || !password}
            className="w-full bg-blue-600 text-white rounded-lg py-2.5 font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
