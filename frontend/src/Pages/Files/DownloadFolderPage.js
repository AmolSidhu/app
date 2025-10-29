import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import DownloadFolderRequest from "../../Components/Requests/DownloadFolderRequest";

const DownloadFolderPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        }
        else {
            document.title = "My Downloadable Folders";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>Download Folder</h1>
            <DownloadFolderRequest />
        </div>
    );
}

export default DownloadFolderPage;