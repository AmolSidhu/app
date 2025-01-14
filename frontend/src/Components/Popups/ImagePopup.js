import React, { useState, useEffect } from "react";
import server from '../Static/Constants';

const ImagePopup = ({ image, closePopup, onNext, onPrevious, hasNext, hasPrevious }) => {
    const [imageData, setImageData] = useState(null);
    const [error, setError] = useState(null);

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

        fetchImageData();
    }, [image.picture_serial]);

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
                        <h2>{imageData.picture_title}</h2>
                        <div className="popup-content">
                            <img src={imageData.imageUrl} alt={imageData.picture_title} className="popup-image" />
                            <div className="popup-details">
                                <div className="popup-tags">
                                    <h3>Tags</h3>
                                    <ul>
                                        {tagsArray.map((tag, index) => (
                                            <li key={index}>{tag}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="popup-people">
                                    <h3>People</h3>
                                    <ul>
                                        {peopleArray.map((person, index) => (
                                            <li key={index}>{person}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                            <div className="popup-description">
                                <h3>Description</h3>
                                <p>{imageData.description}</p>
                            </div>
                        </div>
                        <div className="popup-navigation">
                            {hasPrevious && <button onClick={onPrevious}>Previous</button>}
                            {hasNext && <button onClick={onNext}>Next</button>}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ImagePopup;
