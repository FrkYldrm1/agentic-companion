import React, { useEffect, useState } from "react";
import "../styles/dashboard.css";
import { fetchUserCount, fetchPendingFlagCount } from "../services/api";

const DashboardPage = () => {
    const [userCount, setUserCount] = useState(0);
    const [flagCount, setFlagCount] = useState(0);
    const activeSessions = 5; // placeholder

    useEffect(() => {
        fetchUserCount().then(setUserCount).catch(console.error);
        fetchPendingFlagCount().then(setFlagCount).catch(console.error);
    }, []);

    const metrics = [
        { title: "Users", count: userCount, icon: "👥", bg: "stat-green" },
        { title: "Pending Flags", count: flagCount, icon: "🚩", bg: "stat-yellow" },
        { title: "Active Sessions", count: activeSessions, icon: "💬", bg: "stat-blue" },
    ];

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h2 className="dashboard-title">👋 Welcome back</h2>
            </div>

            <div className="dashboard-grid">
                {metrics.map((m) => (
                    <div key={m.title} className={`dashboard-card ${m.bg}`}>
                        <div className="dashboard-card-icon">{m.icon}</div>
                        <div className="dashboard-card-info">
                            <p className="dashboard-card-title">{m.title}</p>
                            <p className="dashboard-card-count">{m.count}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DashboardPage;
