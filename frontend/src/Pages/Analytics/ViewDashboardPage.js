import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ViewDashboardRequest from "../../Components/Requests/ViewDashboardRequest";

const ViewDashboardPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "View Dashboard";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>View Dashboard</h1>
        <ViewDashboardRequest />
        </div>
    );
}

export default ViewDashboardPage;