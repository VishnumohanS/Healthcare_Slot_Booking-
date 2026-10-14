const pad = (n) => String(n).padStart(2, "0");

export const formatTime = (minutesFromMidnight) =>
  `${pad(Math.floor(minutesFromMidnight / 60) % 24)}:${pad(minutesFromMidnight % 60)}`;

export const formatHour = (hour) => `${pad(hour % 24)}:00`;

/** Every slot start ("HH:MM") for a doctor: the whole appointment must end by end_hour. */
export function generateSlots(doctor, durationMinutes) {
  const slots = [];
  for (let m = doctor.start_hour * 60; m + durationMinutes <= doctor.end_hour * 60; m += durationMinutes) {
    slots.push(formatTime(m));
  }
  return slots;
}

/** Appointment slot strings from the API ("2030-10-20T09:30:00") -> "09:30" */
export const timeOf = (isoSlot) => isoSlot.slice(11, 16);
export const dateOf = (isoSlot) => isoSlot.slice(0, 10);

export const toSlotString = (date, time) => `${date}T${time}:00`;

export function todayString() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function prettyDate(isoDate) {
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString(undefined, {
    weekday: "short", day: "numeric", month: "short", year: "numeric",
  });
}
