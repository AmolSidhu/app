import React, { useState, useEffect, useCallback } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

function VideoSuggestionsRequest() {
    const [videos, setVideos] = useState([]);
    const [error, setError] = useState(null);
    const [selectedSerial, setSelectedSerial] = useState(null);
    const location = useLocation();
    const search = location.search;

    const fetchVideos = useCallback(async () => {
        try {
            const params = new URLSearchParams(search);
            const query = params.get("serial");
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/get/video_suggestions/${query}/`, {
                method: "GET",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const fetchedVideos = [];

            for (let video of data.data) {
                try {
                    const thumbnailResponse = await fetch(`${server}/get/video_thumbnail/${video.serial}`, {
                        method: "GET",
                        headers: {
                            Authorization: token,
                        },
                    });

                    if (!thumbnailResponse.ok) {
                        throw new Error(`Thumbnail fetch error! Status: ${thumbnailResponse.status}`);
                    }

                    const thumbnailBlob = await thumbnailResponse.blob();
                    const thumbnailUrl = URL.createObjectURL(thumbnailBlob);

                    fetchedVideos.push({
                        ...video,
                        image_url: thumbnailUrl,
                    });
                } catch (thumbnailError) {
                    console.error(`Error fetching thumbnail for video ${video.serial}:`, thumbnailError);
                    fetchedVideos.push(video);
                }
            }

            setVideos(fetchedVideos);
        } catch (error) {
            setError(error.message);
        }
    }, [search]);

    useEffect(() => {
        fetchVideos();
    }, [fetchVideos]);

    const openPopup = (serial) => {
        setSelectedSerial(serial);
    };

    const closePopup = () => {
        setSelectedSerial(null);
    };

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (videos.length === 0) {
        return (
            <div className="video-list-container">
                <h1>Suggested Videos</h1>
                <p>There were no similar videos found</p>
            </div>
        );
    }

    return (
        <div className="video-list-container">
            <h1>Suggested Video</h1>
            <div className="video-navigation">
                <div className="video-list">
                    {videos.map((video, index) => (
                        <div
                            key={index}
                            className="video-item"
                            onClick={() => openPopup(video.serial)}
                        >
                            <img src={video.image_url} alt={video.title} />
                        </div>
                    ))}
                </div>
            </div>
            {selectedSerial && (
                <div className="popup">
                    <div className="popup-inner">
                        <button onClick={closePopup}>Close</button>
                        <VideoDetailPopup serial={selectedSerial} onClose={closePopup} />
                    </div>
                </div>
            )}
        </div>
    );
}

export default VideoSuggestionsRequest;
