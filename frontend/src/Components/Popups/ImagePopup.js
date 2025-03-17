import React, { useState, useEffect } from "react";
import server from '../Static/Constants';

const ImagePopup = ({ pictures, selectedIndex, closePopup, onNext, onPrevious, hasNext, hasPrevious }) => {
    const [imageData, setImageData] = useState(null);
    const [error, setError] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false);
    const [hoverSubmenu, setHoverSubmenu] = useState(null);
    const image = pictures[selectedIndex];

    useEffect(() => {
        const fetchImageData = async () => {
            try {
                const token = localStorage.getItem('token');

                const response = await fetch(`${server}/get/picture_data/${image.picture_serial}/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch image');
                }

                const imageData = await response.json();

                if (imageData.data) {
                    const blob = await fetch(`${server}/get/picture_image/${image.picture_serial}/`, {
                        method: 'GET',
                        headers: {
                            'Authorization': token,
                        }
                    }).then(response => response.blob());
                    const imageUrl = URL.createObjectURL(blob);

                    setImageData({
                        ...imageData.data,
                        imageUrl
                    });
                } else {
                    setError('No image data found');
                }
            } catch (err) {
                setError(err.message);
                console.error(err);
            }
        };

        if (image) {
            fetchImageData();
        }
    }, [image]);

    const handleFavouriteToggle = async () => {
        const token = localStorage.getItem('token');
        const action = imageData.is_favourite ? 'remove' : 'add';

        try {
            const response = await fetch(`${server}/update/image_favourites/${image.picture_serial}/`, {
                method: 'POST',
                headers: {
                    'Authorization': token,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action })
            });

            if (!response.ok) throw new Error('Failed to update favourites');

            setImageData(prevData => ({
                ...prevData,
                is_favourite: !prevData.is_favourite
            }));
        } catch (err) {
            console.error(err);
        }
    };

    const handleAddToCustomAlbum = async (albumSerial) => {
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${server}/add/image/custom_album/${albumSerial}/${image.picture_serial}/`, {
                method: 'POST',
                headers: {
                    'Authorization': token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ album_serial: albumSerial }),
            });

            if (!response.ok) throw new Error('Failed to add to custom album');

            console.log(`Added to custom album ${albumSerial} successfully`);
        } catch (err) {
            console.error(err);
        }
    };

    const handleRemoveFromCustomAlbum = async (albumSerial) => {
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${server}/delete/image/custom_album/${albumSerial}/${image.picture_serial}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ album_serial: albumSerial }),
            });

            if (!response.ok) throw new Error('Failed to remove from custom album');

            console.log(`Removed from custom album ${albumSerial} successfully`);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === "ArrowLeft" && hasPrevious) {
                onPrevious();
            } else if (e.key === "ArrowRight" && hasNext) {
                onNext();
            }
        };

        window.addEventListener("keydown", handleKeyPress);

        return () => {
            window.removeEventListener("keydown", handleKeyPress);
        };
    }, [onNext, onPrevious, hasNext, hasPrevious]);

    if (!imageData) return null;

    const tagsArray = typeof imageData.picture_tags === 'string' ? imageData.picture_tags.split(',') : imageData.picture_tags;
    const peopleArray = typeof imageData.picture_people === 'string' ? imageData.picture_people.split(',') : imageData.picture_people;

    return (
        <div className="popup">
            <div className="popup-inner">
                <button className="close-btn" onClick={closePopup}>Close</button>
                {error && <div className="error">{error}</div>}
                {!error && (
                    <>
                        <div className="menu-container">
                            <button onClick={() => setMenuOpen(!menuOpen)} className="menu-btn">⋮</button>
                            {menuOpen && (
                                <div className="menu-dropdown">
                                    <button onClick={handleFavouriteToggle}>
                                        {imageData.is_favourite ? 'Remove from Favourites' : 'Add to Favourites'}
                                    </button>
                                    <div
                                        className="submenu"
                                        onMouseEnter={() => setHoverSubmenu('add')}
                                        onMouseLeave={() => setHoverSubmenu(null)}
                                    >
                                        Add to Custom Album
                                        {hoverSubmenu === 'add' && (
                                            <div className="submenu-dropdown">
                                                {imageData.not_in_custom_albums &&
                                                    imageData.not_in_custom_albums.slice(0, 5).map((album, index) => (
                                                        <button key={index} onClick={() => handleAddToCustomAlbum(JSON.parse(album).album_serial)}>
                                                            {JSON.parse(album).album_name}
                                                        </button>
                                                    ))}
                                                {imageData.not_in_custom_albums && imageData.not_in_custom_albums.length > 5 && <div>Scroll for more...</div>}
                                            </div>
                                        )}
                                    </div>
                                    <div
                                        className="submenu"
                                        onMouseEnter={() => setHoverSubmenu('remove')}
                                        onMouseLeave={() => setHoverSubmenu(null)}
                                    >
                                        Remove from Custom Album
                                        {hoverSubmenu === 'remove' && (
                                            <div className="submenu-dropdown">
                                                {imageData.in_custom_albums &&
                                                    imageData.in_custom_albums.slice(0, 5).map((album, index) => (
                                                        <button key={index} onClick={() => handleRemoveFromCustomAlbum(JSON.parse(album).album_serial)}>
                                                            {JSON.parse(album).album_name}
                                                        </button>
                                                    ))}
                                                {imageData.in_custom_albums && imageData.in_custom_albums.length > 5 && <div>Scroll for more...</div>}
                                            </div>
                                        )}
                                    </div>
                                    <button onClick={() => window.location.href = `/edit/picture/?serial=${image.picture_serial}`}>Edit Picture</button>
                                </div>
                            )}
                        </div>

                        <h2>{imageData.picture_title}</h2>
                        <img src={imageData.imageUrl} alt={imageData.picture_title} className="popup-image" />
                        <div className="description">
                            <strong>Description: </strong>{imageData.picture_description}
                        </div>
                        <div className="tags">
                            <strong>Tags: </strong>{tagsArray.join(', ')}
                        </div>
                        <div className="people">
                            <strong>People: </strong>{peopleArray.join(', ')}
                        </div>
                    </>
                )}
            </div>

            <div className="popup-navigation">
                {hasPrevious && <button className="image-arrow-left" onClick={onPrevious}>←</button>}
                {hasNext && <button className="image-arrow-right" onClick={onNext}>→</button>}
            </div>
        </div>
    );
};

export default ImagePopup;
