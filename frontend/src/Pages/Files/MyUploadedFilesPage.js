import React, { useEffect } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const MyUploadedFilesPage = () => {
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
            <h1>My Uploaded Files</h1>
        </div>
    );
}

export default MyUploadedFilesPage;