import { useCallback, useEffect, useMemo, useState } from "react";
import {
  cancelPaymentOrder,
  createPaymentOrder,
  describeError,
  getDoctorAvailability,
  verifyPayment,
} from "../api/client";
import usePolling from "../hooks/usePolling";
import { formatHour, generateSlots, prettyDate, timeOf, toSlotString, todayString } from "../utils/slots";
import Notice from "./Notice";

const SCRIPT_URL = "https://checkout.razorpay.com/v1/checkout.js";

function loadRazorpay() {
  if (window.Razorpay) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.querySelector(`script[src="${SCRIPT_URL}"]`) || document.createElement("script");
    script.src = SCRIPT_URL;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Could not load Razorpay Checkout. Check your internet connection and try again."));
    if (!script.isConnected) document.body.appendChild(script);
  });
}

export default function BookingForm({ doctors, doctorId, onDoctorChange, slotMinutes, refreshKey, user, onBooked }) {
  const [date, setDate] = useState(todayString());
  const [slot, setSlot] = useState("");
  const [taken, setTaken] = useState(new Set());
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  const doctor = useMemo(() => doctors.find((item) => item.id === doctorId), [doctors, doctorId]);
  const allSlots = useMemo(() => {
    if (!doctor) return [];
    return generateSlots(doctor, slotMinutes).filter((time) => {
      if (date !== todayString()) return true;
      const [hour, minute] = time.split(":").map(Number);
      const now = new Date();
      return hour * 60 + minute > now.getHours() * 60 + now.getMinutes();
    });
  }, [doctor, date, slotMinutes]);

  const loadAvailability = useCallback(async () => {
    if (!doctorId || !date) return;
    try {
      const result = await getDoctorAvailability(doctorId, date);
      setTaken(new Set(result.occupied.map(timeOf)));
      setNotice((current) => current?.type === "error" ? null : current);
    } catch (error) {
      setNotice({ type: "error", text: describeError(error) });
    } finally {
      setLoadingSlots(false);
    }
  }, [doctorId, date]);

  useEffect(() => {
    setLoadingSlots(true);
    setSlot("");
    loadAvailability();
  }, [loadAvailability, refreshKey]);
  usePolling(loadAvailability, 15000);

  useEffect(() => {
    if (slot && taken.has(slot)) setSlot("");
  }, [taken, slot]);

  const startCheckout = async (order) => {
    await loadRazorpay();
    return new Promise((resolve, reject) => {
      let handled = false;
      const checkout = new window.Razorpay({
        key: order.key_id,
        amount: order.amount_paise,
        currency: order.currency,
        name: "Clinic Desk",
        description: `Appointment with ${order.doctor_name}`,
        order_id: order.order_id,
        prefill: { name: user.name },
        theme: { color: "#147d70" },
        handler: (result) => {
          if (handled) return;
          handled = true;
          verifyPayment({
            appointment_id: order.appointment_id,
            razorpay_order_id: result.razorpay_order_id,
            razorpay_payment_id: result.razorpay_payment_id,
            razorpay_signature: result.razorpay_signature,
          }).then(() => resolve("paid")).catch(reject);
        },
        modal: {
          ondismiss: () => {
            if (handled) return;
            handled = true;
            resolve("dismissed");
          },
        },
      });
      checkout.on("payment.failed", (event) => {
        if (handled) return;
        handled = true;
        reject(new Error(event.error?.description || "Payment failed. Please try again."));
      });
      checkout.open();
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setNotice(null);
    const errors = {};
    if (!doctorId) errors.doctor = "Choose a doctor.";
    if (!date) errors.date = "Choose a date.";
    if (!slot) errors.slot = "Pick an available time.";
    setFieldErrors(errors);
    if (Object.keys(errors).length) return;

    setSubmitting(true);
    let order;
    try {
      order = await createPaymentOrder({ doctor_id: doctorId, slot: toSlotString(date, slot) });
      const outcome = await startCheckout(order);
      if (outcome === "dismissed") {
        await cancelPaymentOrder(order.appointment_id);
        setNotice({ type: "error", text: "Checkout was closed. No appointment was confirmed." });
      } else {
        setNotice({
          type: "success",
          text: `Payment confirmed. Your appointment with ${doctor.name} is booked for ${prettyDate(date)} at ${slot}.`,
        });
        setSlot("");
      }
    } catch (error) {
      if (order) {
        try {
          await cancelPaymentOrder(order.appointment_id);
        } catch (cancelError) {
          if (cancelError.response?.status !== 404 && cancelError.response?.status !== 409) {
            setNotice({ type: "error", text: `${error.response ? describeError(error) : error.message || describeError(error)} The pending slot could not be released automatically.` });
            return;
          }
        }
      }
      setNotice({ type: "error", text: error.response ? describeError(error) : error.message || describeError(error) });
    } finally {
      setSubmitting(false);
      loadAvailability();
      onBooked();
    }
  };

  const freeCount = allSlots.filter((time) => !taken.has(time)).length;

  return (
    <section className="panel" aria-labelledby="booking-heading">
      <h2 id="booking-heading">Book an appointment</h2>
      <p className="muted">Choose a doctor and pay their consultation fee securely to confirm your slot.</p>
      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="doctor">Doctor</label>
          <select id="doctor" value={doctorId ?? ""} onChange={(event) => onDoctorChange(event.target.value ? Number(event.target.value) : null)}>
            <option value="">Select a doctor</option>
            {doctors.map((item) => (
              <option key={item.id} value={item.id}>{item.name} — {item.specialization}</option>
            ))}
          </select>
          {fieldErrors.doctor && <p className="field-error">{fieldErrors.doctor}</p>}
        </div>

        {doctor && (
          <div className="doctor-fee">
            <strong>{doctor.name}</strong><span>{doctor.specialization}</span>
            <strong>₹{(doctor.fee_paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</strong>
            {doctor.bio && <p>{doctor.bio}</p>}
          </div>
        )}

        <div className="field">
          <label htmlFor="date">Appointment date</label>
          <input id="date" type="date" value={date} min={todayString()} onChange={(event) => setDate(event.target.value)} />
          {fieldErrors.date && <p className="field-error">{fieldErrors.date}</p>}
        </div>

        <fieldset className="slots">
          <legend>Available times</legend>
          {!doctor ? (
            <p className="empty">Select a doctor to see their open times.</p>
          ) : loadingSlots ? (
            <p className="muted" role="status">Checking availability...</p>
          ) : (
            <>
              <p className="muted">
                {formatHour(doctor.start_hour)}–{formatHour(doctor.end_hour)} · {slotMinutes}-minute slots · {freeCount} open
              </p>
              <div className="slot-grid">
                {allSlots.map((time) => {
                  const isTaken = taken.has(time);
                  return (
                    <label key={time} className={`slot${isTaken ? " is-taken" : ""}${slot === time ? " is-chosen" : ""}`}>
                      <input type="radio" name="slot" value={time} checked={slot === time} disabled={isTaken} onChange={() => setSlot(time)} />
                      <span>{time}</span>
                    </label>
                  );
                })}
              </div>
              {allSlots.length === 0 && <p className="muted">No future slots are available on this date.</p>}
            </>
          )}
          {fieldErrors.slot && <p className="field-error">{fieldErrors.slot}</p>}
        </fieldset>
        <button type="submit" className="primary" disabled={submitting || loadingSlots}>
          {submitting ? "Opening secure checkout..." : "Pay and confirm slot"}
        </button>
      </form>
      <Notice notice={notice} onDismiss={() => setNotice(null)} />
    </section>
  );
}
