import React, { useEffect } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ViewAllShareFolderFilesRequest from "../../Components/Requests/ViewAllShareFolderFilesRequest";

const ViewFolderShareFilesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "View Folder Shared Files";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>View Folder Shared Files</h1>
            <ViewAllShareFolderFilesRequest />
        </div>
    );
}

export default ViewFolderShareFilesPage;