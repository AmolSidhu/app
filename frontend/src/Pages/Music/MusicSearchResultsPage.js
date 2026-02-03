import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const NusicSearchResultsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Music Search Results";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <div>
                <h2>Music Search Results Page</h2>
            </div>
        </div>
    );
}

export default NusicSearchResultsPage;