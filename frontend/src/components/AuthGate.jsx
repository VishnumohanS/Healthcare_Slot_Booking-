import { useState } from "react";
import { describeError, login, register } from "../api/client";
import Notice from "./Notice";

export default function AuthGate({ onAuthenticated }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [role, setRole] = useState("patient");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [fields, setFields] = useState({
    username: "", password: "", name: "", specialization: "",
    start_hour: "9", end_hour: "17", fee: "500",
  });

  const change = (event) => setFields((current) => ({ ...current, [event.target.name]: event.target.value }));

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const payload = {
        username: fields.username,
        password: fields.password,
      };
      const session = isRegistering
        ? await register({
            ...payload,
            name: fields.name,
            role,
            ...(role === "doctor" ? {
              specialization: fields.specialization,
              start_hour: Number(fields.start_hour),
              end_hour: Number(fields.end_hour),
              fee_paise: Math.round(Number(fields.fee) * 100),
            } : {}),
          })
        : await login(payload);
      onAuthenticated(session);
    } catch (error) {
      setNotice({ type: "error", text: describeError(error) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="panel auth-panel" aria-labelledby="auth-title">
        <p className="eyebrow">CLINIC DESK</p>
        <h1 id="auth-title">{isRegistering ? "Create your account" : "Welcome back"}</h1>
        <p className="muted">{isRegistering ? "Register as a patient or a doctor." : "Sign in to manage bookings and appointments."}</p>
        <Notice notice={notice} />
        <form onSubmit={submit} className="auth-form">
          {isRegistering && (
            <>
              <div className="field">
                <label htmlFor="role">Account type</label>
                <select id="role" value={role} onChange={(event) => setRole(event.target.value)}>
                  <option value="patient">Patient</option>
                  <option value="doctor">Doctor</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="name">{role === "doctor" ? "Doctor name" : "Full name"}</label>
                <input id="name" name="name" type="text" required maxLength={100} value={fields.name} onChange={change} />
              </div>
            </>
          )}
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              minLength={3}
              maxLength={50}
              placeholder={isRegistering ? "e.g. john or john@example.com" : "Username or email"}
              value={fields.username}
              onChange={change}
            />
            {isRegistering && <p className="muted">Allowed: letters, numbers, @, ., _, -, + (no spaces).</p>}
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" autoComplete={isRegistering ? "new-password" : "current-password"} required minLength={isRegistering ? 8 : 1} maxLength={128} value={fields.password} onChange={change} />
            {isRegistering && <p className="muted">Use at least 8 characters.</p>}
          </div>
          {isRegistering && role === "doctor" && (
            <>
              <div className="field">
                <label htmlFor="specialization">Specialization</label>
                <input id="specialization" name="specialization" type="text" required maxLength={100} value={fields.specialization} onChange={change} />
              </div>
              <div className="field-row">
                <div className="field">
                  <label htmlFor="start_hour">Work starts</label>
                  <input id="start_hour" name="start_hour" type="number" min="0" max="23" required value={fields.start_hour} onChange={change} />
                </div>
                <div className="field">
                  <label htmlFor="end_hour">Work ends</label>
                  <input id="end_hour" name="end_hour" type="number" min="1" max="24" required value={fields.end_hour} onChange={change} />
                </div>
              </div>
              <div className="field">
                <label htmlFor="fee">Consultation fee (INR)</label>
                <input id="fee" name="fee" type="number" min="1" step="0.01" required value={fields.fee} onChange={change} />
              </div>
            </>
          )}
          <button className="primary auth-submit" type="submit" disabled={busy}>
            {busy ? "Please wait..." : isRegistering ? "Create account" : "Sign in"}
          </button>
        </form>
        <p className="auth-switch">
          {isRegistering ? "Already registered?" : "New to Clinic Desk?"}{" "}
          <button type="button" className="link-button" onClick={() => { setIsRegistering((value) => !value); setNotice(null); }}>
            {isRegistering ? "Sign in" : "Create an account"}
          </button>
        </p>
      </section>
    </main>
  );
}
