import React, { useState, useEffect } from "react";
import server from "../Static/Constants";

const YoutubePlaylistsRequest = () => {
    const [playlists, setPlaylists] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);

    const VIDEOS_PER_PAGE = 5;

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
            return;
        }

        fetch(`${server}/get/youtube_playlists/`, {
            method: "GET",
            headers: { Authorization: token }
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(result => {
            if (!result.ok) {
                setErrorMessage(result.data.message || "Failed to fetch playlists.");
                return;
            }

            const loadedPlaylists = result.data.data.map(playlist => ({
                ...playlist,
                videos: [],
                currentPage: 0,
                total: 0
            }));

            setPlaylists(loadedPlaylists);

            loadedPlaylists.forEach(playlist => {
                fetchVideosForPlaylist(playlist.serial, 0);
            });
        })
        .catch(err => {
            console.error("Top-level fetch error:", err);
            setErrorMessage("An error occurred while fetching playlists.");
        });
    }, []);

    const fetchVideosForPlaylist = (serial, page) => {
        const token = localStorage.getItem("token");
        const offset = page * VIDEOS_PER_PAGE;

        fetch(`${server}/get/playlist_videos/${serial}/?offset=${offset}&limit=${VIDEOS_PER_PAGE}`, {
            method: "GET",
            headers: { Authorization: token }
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(result => {
            if (!result.ok || !result.data.data) return;

            const videos = result.data.data;
            const total = result.data.total;

            const fetchThumbnails = async () => {
                const videosWithThumbnails = await Promise.all(
                    videos.map(async (video) => {
                        try {
                            const thumbRes = await fetch(`${server}/get/youtube_thumbnail/${video.serial}/`, {
                                method: "GET",
                                headers: { Authorization: token }
                            });

                            if (!thumbRes.ok) {
                                return { ...video, thumbnailUrl: null };
                            }

                            const blob = await thumbRes.blob();
                            const url = URL.createObjectURL(blob);
                            return { ...video, thumbnailUrl: url };
                        } catch {
                            return { ...video, thumbnailUrl: null };
                        }
                    })
                );

                setPlaylists(prev => prev.map(p => {
                    if (p.serial !== serial) return p;
                    return {
                        ...p,
                        videos: videosWithThumbnails,
                        total,
                        currentPage: page
                    };
                }));
            };

            fetchThumbnails();
        })
        .catch(err => {
            console.error("Fetch videos error:", err);
        });
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
        <div className="playlists-container">
            <h2>YouTube Playlists</h2>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
            {playlists.map((playlist) => (
                <div key={playlist.serial} className="playlist-item">
                    <h3>{playlist.name}</h3>
                    <p>{playlist.description}</p>
                    <div className="videos-list">
                        {playlist.videos.length > 0 ? (
                            <>
                                {playlist.videos.map((video) => (
                                    <div key={video.serial} className="video-item" style={{ display: "flex", alignItems: "center", marginBottom: "1rem" }}>
                                        {video.thumbnailUrl ? (
                                            <img
                                                src={video.thumbnailUrl}
                                                alt={video.title}
                                                style={{ width: "120px", height: "auto", marginRight: "1rem" }}
                                            />
                                        ) : (
                                            <div style={{ width: "120px", height: "90px", backgroundColor: "#ccc", marginRight: "1rem" }} />
                                        )}
                                        <div>
                                            <h4>{video.title}</h4>
                                        </div>
                                    </div>
                                ))}
                                <div className="pagination-controls" style={{ marginTop: "1rem" }}>
                                    <button
                                        onClick={() => handlePageChange(playlist.serial, -1)}
                                        disabled={playlist.currentPage === 0}
                                    >
                                        Previous
                                    </button>
                                    <span style={{ margin: "0 1rem" }}>
                                        Page {playlist.currentPage + 1} of {Math.ceil(playlist.total / VIDEOS_PER_PAGE)}
                                    </span>
                                    <button
                                        onClick={() => handlePageChange(playlist.serial, 1)}
                                        disabled={(playlist.currentPage + 1) * VIDEOS_PER_PAGE >= playlist.total}
                                    >
                                        Next
                                    </button>
                                </div>
                            </>
                        ) : (
                            <p>No videos in this playlist.</p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default YoutubePlaylistsRequest;
