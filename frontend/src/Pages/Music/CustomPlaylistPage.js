import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const CustomPlaylistPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Custom Music Playlist";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <div>
                <h2>Custom Music Playlist Page</h2>
            </div>
        </div>
    );
}

export default CustomPlaylistPage;