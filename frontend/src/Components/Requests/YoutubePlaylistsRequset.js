import React, { useState, useEffect } from "react";
import server from "../Static/Constants";

const YoutubePlaylistsRequest = () => {
    const [playlists, setPlaylists] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);

    const VIDEOS_PER_PAGE = 5;

    useEffect(() => {
        const fetchPlaylists = async () => {
            const token = localStorage.getItem("token");
            if (!token) {
                window.location.href = "/login/";
                return;
            }

            try {
                const res = await fetch(`${server}/get/youtube_playlists/`, {
                    headers: { Authorization: token }
                });
                const data = await res.json();

                if (!res.ok) {
                    setErrorMessage(data.message || "Failed to fetch playlists.");
                    return;
                }

                const loadedPlaylists = data.data.map(playlist => ({
                    ...playlist,
                    videos: [],
                    currentPage: 0,
                    total: 0
                }));

                setPlaylists(loadedPlaylists);

                for (const playlist of loadedPlaylists) {
                    await fetchVideosForPlaylist(playlist.serial, 0);
                }
            } catch (err) {
                console.error("Top-level fetch error:", err);
                setErrorMessage("An error occurred while fetching playlists.");
            }
        };

        fetchPlaylists();
    }, []);

    const fetchVideosForPlaylist = async (serial, page) => {
        const token = localStorage.getItem("token");
        const offset = page * VIDEOS_PER_PAGE;

        try {
            const res = await fetch(
                `${server}/get/playlist_videos/${serial}/?offset=${offset}&limit=${VIDEOS_PER_PAGE}`,
                { headers: { Authorization: token } }
            );
            const result = await res.json();

            if (!res.ok || !result.data) return;

            const { data: videos, total } = result;

            const videosWithThumbnails = [];

            for (const video of videos) {
                let thumbnailUrl = null;
                try {
                    const thumbRes = await fetch(`${server}/get/youtube_thumbnail/${video.serial}/`, {
                        headers: { Authorization: token }
                    });

                    if (thumbRes.ok) {
                        const blob = await thumbRes.blob();
                        thumbnailUrl = URL.createObjectURL(blob);
                    }
                } catch (err) {
                    console.error(`Error fetching thumbnail for video ${video.serial}`, err);
                }

                videosWithThumbnails.push({ ...video, thumbnailUrl });
            }

            setPlaylists(prev =>
                prev.map(p =>
                    p.serial === serial
                        ? { ...p, videos: videosWithThumbnails, total, currentPage: page }
                        : p
                )
            );
        } catch (err) {
            console.error("Fetch videos error:", err);
        }
    };

    const handlePageChange = (serial, direction) => {
        const playlist = playlists.find(p => p.serial === serial);
        if (!playlist) return;

        const nextPage = playlist.currentPage + direction;
        const maxPage = Math.ceil(playlist.total / VIDEOS_PER_PAGE) - 1;

        if (nextPage >= 0 && nextPage <= maxPage) {
            fetchVideosForPlaylist(serial, nextPage);
        }
    };

    return (
        <div className="video-list-container">
            <h1>YouTube Playlists</h1>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
            {playlists.map(playlist => (
                <div key={playlist.serial} className="genre-section">
                    <h2 className="genre-title">{playlist.name}</h2>
                    <p>{playlist.description}</p>
                    <div className="video-grid-container">
                        {playlist.videos.length > 0 ? (
                            playlist.videos.map(video => (
                                <div key={video.serial} className="video-grid-item">
                                    <a href={`/youtube/stream/?serial=${video.serial}`}>
                                        {video.thumbnailUrl ? (
                                            <img src={video.thumbnailUrl} alt={video.title} />
                                        ) : (
                                            <div style={{ width: "100%", height: "90px", backgroundColor: "#ccc" }} />
                                        )}
                                    </a>
                                    <h4>
                                        <a
                                            href={`/youtube/stream/?serial=${video.serial}`}
                                            style={{ textDecoration: "none", color: "inherit" }}
                                        >
                                            {video.title}
                                        </a>
                                    </h4>
                                </div>
                            ))
                        ) : (
                            <p>No videos in this playlist.</p>
                        )}
                    </div>

                    {playlist.total > VIDEOS_PER_PAGE && (
                        <div className="video-navigation" style={{ marginTop: "1rem" }}>
                            <button
                                className="nav-arrow"
                                onClick={() => handlePageChange(playlist.serial, -1)}
                                disabled={playlist.currentPage === 0}
                            >
                                &larr;
                            </button>
                            <span>
                                Page {playlist.currentPage + 1} of{" "}
                                {Math.ceil(playlist.total / VIDEOS_PER_PAGE)}
                            </span>
                            <button
                                className="nav-arrow"
                                onClick={() => handlePageChange(playlist.serial, 1)}
                                disabled={(playlist.currentPage + 1) * VIDEOS_PER_PAGE >= playlist.total}
                            >
                                &rarr;
                            </button>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default YoutubePlaylistsRequest;