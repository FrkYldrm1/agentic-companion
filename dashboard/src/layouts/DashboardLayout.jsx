import React from "react";
import "../styles/style.css";

const DashboardLayout = ({ view, setView, children }) => {
    return (
        <div className="layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-title">👩‍⚕️ Agentic Companion Dashboard</div>
                <nav className="sidebar-nav">
                    <button
                        onClick={() => setView("dashboard")}
                        className={`nav-button ${view === "dashboard" ? "active" : ""}`}
                    >
                        📊 Dashboard
                    </button>
                    <button
                        onClick={() => setView("users")}
                        className={`nav-button ${view === "users" ? "active" : ""}`}
                    >
                        👥 Users
                    </button>
                    <button
                        onClick={() => setView("flags")}
                        className={`nav-button ${view === "flags" ? "active" : ""}`}
                    >
                        🚩 Flagged Responses
                    </button>
                </nav>
            </aside>

            {/* Main content area */}
            <main className="main-content">
                <div className="topbar">
                    <div className="topbar-title">Agentic Companion Dashboard</div>
                    <div className="topbar-profile">Supervisor</div>
                </div>
                <div className="main-area">{children}</div>
            </main>
        </div>
    );
};

export default DashboardLayout;