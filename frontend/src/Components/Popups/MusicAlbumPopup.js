import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const MusicAlbumPopup = ({ album, onClose }) => {
    const [thumbnail, setThumbnail] = useState(null);
    const [tracks, setTracks] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");

        const fetchThumbnail = async () => {
            try {
                const response = await fetch(`${server}/get/album_thumbnail/${album.serial}/`, {
                    headers: { Authorization: token }
                });

                if (response.ok) {
                    const blob = await response.blob();
                    setThumbnail(URL.createObjectURL(blob));
                } else {
                    setError("Failed to load thumbnail.");
                }
            } catch (err) {
                console.error(err);
                setError("An error occurred while fetching the thumbnail.");
            }
        };

        const fetchTracks = async () => {
            try {
                const response = await fetch(`${server}/get/track_data/${album.serial}/`, {
                    headers: { Authorization: token }
                });

                const result = await response.json();

                if (!response.ok) {
                    setError(result.message || "Failed to fetch tracks");
                    return;
                }

                const trackDataWithPreviews = await Promise.all(
                    result.data.map(async (track) => {
                        try {
                            const previewResponse = await fetch(`${server}/get/track_preview/${track.track_serial}/`, {
                                headers: { Authorization: token }
                            });

                            if (previewResponse.ok) {
                                const blob = await previewResponse.blob();
                                const previewUrl = URL.createObjectURL(blob);
                                return { ...track, previewUrl };
                            } else {
                                return { ...track, previewUrl: null };
                            }
                        } catch (e) {
                            console.warn(`Failed to fetch preview for track ${track.track_serial}`, e);
                            return { ...track, previewUrl: null };
                        }
                    })
                );

                setTracks(trackDataWithPreviews);
            } catch (err) {
                console.error(err);
                setError("An error occurred while fetching track data.");
            }
        };

        fetchThumbnail();
        fetchTracks();
    }, [album.serial]);

    const formatDuration = (durationInSeconds) => {
        const minutes = Math.floor(durationInSeconds / 60);
        const seconds = durationInSeconds % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="close-button" onClick={onClose}>X</button>
                <h2>{album.album_name}</h2>
                {thumbnail && <img src={thumbnail} alt="Album Thumbnail" className="album-thumbnail" />}
                <p><strong>Artist:</strong> {album.artist_record}</p>
                <p><strong>Type:</strong> {album.album_type}</p>
                <p><strong>Popularity:</strong> {album.album_popularity}</p>
                <p><strong>Release Date:</strong> {album.release_date}</p>
                <p><strong>Total Tracks:</strong> {album.total_tracks}</p>

                <h3>Tracks</h3>
                {tracks.length === 0 ? (
                    <p>Loading tracks...</p>
                ) : (
                    <ul className="track-list">
                        {tracks.map(track => (
                            <li key={track.track_serial} className="track-item">
                                <p><strong>{track.track_number}. {track.track_name}</strong> ({formatDuration(track.track_duration)})</p>
                                {track.previewUrl ? (
                                    <audio controls>
                                        <source src={track.previewUrl} type="audio/mpeg" />
                                        Your browser does not support the audio element.
                                    </audio>
                                ) : (
                                    <p>No preview available.</p>
                                )}
                            </li>
                        ))}
                    </ul>
                )}

                {error && <p className="error-text">{error}</p>}
            </div>
        </div>
    );
};

export default MusicAlbumPopup;
