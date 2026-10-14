import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  CategoryScale,
  BarController,
  BarElement,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { blockSlot, describeError, updateDoctorProfile } from "../api/client";
import { toSlotString, todayString } from "../utils/slots";
import Notice from "./Notice";

ChartJS.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function DoctorDashboard({ profile, report, slotMinutes, onChanged }) {
  const [draft, setDraft] = useState(null);
  const [date, setDate] = useState(todayString());
  const [time, setTime] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    if (profile) {
      setDraft({
        name: profile.name,
        specialization: profile.specialization,
        start_hour: profile.start_hour,
        end_hour: profile.end_hour,
        fee: (profile.fee_paise / 100).toFixed(2),
        bio: profile.bio,
      });
    }
  }, [profile]);

  if (!profile || !draft) return <section className="panel"><p className="muted">Loading your doctor dashboard...</p></section>;

  const updateField = (event) => setDraft((current) => ({ ...current, [event.target.name]: event.target.value }));
  const saveProfile = async (event) => {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      await updateDoctorProfile({
        name: draft.name,
        specialization: draft.specialization,
        start_hour: Number(draft.start_hour),
        end_hour: Number(draft.end_hour),
        fee_paise: Math.round(Number(draft.fee) * 100),
        bio: draft.bio,
      });
      setNotice({ type: "success", text: "Your doctor profile and consultation fee were updated." });
      onChanged();
    } catch (error) {
      setNotice({ type: "error", text: describeError(error) });
    } finally {
      setBusy(false);
    }
  };

  const addBlock = async (event) => {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      await blockSlot(toSlotString(date, time));
      setTime("");
      setNotice({ type: "success", text: `Your ${date} ${time} slot is now blocked.` });
      onChanged();
    } catch (error) {
      setNotice({ type: "error", text: describeError(error) });
    } finally {
      setBusy(false);
    }
  };

  const chartData = {
    labels: report?.monthly_bookings?.map((item) => item.month) ?? [],
    datasets: [{
      label: "Confirmed appointments",
      data: report?.monthly_bookings?.map((item) => item.appointments) ?? [],
      backgroundColor: "#79c4b8",
      borderColor: "#147d70",
      borderWidth: 1,
      borderRadius: 6,
    }],
  };

  return (
    <div className="doctor-dashboard">
      <section className="report-grid" aria-label="Appointment summary">
        <article className="metric-card"><span>Confirmed appointments</span><strong>{report?.total_appointments ?? 0}</strong></article>
        <article className="metric-card"><span>Cancelled appointments</span><strong>{report?.cancelled_appointments ?? 0}</strong></article>
        <article className="metric-card"><span>Blocked slots</span><strong>{report?.blocked_slots ?? 0}</strong></article>
        <article className="metric-card"><span>Payments received</span><strong>₹{((report?.revenue_paise ?? 0) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</strong></article>
      </section>
      <section className="panel" aria-labelledby="report-heading">
        <h2 id="report-heading">Booking report</h2>
        <div className="chart-wrap">
          <Bar
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false }, tooltip: { intersect: false } },
              scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            }}
          />
        </div>
      </section>
      <div className="doctor-tools">
        <section className="panel" aria-labelledby="profile-heading">
          <h2 id="profile-heading">Doctor profile</h2>
          <form onSubmit={saveProfile}>
            <div className="field">
              <label htmlFor="profile-name">Name</label>
              <input id="profile-name" name="name" required maxLength={100} value={draft.name} onChange={updateField} />
            </div>
            <div className="field">
              <label htmlFor="specialization">Specialization</label>
              <input id="specialization" name="specialization" required maxLength={100} value={draft.specialization} onChange={updateField} />
            </div>
            <div className="field-row">
              <div className="field">
                <label htmlFor="start-hour">Work starts</label>
                <input id="start-hour" name="start_hour" type="number" min="0" max="23" required value={draft.start_hour} onChange={updateField} />
              </div>
              <div className="field">
                <label htmlFor="end-hour">Work ends</label>
                <input id="end-hour" name="end_hour" type="number" min="1" max="24" required value={draft.end_hour} onChange={updateField} />
              </div>
            </div>
            <div className="field">
              <label htmlFor="fee">Consultation fee (INR)</label>
              <input id="fee" name="fee" type="number" min="1" step="0.01" required value={draft.fee} onChange={updateField} />
            </div>
            <div className="field">
              <label htmlFor="bio">About you</label>
              <textarea id="bio" name="bio" rows="3" maxLength={2000} value={draft.bio} onChange={updateField} />
            </div>
            <button className="primary" disabled={busy}>Save profile</button>
          </form>
        </section>
        <section className="panel" aria-labelledby="block-heading">
          <h2 id="block-heading">Block personal time</h2>
          <p className="muted">Block an open slot for a break or other unavailability.</p>
          <form onSubmit={addBlock}>
            <div className="field">
              <label htmlFor="block-date">Date</label>
              <input id="block-date" type="date" min={todayString()} value={date} required onChange={(event) => setDate(event.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="block-time">Start time</label>
              <input id="block-time" type="time" step={slotMinutes * 60} required value={time} onChange={(event) => setTime(event.target.value)} />
            </div>
            <p className="muted">This blocks one appointment-length slot.</p>
            <button className="primary" disabled={busy || !time}>Block slot</button>
          </form>
        </section>
      </div>
      <Notice notice={notice} onDismiss={() => setNotice(null)} />
    </div>
  );
}
