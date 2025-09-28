import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import DownloadFileRequest from "../../Components/Requests/DownloadFileRequest";

const DownloadFilePage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "My Uploaded Files";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>Download File</h1>
            <DownloadFileRequest />
        </div>
    );
}

export default DownloadFilePage;