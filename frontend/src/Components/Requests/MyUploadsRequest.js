import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import server from "../Static/Constants";

const MyUploadsRequest = () => {
    const [videos, setVideos] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchVideos = async () => {
            try {
                const token = localStorage.getItem('token');

                const videoResponse = await fetch(`${server}/get/editing_video_list/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                });

                if (!videoResponse.ok) {
                    throw new Error('Failed to fetch videos');
                }

                const videoData = await videoResponse.json();

                if (videoData.data) {
                    setVideos(videoData.data);
                } else {
                    setError('No videos found');
                }
            } catch (error) {
                setError(error.message);
            }
        };

        fetchVideos();
    }, []);

    return (
        <div>
            <h2>My Uploads</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
                {videos.map((video) => (
                    <div key={video.serial} style={{ padding: "10px", border: "1px solid #ddd", borderRadius: "5px" }}>
                        <h3>{video.title}</h3>
                        <p>{video.description}</p>
                        <Link to={`/edit/video/?serial=${video.serial}`} style={{ color: "blue", textDecoration: "underline" }}>
                            Edit
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MyUploadsRequest;
