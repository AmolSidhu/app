import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ViewAllScrapersRequest from "../../Components/Requests/ViewAllScrapersRequest";

const ViewScrapersPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "View Scrapers";
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <h1>View Scrapers</h1>
            <ViewAllScrapersRequest />
        </div>
    );
}

export default ViewScrapersPage;