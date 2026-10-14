import { useState } from "react";
import { cancelAppointment, describeError } from "../api/client";
import { dateOf, prettyDate, timeOf } from "../utils/slots";
import Notice from "./Notice";

export default function AppointmentList({ appointments, doctors, loading, role, onChanged }) {
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState(null);
  const doctorById = Object.fromEntries(doctors.map((d) => [d.id, d]));

  const handleCancel = async (appointment) => {
    const doctor = doctorById[appointment.doctor_id];
    const label = appointment.status === "blocked"
      ? `${timeOf(appointment.slot)} blocked slot with ${doctor?.name ?? "you"}`
      : `${appointment.patient_name ?? "Patient"} with ${doctor?.name ?? "the doctor"} on ${prettyDate(dateOf(appointment.slot))} at ${timeOf(appointment.slot)}`;
    if (!window.confirm(`Cancel ${label}?`)) return;
    setBusyId(appointment.id);
    setNotice(null);
    try {
      await cancelAppointment(appointment.id);
      setNotice({ type: "success", text: `Cancelled: ${label}. The time is open again.` });
    } catch (error) {
      setNotice({ type: "error", text: describeError(error) });
    } finally {
      setBusyId(null);
      onChanged();
    }
  };

  return (
    <section className="panel wide" aria-labelledby="appts-heading">
      <h2 id="appts-heading">Upcoming appointments</h2>
      <Notice notice={notice} onDismiss={() => setNotice(null)} />
      {loading && appointments.length === 0 ? (
        <p className="muted" role="status">Loading appointments...</p>
      ) : appointments.length === 0 ? (
        <p className="empty">No appointments are booked. Use the form to add one.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Time</th>
                <th scope="col">{role === "doctor" ? "Patient / slot" : "Appointment"}</th>
                <th scope="col">Doctor</th>
                <th scope="col"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((a) => {
                const doctor = doctorById[a.doctor_id];
                const cancellationTooLate = new Date(a.slot) <= new Date(Date.now() + 2 * 60 * 60 * 1000);
                return (
                  <tr key={a.id}>
                    <td data-label="Date">{prettyDate(dateOf(a.slot))}</td>
                    <td data-label="Time" className="time-cell">{timeOf(a.slot)}</td>
                    <td data-label="Patient">{a.status === "blocked" ? "Blocked by you" : (a.patient_name ?? "—")}</td>
                    <td data-label="Doctor">
                      {doctor ? `${doctor.name} (${doctor.specialization})` : `Doctor #${a.doctor_id}`}
                    </td>
                    <td className="actions">
                      {(role === "doctor" && a.status === "blocked") || (role === "patient" && a.status === "booked" && !cancellationTooLate) ? (
                        <button
                          type="button"
                          className="danger"
                          disabled={busyId === a.id}
                          onClick={() => handleCancel(a)}
                          aria-label={role === "doctor" ? `Unblock slot at ${timeOf(a.slot)}` : `Cancel appointment at ${timeOf(a.slot)}`}
                        >
                          {busyId === a.id ? "Cancelling..." : role === "doctor" ? "Unblock slot" : "Cancel"}
                        </button>
                      ) : role === "patient" && a.status === "booked" && cancellationTooLate ? (
                        <span className="muted">Cancellation closes 2 hours before</span>
                      ) : null}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
