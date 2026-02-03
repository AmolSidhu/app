import React, { useState } from "react";
import server from "../Static/Constants";

const UploadYoutubeVideoToPlaylistPopup = ({ playlistSerial, onClose }) => {
    const [videoUrl, setVideoUrl] = useState("");
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
            return;
        }

        if (!videoUrl) {
            setErrorMessage("YouTube URL is required.");
            return;
        }

        setLoading(true);
        setErrorMessage(null);
        setSuccessMessage(null);

        try {
            const res = await fetch(`${server}/upload/youtube_video/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: token
                },
                body: JSON.stringify({
                    youtube_link: videoUrl,
                    add_to_playlists: [playlistSerial]
                })
            });

            const data = await res.json();

            if (!res.ok) {
                setErrorMessage(data.message || "Upload failed.");
                return;
            }

            setSuccessMessage("YouTube video upload started successfully.");
            setVideoUrl("");
        } catch (err) {
            console.error("Upload error:", err);
            setErrorMessage("An unexpected error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h3>Add YouTube Video to Playlist</h3>

                {errorMessage && <p className="error-message">{errorMessage}</p>}
                {successMessage && <p className="success-message">{successMessage}</p>}

                <input
                    type="text"
                    placeholder="YouTube video URL"
                    value={videoUrl}
                    onChange={e => setVideoUrl(e.target.value)}
                    style={{ width: "100%", marginBottom: "1rem" }}
                />

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "1rem" }}>
                    <button onClick={onClose} disabled={loading}>
                        Cancel
                    </button>
                    <button onClick={handleSubmit} disabled={loading}>
                        {loading ? "Uploading..." : "Upload"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UploadYoutubeVideoToPlaylistPopup;
