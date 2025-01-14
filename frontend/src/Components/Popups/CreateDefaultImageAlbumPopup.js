import React, { useState } from 'react';
import server from '../Static/Constants';

const CreateDefaultImageAlbumPopup = ({ isOpen, onClose }) => {
    const [albumName, setAlbumName] = useState('');
    const [albumDescription, setAlbumDescription] = useState('');
    const [tagInput, setTagInput] = useState('');
    const [tags, setTags] = useState([]);
    const [message, setMessage] = useState('');

    const handleCreateAlbum = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');
        const data = {
            album_name: albumName,
            album_description: albumDescription,
            tags: tags,
        };

        try {
            const response = await fetch(`${server}/create/album/`, {
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

    const handleTagKeyDown = (e) => {
        if (e.key === 'Enter' && tagInput.trim()) {
            e.preventDefault();
            setTags([...tags, tagInput.trim()]);
            setTagInput('');
        }
    };

    const handleRemoveTag = (index) => {
        setTags(tags.filter((tag, i) => i !== index));
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
                    <label>
                        Tags:
                        <input
                            type="text"
                            value={tagInput}
                            onChange={(e) => setTagInput(e.target.value)}
                            onKeyDown={handleTagKeyDown}
                            placeholder="Enter a tag and press Enter"
                        />
                        <div>
                            {tags.map((tag, index) => (
                                <span key={index} className="tag">
                                    {tag}
                                    <button type="button" onClick={() => handleRemoveTag(index)}>x</button>
                                </span>
                            ))}
                        </div>
                    </label>
                    <button type="submit">Create Album</button>
                </form>
                {message && <p>{message}</p>}
            </div>
        </div>
    );
};

export default CreateDefaultImageAlbumPopup;
