import { useCallback, useEffect, useState } from "react";
import {
  describeError,
  getCurrentUser,
  getDoctorProfile,
  getDoctorReports,
  getSchedulingConfig,
  listAppointments,
  listDoctors,
} from "./api/client";
import AppointmentList from "./components/AppointmentList";
import AuthGate from "./components/AuthGate";
import BookingForm from "./components/BookingForm";
import DoctorDashboard from "./components/DoctorDashboard";
import DoctorList from "./components/DoctorList";
import Notice from "./components/Notice";
import usePolling from "./hooks/usePolling";

export default function App() {
  const [user, setUser] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [doctorProfile, setDoctorProfile] = useState(null);
  const [doctorReport, setDoctorReport] = useState(null);
  const [slotMinutes, setSlotMinutes] = useState(30);
  const [doctorId, setDoctorId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(async () => {
    if (!user) return;
    try {
      const errors = [];
      const [doctorResult, appointmentResult] = await Promise.allSettled([
        listDoctors(),
        listAppointments(),
      ]);
      if (doctorResult.status === "fulfilled") {
        setDoctors(doctorResult.value);
      } else {
        errors.push(describeError(doctorResult.reason));
      }
      if (appointmentResult.status === "fulfilled") {
        setAppointments(appointmentResult.value);
      } else {
        errors.push(describeError(appointmentResult.reason));
      }
      if (user.role === "doctor") {
        const [profileResult, reportResult] = await Promise.allSettled([
          getDoctorProfile(),
          getDoctorReports(),
        ]);
        if (profileResult.status === "fulfilled") {
          setDoctorProfile(profileResult.value);
        } else {
          errors.push(describeError(profileResult.reason));
        }
        if (reportResult.status === "fulfilled") {
          setDoctorReport(reportResult.value);
        } else {
          errors.push(describeError(reportResult.reason));
        }
      }
      setError(errors.length ? { type: "error", text: errors.join(" ") } : null);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    getSchedulingConfig()
      .then((config) => setSlotMinutes(config.slot_duration_minutes))
      .catch((err) => setError({ type: "error", text: describeError(err) }));
    const token = localStorage.getItem("clinic-access-token");
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch((err) => {
        localStorage.removeItem("clinic-access-token");
        if (err.response?.status !== 401) setError({ type: "error", text: describeError(err) });
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (user) refresh();
  }, [user, refresh]);
  usePolling(refresh, user ? 15000 : null);

  const authenticated = (session) => {
    localStorage.setItem("clinic-access-token", session.access_token);
    setDoctorProfile(null);
    setUser(session.user);
  };
  const changed = useCallback(async () => {
    await refresh();
    setRefreshKey((key) => key + 1);
  }, [refresh]);
  const signOut = () => {
    localStorage.removeItem("clinic-access-token");
    setUser(null);
    setDoctors([]);
    setAppointments([]);
    setDoctorProfile(null);
    setDoctorReport(null);
    setLoading(false);
  };

  if (!user) {
    if (loading && localStorage.getItem("clinic-access-token")) {
      return <main className="auth-page"><section className="panel auth-panel"><p role="status">Restoring your session...</p></section></main>;
    }
    return <><Notice notice={error} /><AuthGate onAuthenticated={authenticated} /></>;
  }

  return (
    <div className="app">
      <header className="masthead app-header">
        <div>
          <p className="eyebrow">CLINIC DESK</p>
          <h1>{user.role === "doctor" ? "Doctor dashboard" : "Find your doctor"}</h1>
          <p>{user.role === "doctor" ? `Welcome, ${user.name}. Manage your practice and review your reports.` : "Browse specialists, find a suitable time, and confirm your appointment securely."}</p>
        </div>
        <div className="account-bar">
          <span>{user.name} <span className="role-chip">{user.role}</span></span>
          <button type="button" className="link-button" onClick={signOut}>Sign out</button>
        </div>
      </header>
      <Notice notice={error} />
      {user.role === "patient" ? (
        <main className="layout">
          <DoctorList doctors={doctors} selectedId={doctorId} onSelect={setDoctorId} loading={loading} />
          <BookingForm
            doctors={doctors}
            doctorId={doctorId}
            onDoctorChange={setDoctorId}
            slotMinutes={slotMinutes}
            refreshKey={refreshKey}
            user={user}
            onBooked={changed}
          />
          <AppointmentList appointments={appointments} doctors={doctors} loading={loading} role={user.role} onChanged={changed} />
        </main>
      ) : (
        <main className="doctor-layout">
          <DoctorDashboard profile={doctorProfile} report={doctorReport} slotMinutes={slotMinutes} onChanged={changed} />
          <AppointmentList appointments={appointments} doctors={doctors} loading={loading} role={user.role} onChanged={changed} />
        </main>
      )}
    </div>
  );
}
