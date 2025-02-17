import React, { useState } from 'react';
import server from '../Static/Constants';

const CreateCustomVideoListPopup = ({ isOpen, onClose }) => {
    const [listName, setListName] = useState('');
    const [message, setMessage] = useState('');

    const handleCreateList = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');
        const data = { list_name: listName };

        try {
            const response = await fetch(`${server}/create/custom_video_list/`, {
                method: 'POST',
                headers: {
                    Authorization: token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                setMessage('List created successfully!');
                setListName('');
                setTimeout(() => {
                    setMessage('');
                    onClose();
                }, 2000);
            } else {
                const errorData = await response.json();
                setMessage(`${errorData?.message || 'Failed to create the list.'}`);
            }
        } catch (error) {
            setMessage('Internal server error. Please try again later.');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="popup-overlay">
            <div className="popup-box">
                <button className="popup-close-btn" onClick={onClose}>
                    &times;
                </button>
                <h2>Create Custom Video List</h2>
                <form onSubmit={handleCreateList}>
                    <label htmlFor="listName">List Name:</label>
                    <input
                        id="listName"
                        type="text"
                        value={listName}
                        onChange={(e) => setListName(e.target.value)}
                        placeholder="Enter list name"
                        required
                    />
                    <button type="submit" className="create-btn">
                        Create List
                    </button>
                </form>
                {message && <p className="popup-message">{message}</p>}
            </div>
        </div>
    );
};

export default CreateCustomVideoListPopup;
