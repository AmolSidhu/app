import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import YoutubePlaylistsRequest from "../../Components/Requests/YoutubePlaylistsRequset";
import CreateYoutubePlaylistPopup from "../../Components/Popups/CreateYoutubePlaylistPopup";
import UploadYoutubeVideoPopup from "../../Components/Popups/UploadYoutubeVideoPopup";

const MyYoutubeListsPage = () => {
    const [showUploadPopup, setShowUploadPopup] = useState(false);
    const [showCreatePlaylistPopup, setShowCreatePlaylistPopup] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "My Youtube Lists";
        }
    }, []);

    return (
        <div>
            <MainNavbar />

            <div style={{ margin: "20px" }}>
                <button onClick={() => setShowCreatePlaylistPopup(true)}>Create Playlist</button>
                <button onClick={() => setShowUploadPopup(true)} style={{ marginLeft: "10px" }}>Upload Video</button>
            </div>

            {showCreatePlaylistPopup && (
                <CreateYoutubePlaylistPopup onClose={() => setShowCreatePlaylistPopup(false)} />
            )}

            {showUploadPopup && (
                <UploadYoutubeVideoPopup onClose={() => setShowUploadPopup(false)} />
            )}
            
            <YoutubePlaylistsRequest />
        </div>
    );
}

export default MyYoutubeListsPage;
