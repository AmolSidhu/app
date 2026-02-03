import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const ViewAllArtistsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "View All Music Artists";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <div>
                <h2>View All Music Artists Page</h2>
            </div>
        </div>
    );
}

export default ViewAllArtistsPage;