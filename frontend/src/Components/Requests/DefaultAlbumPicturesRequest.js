import React, { useState, useEffect } from "react";
import server from '../Static/Constants';
import PictureUploadPopup from '../Popups/PictureUploadPopup';
import ImagePopup from '../Popups/ImagePopup';

const DefaultAlbumPicturesRequest = () => {
    const [pictures, setPictures] = useState([]);
    const [error, setError] = useState(null);
    const [isUploadPopupOpen, setIsUploadPopupOpen] = useState(false);
    const [selectedImageIndex, setSelectedImageIndex] = useState(null);

    useEffect(() => {
        const fetchPictures = async () => {
            try {
                const token = localStorage.getItem('token');
                const urlParams = new URLSearchParams(window.location.search);
                const album = urlParams.get('album');

                if (!album) {
                    setError('Album parameter is missing');
                    return;
                }

                const pictureResponse = await fetch(`${server}/get/picture/${album}`, {
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
                                method: 'GET',
                                headers: {
                                    'Authorization': token,
                                    'Content-Type': 'application/json'
                                }
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
            } catch (error) {
                setError(error.message);
                console.error(error);
            }
        };

        fetchPictures();
    }, []);

    const openUploadPopup = () => setIsUploadPopupOpen(true);
    const closeUploadPopup = () => setIsUploadPopupOpen(false);

    const openImagePopup = (index) => {
        setSelectedImageIndex(index);
    };

    const closeImagePopup = () => setSelectedImageIndex(null);

    const handleNextImage = () => {
        setSelectedImageIndex((prevIndex) => (prevIndex + 1) % pictures.length);
    };

    const handlePrevImage = () => {
        setSelectedImageIndex((prevIndex) => (prevIndex - 1 + pictures.length) % pictures.length);
    };

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div>
            <button className="upload-button create-album-button button" onClick={openUploadPopup}>
                Upload Picture
            </button>
            {pictures.map((picture, index) => (
                <div key={picture.picture_serial} className="picture-item" onClick={() => openImagePopup(index)}>
                    <img src={picture.thumbnailUrl} alt={picture.picture_name} />
                    <h3>{picture.picture_title}</h3>
                    <p>{picture.picture_description}</p>
                </div>
            ))}
            {selectedImageIndex !== null && (
                <ImagePopup
                    image={pictures[selectedImageIndex]}
                    closePopup={closeImagePopup}
                    onNext={handleNextImage}
                    onPrevious={handlePrevImage}
                    hasNext={selectedImageIndex < pictures.length - 1}
                    hasPrevious={selectedImageIndex > 0}
                />
            )}
            <PictureUploadPopup isOpen={isUploadPopupOpen} onClose={closeUploadPopup} />
        </div>
    );
};

export default DefaultAlbumPicturesRequest;
