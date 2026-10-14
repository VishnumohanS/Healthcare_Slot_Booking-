export default function Notice({ notice, onDismiss }) {
  if (!notice) return null;
  const isError = notice.type === "error";
  return (
    <div className={`notice notice-${notice.type}`} role={isError ? "alert" : "status"}>
      <span>{notice.text}</span>
      {onDismiss && (
        <button type="button" className="link-button" onClick={onDismiss} aria-label="Dismiss message">
          Dismiss
        </button>
      )}
    </div>
  );
}
