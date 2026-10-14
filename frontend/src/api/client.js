// All backend communication goes through this Axios module. The frontend never touches SQLite.
import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const http = axios.create({
  baseURL,
  timeout: 10000,
  headers: { "Content-Type": "application/json", Accept: "application/json" },
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("clinic-access-token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const data = (promise) => promise.then((response) => response.data);

export const register = (payload) => data(http.post("/auth/register", payload));
export const login = (payload) => data(http.post("/auth/login", payload));
export const getCurrentUser = () => data(http.get("/auth/me"));
export const getSchedulingConfig = () => data(http.get("/config/scheduling"));
export const listDoctors = () => data(http.get("/doctors/"));
export const listAppointments = (params = {}) => data(http.get("/appointments/", { params }));
export const getDoctorAvailability = (doctorId, date) =>
  data(http.get(`/doctors/${doctorId}/availability`, { params: { date } }));
export const createPaymentOrder = (payload) => data(http.post("/payments/orders", payload));
export const verifyPayment = (payload) => data(http.post("/payments/verify", payload));
export const cancelPaymentOrder = (appointmentId) => data(http.post(`/payments/${appointmentId}/cancel`));
export const cancelAppointment = (id) => data(http.delete(`/appointments/${id}`));
export const blockSlot = (slot) => data(http.post("/appointments/block", { slot }));
export const getDoctorProfile = () => data(http.get("/doctors/me"));
export const updateDoctorProfile = (payload) => data(http.patch("/doctors/me", payload));
export const getDoctorReports = () => data(http.get("/doctors/me/reports"));

/** Turn any Axios error into a short, user-friendly message. */
export function describeError(error) {
  if (!error.response) {
    return error.code === "ECONNABORTED"
      ? "The server took too long to respond. Please try again."
      : `Cannot reach the server at ${baseURL}. Is the backend running?`;
  }
  const { status, data: body } = error.response;
  const apiMessage = body?.error?.message;
  const detail = body?.error?.details?.[0]?.message;
  switch (status) {
    case 404:
      return apiMessage || "That item no longer exists.";
    case 409:
      return "That time was just taken or already changed. Availability has been refreshed - please pick another slot.";
    case 422:
      return [apiMessage, detail].filter(Boolean).join(" ") || "Some of the information is invalid.";
    default:
      return apiMessage || "Something went wrong on the server. Please try again.";
  }
}
