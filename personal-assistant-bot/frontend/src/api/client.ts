import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// Auth
export const login = (password: string) =>
  api.post<{ access_token: string }>("/auth/login", { password });

// Stats
export const getStats = () => api.get("/stats");

// Tasks
export const getTasks = (params?: Record<string, unknown>) =>
  api.get("/tasks/", { params });
export const createTask = (data: Record<string, unknown>) =>
  api.post("/tasks/", data);
export const updateTask = (id: number, data: Record<string, unknown>) =>
  api.put(`/tasks/${id}`, data);
export const markTaskDone = (id: number) => api.patch(`/tasks/${id}/done`);
export const deleteTask = (id: number) => api.delete(`/tasks/${id}`);

// Routines
export const getRoutines = (params?: Record<string, unknown>) =>
  api.get("/routines/", { params });
export const createRoutine = (data: Record<string, unknown>) =>
  api.post("/routines/", data);
export const updateRoutine = (id: number, data: Record<string, unknown>) =>
  api.put(`/routines/${id}`, data);
export const markRoutineDone = (id: number) =>
  api.patch(`/routines/${id}/done`);
export const deleteRoutine = (id: number) => api.delete(`/routines/${id}`);

// Notes
export const getNotes = (params?: Record<string, unknown>) =>
  api.get("/notes/", { params });
export const createNote = (data: Record<string, unknown>) =>
  api.post("/notes/", data);
export const updateNote = (id: number, data: Record<string, unknown>) =>
  api.put(`/notes/${id}`, data);
export const deleteNote = (id: number) => api.delete(`/notes/${id}`);

// Businesses
export const getBusinesses = (params?: Record<string, unknown>) =>
  api.get("/businesses/", { params });
export const createBusiness = (data: Record<string, unknown>) =>
  api.post("/businesses/", data);
export const updateBusiness = (id: number, data: Record<string, unknown>) =>
  api.put(`/businesses/${id}`, data);
export const deleteBusiness = (id: number) =>
  api.delete(`/businesses/${id}`);
