import React, { useState } from 'react';
import server from '../Static/Constants';

const CreatecustomImageAlbumPopup = ({ isOpen, onClose }) => {
    const [albumName, setAlbumName] = useState('');
    const [albumDescription, setAlbumDescription] = useState('');
    const [message, setMessage] = useState('');

    const handleCreateAlbum = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');
        const data = {
            album_name: albumName,
            album_description: albumDescription,
        };

        try {
            const response = await fetch(`${server}/create/custom_album/`, {
                method: 'POST',
                headers: {
                    Authorization: token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.status === 201) {
                setMessage('Album created successfully');
                onClose();
            } else {
                const errorData = await response.json();
                setMessage(errorData.message);
            }
        } catch (error) {
            setMessage('Internal server error');
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="picture-upload-form">
            <div className="picture-upload-form-content">
                <button className="picture-upload-form-close" onClick={onClose}>✕</button>
                <h2>Create Album</h2>
                <form className="picture-upload-form-inner" onSubmit={handleCreateAlbum}>
                    <label className="picture-upload-form-label">
                        Album Name:
                        <input
                            className="picture-upload-form-input"
                            type="text"
                            value={albumName}
                            onChange={(e) => setAlbumName(e.target.value)}
                            required
                        />
                    </label>
                    <label className="picture-upload-form-label">
                        Album Description:
                        <textarea
                            className="picture-upload-form-textarea"
                            value={albumDescription}
                            onChange={(e) => setAlbumDescription(e.target.value)}
                            required
                        />
                    </label>
                    <div className="picture-upload-form-button-container">
                        <button className="picture-upload-form-upload-button" type="submit">Create Album</button>
                    </div>
                </form>
                {message && <p className="picture-upload-form-message">{message}</p>}
            </div>
        </div>
    );
};

export default CreatecustomImageAlbumPopup;
