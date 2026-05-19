import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Tasks from "./pages/Tasks";
import Routines from "./pages/Routines";
import Notes from "./pages/Notes";
import Businesses from "./pages/Businesses";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("token");
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="routines" element={<Routines />} />
          <Route path="notes" element={<Notes />} />
          <Route path="businesses" element={<Businesses />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
