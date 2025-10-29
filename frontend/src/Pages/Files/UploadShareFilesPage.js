import React, { useEffect } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import FileShareSwitch from "../../Components/Static/FileShareSwitch";

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
            <FileShareSwitch />
        </div>
    );
};

export default UploadShareFilesPage;