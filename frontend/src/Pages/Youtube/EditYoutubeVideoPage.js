import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const EditYoutubeVideoPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Edit Youtube Video";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <div>
                <h2>Edit Youtube Video Page</h2>
            </div>
        </div>
    );
}

export default EditYoutubeVideoPage;