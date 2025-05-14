import React, { useState } from "react";
import DashboardLayout from "./layouts/DashboardLayout";
import UsersPage from "./pages/UsersPage";
import GovernanceDashboard from "./pages/GovernanceDashboard";
import DashboardPage from "./pages/DashboardPage";
import './styles/style.css';



function App() {
  const [view, setView] = useState("dashboard");

  const renderPage = () => {
    switch (view) {
      case "dashboard":
        return <DashboardPage />;
      case "users":
        return <UsersPage />;
      case "flags":
        return <GovernanceDashboard />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <DashboardLayout view={view} setView={setView}>
      {renderPage()}
    </DashboardLayout>
  );
}

export default App;
