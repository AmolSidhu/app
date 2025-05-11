import React, { useState, useEffect } from "react";
import server from "../Static/Constants";

const UploadYoutubeVideoPopup = ({ onClose }) => {
    const [videoUrl, setVideoUrl] = useState("");
    const [videoTitle, setVideoTitle] = useState("");
    const [videoDescription, setVideoDescription] = useState("");
    const [playlists, setPlaylists] = useState([]);
    const [selectedPlaylists, setSelectedPlaylists] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);

    useEffect(() => {
        const fetchPlaylists = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}/get/youtube_playlists/`, {
                    headers: {
                        "Authorization": token
                    }
                });

                const data = await response.json();
                if (response.ok) {
                    setPlaylists(data.data || []);
                } else {
                    setErrorMessage(data.message || "Failed to fetch playlists.");
                }
            } catch (error) {
                console.error("Error fetching playlists:", error);
                setErrorMessage("An error occurred while loading playlists.");
            }
        };

        fetchPlaylists();
    }, []);

    const handleUpload = async () => {
        if (!videoUrl || !videoTitle || !videoDescription) {
            setErrorMessage("Please fill in all fields.");
            return;
        }

        const payload = {
            youtube_link: videoUrl,
            video_title: videoTitle,
            video_description: videoDescription,
            add_to_playlists: selectedPlaylists,
        };

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/upload/youtube_video/`, {
                method: "POST",
                headers: {
                    "Authorization": token,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const responseData = await response.json();
            if (response.ok) {
                alert("Video uploaded successfully!");
                onClose();
            } else {
                setErrorMessage(responseData.message || "An error occurred during upload.");
            }
        } catch (error) {
            console.error("Error uploading video:", error);
            setErrorMessage("An error occurred during upload.");
        }
    };

    const togglePlaylistSelection = (serial) => {
        setSelectedPlaylists((prev) =>
            prev.includes(serial)
                ? prev.filter((item) => item !== serial)
                : [...prev, serial]
        );
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Upload YouTube Video</h2>
                {errorMessage && <p className="error-message">{errorMessage}</p>}
                <input
                    type="text"
                    placeholder="Video URL"
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Video Title"
                    value={videoTitle}
                    onChange={(e) => setVideoTitle(e.target.value)}
                />
                <textarea
                    placeholder="Video Description"
                    value={videoDescription}
                    onChange={(e) => setVideoDescription(e.target.value)}
                ></textarea>

                <div className="playlist-section">
                    <label>Select Playlists:</label>
                    <div className="playlist-options">
                        {playlists.map((playlist) => (
                            <div key={playlist.serial}>
                                <input
                                    type="checkbox"
                                    id={`playlist-${playlist.serial}`}
                                    value={playlist.serial}
                                    checked={selectedPlaylists.includes(playlist.serial)}
                                    onChange={() => togglePlaylistSelection(playlist.serial)}
                                />
                                <label htmlFor={`playlist-${playlist.serial}`}>
                                    {playlist.name}
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                <button onClick={handleUpload}>Upload</button>
                <button onClick={onClose}>Cancel</button>
            </div>
        </div>
    );
};

export default UploadYoutubeVideoPopup;
