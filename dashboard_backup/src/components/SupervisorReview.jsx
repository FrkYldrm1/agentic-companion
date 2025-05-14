import React, { useEffect, useState } from "react";
import { getFlaggedResponses, resolveFlag } from "../services/api";
import "../styles/style.css";

const SupervisorReview = () => {
    const [flags, setFlags] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editedResponses, setEditedResponses] = useState({});
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getFlaggedResponses();
                const unique = data.filter((f) => f.status === "pending");
                setFlags(unique);
            } catch (err) {
                setError("❌ Failed to fetch flagged responses.");
            }
            setLoading(false);
        };
        fetchData();
    }, []);

    const handleEditChange = (id, value) => {
        setEditedResponses((prev) => ({ ...prev, [id]: value }));
    };

    const handleAction = async (flag, action) => {
        const replacement = editedResponses[flag.id];

        if (action === "edited" && (!replacement || replacement.trim() === "")) {
            alert("✏️ Please enter a revised response.");
            return;
        }

        try {
            await resolveFlag(flag.id, action, replacement);
            setFlags(flags.filter((f) => f.id !== flag.id));
        } catch (err) {
            console.error("❌ Failed to resolve flag:", err);
        }
    };

    return (
        <div className="card-list">
            {loading ? (
                <p>Loading flagged responses...</p>
            ) : flags.length === 0 ? (
                <p>No flagged responses pending.</p>
            ) : (
                flags.map((flag) => (
                    <div key={flag.id} className="dashboard-card stat-yellow">
                        <p><strong>User ID:</strong> {flag.user_id || "–"}</p>
                        <p><strong>Input:</strong> {flag.input_text}</p>
                        <p><strong>Response:</strong> {flag.response_text}</p>
                        <p><strong>Reason:</strong> {flag.reason}</p>
                        <p><strong>Confidence:</strong> {flag.confidence_score?.toFixed(2)}</p>
                        <p><strong>Time:</strong> {new Date(flag.timestamp).toLocaleString()}</p>

                        <textarea
                            className="edit-box"
                            rows={3}
                            placeholder="Edit response before sending..."
                            value={editedResponses[flag.id] || flag.response_text}
                            onChange={(e) => handleEditChange(flag.id, e.target.value)}
                        />

                        <div className="flag-actions">
                            <button className="button-green" onClick={() => handleAction(flag, "approved")}>✅ Approve</button>
                            <button className="button-blue" onClick={() => handleAction(flag, "edited")}>✏️ Edit</button>
                            <button className="button-red" onClick={() => handleAction(flag, "rejected")}>❌ Reject</button>
                        </div>
                    </div>
                ))
            )}
            {error && <p className="form-message">{error}</p>}
        </div>
    );
};

export default SupervisorReview;
