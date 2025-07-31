import React, { useEffect } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const UploadShareFilesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Upload & Share Files";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>Upload & Share Files</h1>
        </div>
    );
};

export default UploadShareFilesPage;
