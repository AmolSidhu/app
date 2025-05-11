import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import MyVideoRequestsRequest from "../../Components/Requests/MyVideoRequestsRequest";

const ViewMyVideoRequestsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "My Video Request";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>View My Video Requests</h1>
        <MyVideoRequestsRequest />
        </div>
    );
}

export default ViewMyVideoRequestsPage;