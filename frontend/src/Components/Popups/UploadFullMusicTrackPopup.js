import React, { useState } from "react";
import server from "../Static/Constants";

const UploadFullMusicTrackPopup = ({ album, track, onClose }) => {
    const [file, setFile] = useState(null);
    const [youtubeLink, setYoutubeLink] = useState("");
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    const handleUpload = async () => {
        const token = localStorage.getItem("token");
        const formData = new FormData();

        formData.append("track_serial", track.track_serial);

        if (file) formData.append("track_file", file);
        if (youtubeLink) formData.append("youtube_link", youtubeLink);

        try {
            const response = await fetch(
                `${server}/add_full_track/${track.track_serial}/`,
                {
                    method: "POST",
                    headers: { Authorization: token },
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                setError(data.message || "Upload failed");
            } else {
                setMessage("Full song added successfully!");
            }
        } catch (err) {
            console.error(err);
            setError("An error occurred during upload.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="close-button" onClick={onClose}>X</button>

                <h3>
                    Upload Full Track for {track.track_name} from Album {album.album_name}
                </h3>

                {error && <p style={{ color: "red" }}>{error}</p>}
                {message && <p style={{ color: "green" }}>{message}</p>}

                <div>
                    <label>Upload MP3 File:</label>
                    <input
                        type="file"
                        accept="audio/*"
                        onChange={(e) => setFile(e.target.files[0])}
                    />
                </div>

                <div>
                    <label>YouTube Link (optional):</label>
                    <input
                        type="text"
                        value={youtubeLink}
                        onChange={(e) => setYoutubeLink(e.target.value)}
                        placeholder="https://youtube.com/..."
                    />
                </div>

                <button onClick={handleUpload} className="upload-button">
                    Submit Full Track
                </button>
            </div>
        </div>
    );
};

export default UploadFullMusicTrackPopup;
