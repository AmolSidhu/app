import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ViewScraperHistoryRequest from "../../Components/Requests/ViewScraperHistoryRequest";

const ViewScraperHistoryPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "View Scraper History";
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <h1>View Scraper History</h1>
            <ViewScraperHistoryRequest />
        </div>
    );
}

export default ViewScraperHistoryPage;