import React, { useState } from "react";
import server from '../Static/Constants';

const CreateYoutubePlaylistPopup = ({ onClose }) => {
    const [playlistTitle, setPlaylistTitle] = useState("");
    const [playlistDescription, setPlaylistDescription] = useState("");
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleCreatePlaylist = async () => {
        setErrorMessage(null);
        setSuccessMessage(null);

        if (!playlistTitle || !playlistDescription) {
            setErrorMessage("Please fill in all fields.");
            return;
        }

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/create/youtube_playlist/`, {
                method: "POST",
                headers: {
                    "Authorization": token,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: playlistTitle,
                    description: playlistDescription,
                })
            });

            if (response.ok) {
                setSuccessMessage("Playlist created successfully!");
                setPlaylistTitle("");
                setPlaylistDescription("");
            } else {
                const errorData = await response.json();
                setErrorMessage(errorData.message || "An error occurred during playlist creation.");
            }
        } catch (error) {
            console.error("Error creating playlist:", error);
            setErrorMessage("An error occurred during playlist creation.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Create YouTube Playlist</h2>
                
                {errorMessage && <p className="error-message" style={{ color: "red" }}>{errorMessage}</p>}
                {successMessage && <p className="success-message" style={{ color: "green" }}>{successMessage}</p>}
                
                <input
                    type="text"
                    placeholder="Playlist Title"
                    value={playlistTitle}
                    onChange={(e) => setPlaylistTitle(e.target.value)}
                />
                <textarea
                    placeholder="Playlist Description"
                    value={playlistDescription}
                    onChange={(e) => setPlaylistDescription(e.target.value)}
                />
                <button onClick={handleCreatePlaylist}>Create Playlist</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </div>
    );
};

export default CreateYoutubePlaylistPopup;
