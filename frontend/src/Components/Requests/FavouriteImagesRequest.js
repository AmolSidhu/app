import React, { useState, useEffect } from "react";
import server from '../Static/Constants';
import ImagePopup from '../Popups/ImagePopup';

const FavouriteImageRequest = () => {
    const [pictures, setPictures] = useState([]);
    const [error, setError] = useState(null);
    const [selectedImage, setSelectedImage] = useState(null);

    useEffect(() => {
        const fetchPictures = async () => {
            try {
                const token = localStorage.getItem('token');

                const pictureResponse = await fetch(`${server}/get/favourite_images/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    },
                });

                if (!pictureResponse.ok) {
                    throw new Error('Failed to fetch pictures');
                }

                const pictureData = await pictureResponse.json();

                if (pictureData.data) {
                    const picturesWithThumbnails = await Promise.all(
                        pictureData.data.map(async (picture) => {
                            const thumbnailResponse = await fetch(`${server}/get/thumbnail/${picture.picture_serial}`, {
                                method: 'GET'
                            });

                            if (!thumbnailResponse.ok) {
                                throw new Error('Failed to fetch thumbnail');
                            }

                            const blob = await thumbnailResponse.blob();
                            const imageUrl = URL.createObjectURL(blob);
                            return { ...picture, thumbnailUrl: imageUrl };
                        })
                    );
                    setPictures(picturesWithThumbnails);
                } else {
                    setError('No pictures found');
                }
            } catch (err) {
                setError(err.message);
                console.error(err);
            }
        };

        fetchPictures();
    }, []);

    const openImagePopup = (image) => {
        setSelectedImage(image);
    };

    const closeImagePopup = () => setSelectedImage(null);

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div>
            {pictures.map((picture) => (
                <div key={picture.picture_serial} className="picture-item" onClick={() => openImagePopup(picture)}>
                    <img src={picture.thumbnailUrl} alt={picture.picture_name} />
                    <h3>{picture.picture_title}</h3>
                    <p>{picture.picture_description}</p>
                </div>
            ))}
            {selectedImage && (
                <ImagePopup image={selectedImage} closePopup={closeImagePopup} />
            )}
        </div>
    );
};

export default FavouriteImageRequest;
