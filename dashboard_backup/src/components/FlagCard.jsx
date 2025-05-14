import React from "react";

const FlagCard = ({ flag, value, onChange, onAction }) => {
    const formattedTime = new Date(flag.timestamp).toLocaleString();

    return (
        <div className="flag-card">
            {/* Response Block */}
            <div className="flag-block">
                <div className="flag-label">💬 Response:</div>
                <pre className="flag-text">{flag.response_text}</pre>
            </div>

            {/* User Input Block */}
            <div className="flag-block">
                <div className="flag-label">🙋 Input:</div>
                <pre className="flag-text">{flag.input_text}</pre>
            </div>

            {/* Reason + Confidence */}
            <div className="flag-block">
                <strong>🛑 Reason:</strong> {flag.reason} &nbsp;&nbsp;
                <strong>📊 Confidence:</strong> {flag.confidence_score?.toFixed(2) || "–"}
            </div>

            {/* Timestamp */}
            <div className="flag-block">
                <strong>🕓 Time:</strong> {formattedTime}
            </div>

            {/* Editable box */}
            <textarea
                className="edit-box"
                rows={3}
                placeholder="Edit response before sending..."
                value={value}
                onChange={(e) => onChange(flag.id, e.target.value)}
            />

            {/* Action buttons */}
            <div className="flag-actions">
                <button className="button-green" onClick={() => onAction(flag, "approved")}>
                    ✅ Approve
                </button>
                <button className="button-blue" onClick={() => onAction(flag, "edited")}>
                    ✏️ Edit
                </button>
                <button className="button-red" onClick={() => onAction(flag, "rejected")}>
                    ❌ Reject
                </button>
            </div>
        </div>
    );
};

export default FlagCard;
