import React, { useState } from 'react';
import server from '../Static/Constants';

const CreateMusicAlbumPopup = ({ onClose }) => {
    const [spotifyLink, setSpotifyLink] = useState("");
    const [appleLink, setAppleLink] = useState("");
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleCreateAlbum = async () => {
        setErrorMessage(null);
        setSuccessMessage(null);

        if (!spotifyLink || !appleLink) {
            setErrorMessage("Please fill in all fields.");
            return;
        }

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/upload/music_links/`, {
                method: "POST",
                headers: {
                    "Authorization": token,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    spotify_link: spotifyLink,
                    apple_link: appleLink,
                })
            });

            if (response.ok) {
                setSuccessMessage("Album created successfully! Album is being processed.");
                setSpotifyLink("");
                setAppleLink("");

            } else {
                const errorData = await response.json();
                setErrorMessage(errorData.message || "An error occurred during album creation.");
            }
        } catch (error) {
            console.error("Error creating album:", error);
            setErrorMessage("An error occurred during album creation.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Create Music Album</h2>

                {errorMessage && <p className="error-message" style={{ color: "red" }}>{errorMessage}</p>}
                {successMessage && <p className="success-message" style={{ color: "green" }}>{successMessage}</p>}

                <input
                    type="text"
                    placeholder="Album Spotify Link"
                    value={spotifyLink}
                    onChange={(e) => setSpotifyLink(e.target.value)}
                />
                <textarea
                    placeholder="Album Apple Music Link"
                    value={appleLink}
                    onChange={(e) => setAppleLink(e.target.value)}
                />
                <button onClick={handleCreateAlbum}>Create Album</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </div>
    );
};

export default CreateMusicAlbumPopup;
