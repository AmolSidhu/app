import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import server from "../Static/Constants";
import CreateDefaultImageAlbumPopup from "../Popups/CreateDefaultImageAlbumPopup";

const DefaultImageAlbumRequest = () => {
    const [albums, setAlbums] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDefaultAlbums = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}/get/albums/`, {
                    method: "GET",
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    }
                });
                if (!response.ok) {
                    throw new Error("An error occurred while fetching default albums");
                }
                const result = await response.json();
                if (result.data) {
                    setAlbums(result.data);
                } else {
                    throw new Error("An error occurred while fetching default albums");
                }   
                setLoading(false);
            }
            catch (error) {
                setError(error.message);
                setLoading(false);
            }
        };
        fetchDefaultAlbums();
    }, []);

    const openPopup = () => {
        setIsPopupOpen(true);
    };

    const closePopup = () => {
        setIsPopupOpen(false);
    };

    const handleAlbumClick = (albumSerial) => {
        navigate(`/pictures?album=${albumSerial}`);
    };

    return (
        <div>
            <button onClick={openPopup} className="create-album-button button">
                Create Album
            </button>
            <CreateDefaultImageAlbumPopup isOpen={isPopupOpen} onClose={closePopup} />
            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <div>
                    {albums.map((album) => (
                        <div 
                            key={album.album_serial}
                            onClick={() => handleAlbumClick(album.album_serial)}
                            style={{ cursor: "pointer" }}
                        >
                            <h2>{album.album_name}</h2>
                            <p>{album.album_description}</p> 
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default DefaultImageAlbumRequest;
