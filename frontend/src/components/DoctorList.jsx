import { formatHour } from "../utils/slots";

export default function DoctorList({ doctors, selectedId, onSelect, loading }) {
  return (
    <section className="panel" aria-labelledby="doctors-heading">
      <h2 id="doctors-heading">Doctors</h2>
      {loading && doctors.length === 0 ? (
        <p className="muted" role="status">Loading doctors...</p>
      ) : doctors.length === 0 ? (
        <p className="empty">No doctors yet. Seed the database or add one through the API.</p>
      ) : (
        <ul className="doctor-list">
          {doctors.map((doctor) => {
            const selected = doctor.id === selectedId;
            return (
              <li key={doctor.id}>
                <button
                  type="button"
                  className={`doctor-card${selected ? " is-selected" : ""}`}
                  aria-pressed={selected}
                  onClick={() => onSelect(doctor.id)}
                >
                  <span className="doctor-name">{doctor.name}</span>
                  <span className="doctor-spec">{doctor.specialization}</span>
                  <span className="doctor-hours">
                    {formatHour(doctor.start_hour)} - {formatHour(doctor.end_hour)}
                  </span>
                  <span className="doctor-fee-label">
                    ₹{(doctor.fee_paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
