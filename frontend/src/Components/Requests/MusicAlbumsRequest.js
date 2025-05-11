import React, { useState, useEffect } from 'react';
import server from '../Static/Constants';
import CreateMusicAlbumPopup from '../Popups/CreateMusicAlbumPopup';
import MusicAlbumPopup from '../Popups/MusicAlbumPopup';

const MusicAlbumsRequest = () => {
    const [albums, setAlbums] = useState([]);
    const [showCreatePopup, setShowCreatePopup] = useState(false);
    const [selectedAlbum, setSelectedAlbum] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAlbums = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}/get/music_albums/`, {
                    headers: { Authorization: token }
                });

                const data = await response.json();
                if (!response.ok) {
                    setError(data.message || 'Failed to fetch albums');
                    return;
                }

                const albumsWithThumbnails = [];
                for (const album of data.data) {
                    let thumbnail = null;
                    try {
                        const thumbResponse = await fetch(`${server}/get/album_thumbnail/${album.serial}/`, {
                            headers: { Authorization: token }
                        });

                        if (thumbResponse.ok) {
                            const blob = await thumbResponse.blob();
                            thumbnail = URL.createObjectURL(blob);
                        }
                    } catch (err) {
                        console.warn(`Failed to load thumbnail for ${album.serial}`, err);
                    }

                    albumsWithThumbnails.push({ ...album, thumbnail });
                }

                setAlbums(albumsWithThumbnails);
            } catch (err) {
                console.error(err);
                setError('An error occurred while fetching albums.');
            }
        };

        fetchAlbums();
    }, []);

    return (
        <div className="music-page">
            <h1 className="music-title">Music Albums</h1>
            <button className="create-button" onClick={() => setShowCreatePopup(true)}>Create New Album</button>

            {error && <p className="error-text">{error}</p>}

            <div className="album-grid">
                {albums.map((album) => (
                    <div key={album.serial} className="album-card">
                        {album.thumbnail ? (
                            <img
                                src={album.thumbnail}
                                alt={album.album_name}
                                className="album-thumbnail"
                                onClick={() => setSelectedAlbum(album)}
                                style={{ cursor: "pointer" }}
                            />
                        ) : (
                            <div
                                className="no-thumbnail"
                                onClick={() => setSelectedAlbum(album)}
                                style={{ cursor: "pointer" }}
                            >
                                No Image
                            </div>
                        )}
                        <h3 className="album-name">{album.album_name}</h3>
                        <p><strong>Artist:</strong> {album.artist_record}</p>
                        <p><strong>Type:</strong> {album.album_type}</p>
                        <p><strong>Popularity:</strong> {album.album_popularity}</p>
                        <p><strong>Release:</strong> {album.release_date}</p>
                        <p><strong>Tracks:</strong> {album.total_tracks}</p>
                        <a href={album.album_spotify_link} target="_blank" rel="noopener noreferrer">Spotify</a>
                    </div>
                ))}
            </div>

            {showCreatePopup && <CreateMusicAlbumPopup onClose={() => setShowCreatePopup(false)} />}
            {selectedAlbum && <MusicAlbumPopup album={selectedAlbum} onClose={() => setSelectedAlbum(null)} />}
        </div>
    );
};

export default MusicAlbumsRequest;
