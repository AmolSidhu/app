import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ViewMyDashboardsRequest from "../../Components/Requests/ViewMyDashbaordsRequest";
import CreateDashboardPopup from "../../Components/Popups/CreateDashboardPopup";

const MyDashboardsPage = () => {
  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "My Dashboards";
    }
  }, []);

  return (
    <div>
      <MainNavbar />

      <div style={{ padding: "20px" }}>
        <button onClick={() => setShowPopup(true)}>
          + Create Dashboard
        </button>
      </div>

      {showPopup && (
        <CreateDashboardPopup onClose={() => setShowPopup(false)} />
      )}

      <section style={{ padding: "20px" }}>
        <ViewMyDashboardsRequest />
      </section>
    </div>
  );
};

export default MyDashboardsPage;
