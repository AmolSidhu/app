import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const CreateDashboardPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Create Dashboard";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Create Dashboard</h1>
        </div>
    );
}

export default CreateDashboardPage;