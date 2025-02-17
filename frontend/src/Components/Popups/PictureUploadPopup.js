import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import server from '../Static/Constants';

const PictureUploadPopup = ({ isOpen, onClose }) => {
    const [image, setImage] = useState(null);
    const [album, setAlbum] = useState('');
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [tagInput, setTagInput] = useState('');
    const [tags, setTags] = useState([]);
    const [peopleInput, setPeopleInput] = useState('');
    const [people, setPeople] = useState([]);
    const [userEditable, setUserEditable] = useState(true);
    const [message, setMessage] = useState('');
    const location = useLocation();

    useEffect(() => {
        const query = new URLSearchParams(location.search);
        const albumName = query.get('album');
        if (albumName) {
            setAlbum(albumName);
        }
    }, [location.search]);

    useEffect(() => {
        const fetchTags = async () => {
            if (album) {
                const token = localStorage.getItem('token');
                try {
                    const response = await fetch(`${server}/get/tags/${album}`, {
                        method: 'GET',
                        headers: {
                            Authorization: token,
                        },
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setTags(data.tags || []);
                    } else {
                        const errorData = await response.json();
                        setMessage(errorData.message || 'Failed to fetch tags');
                    }
                } catch (error) {
                    setMessage('Internal server error');
                }
            }
        };

        fetchTags();
    }, [album]);

    const handleImageChange = (e) => {
        setImage(e.target.files[0]);
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

    const handlePeopleKeyDown = (e) => {
        if (e.key === 'Enter' && peopleInput.trim()) {
            e.preventDefault();
            setPeople([...people, peopleInput.trim()]);
            setPeopleInput('');
        }
    };

    const handleRemovePerson = (index) => {
        setPeople(people.filter((person, i) => i !== index));
    };

    const handleUpload = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('image', image);
        formData.append('album', album);
        formData.append('title', title);
        formData.append('description', description);
        formData.append('tags', tags.join(','));
        formData.append('people', people.join(','));
        formData.append('user_editable', userEditable);

        try {
            const response = await fetch(`${server}/upload/picture/`, {
                method: 'POST',
                headers: {
                    Authorization: token,
                },
                body: formData,
            });

            if (response.status === 201) {
                setMessage('Image uploaded successfully');
                onClose();
                window.location.reload();
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
                <h2>Upload Picture</h2>
                <form className="picture-upload-form-inner" onSubmit={handleUpload}>
                    <label className="picture-upload-form-label">
                        Image:
                        <input type="file" onChange={handleImageChange} required />
                    </label>
                    <label className="picture-upload-form-label">
                        Album Name:
                        <input
                            type="text"
                            value={album}
                            onChange={(e) => setAlbum(e.target.value)}
                            required
                            disabled
                        />
                    </label>
                    <label className="picture-upload-form-label">
                        Title:
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                        />
                    </label>
                    <label className="picture-upload-form-label">
                        Description:
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            required
                        />
                    </label>
                    <label className="picture-upload-form-label">
                        Tags:
                        <input
                            type="text"
                            value={tagInput}
                            onChange={(e) => setTagInput(e.target.value)}
                            onKeyDown={handleTagKeyDown}
                            placeholder="Enter a tag and press Enter"
                        />
                        <div className="picture-upload-form-tag-list">
                            {tags.map((tag, index) => (
                                <span key={index} className="picture-upload-form-tag">
                                    {tag}
                                    <button type="button" onClick={() => handleRemoveTag(index)}>x</button>
                                </span>
                            ))}
                        </div>
                    </label>
                    <label className="picture-upload-form-label">
                        People:
                        <input
                            type="text"
                            value={peopleInput}
                            onChange={(e) => setPeopleInput(e.target.value)}
                            onKeyDown={handlePeopleKeyDown}
                            placeholder="Enter a person's name and press Enter"
                        />
                        <div className="picture-upload-form-people-list">
                            {people.map((person, index) => (
                                <span key={index} className="picture-upload-form-person">
                                    {person}
                                    <button type="button" onClick={() => handleRemovePerson(index)}>x</button>
                                </span>
                            ))}
                        </div>
                    </label>
                    <label className="picture-upload-form-checkbox">
                        <input
                            type="checkbox"
                            checked={userEditable}
                            onChange={(e) => setUserEditable(e.target.checked)}
                        />
                        User Editable
                    </label>
                    <div className="picture-upload-form-button-container">
                        <button className="picture-upload-form-upload-button" type="submit">Upload</button>
                    </div>
                </form>
                {message && <p className="picture-upload-form-message">{message}</p>}
            </div>
        </div>
    );
};

export default PictureUploadPopup;