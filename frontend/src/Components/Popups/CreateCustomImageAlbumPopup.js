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
        <div className="popup">
            <div className="popup-content">
                <button onClick={onClose}>Close</button>
                <h2>Create Album</h2>
                <form onSubmit={handleCreateAlbum}>
                    <label>
                        Album Name:
                        <input
                            type="text"
                            value={albumName}
                            onChange={(e) => setAlbumName(e.target.value)}
                            required
                        />
                    </label>
                    <label>
                        Album Description:
                        <textarea
                            value={albumDescription}
                            onChange={(e) => setAlbumDescription(e.target.value)}
                            required
                        />
                    </label>
                    <button type="submit">Create Album</button>
                </form>
                {message && <p>{message}</p>}
            </div>
        </div>
    );
};

export default CreatecustomImageAlbumPopup;
