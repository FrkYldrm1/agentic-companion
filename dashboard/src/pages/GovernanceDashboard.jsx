import React from "react";
import SupervisorReview from "../components/SupervisorReview";
import "../styles/style.css";

const GovernanceDashboard = () => {
    return (
        <div className="page-container">
            <div className="section-header">
                <h2>🚩 Flagged Responses</h2>
                <p>These are responses flagged by the governance system.</p>
            </div>
            <SupervisorReview />
        </div>
    );
};

export default GovernanceDashboard;
