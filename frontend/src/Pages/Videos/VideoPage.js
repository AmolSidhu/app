import React, { useEffect, useState } from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import DefaultVideoListRequest from '../../Components/Requests/DefaultVideoListRequest';
import VideoHistoryRequest from '../../Components/Requests/VideoHistoryRequest';
import GenreVideoListRequest from '../../Components/Requests/GenreVideoListRequest';
import VideoSearhPopup from '../../Components/Popups/VideoSearchPopup';
import VideoTitleSearchRequest from '../../Components/Requests/VideoTitleSearchRequest';

const VideoPage = () => {
    const [isSearchVisible, setIsSearchVisible] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Videos';
        }
    }, []);

    const toggleSearchPopup = () => {
        setIsSearchVisible(!isSearchVisible);
    };

    const closeSearchPopup = () => {
        setIsSearchVisible(false);
    };

    return (
        <div>
            <MainNavbar />
            <div style={{ padding: '10px', textAlign: 'right', position: 'relative' }}>
                <button onClick={toggleSearchPopup} style={{ cursor: 'pointer', fontSize: '16px' }}>
                    🔍 Search
                </button>
            </div>

            {isSearchVisible && (
                <div
                    style={{
                        position: 'absolute',
                        top: '60px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        backgroundColor: 'white',
                        border: '1px solid #ccc',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        zIndex: 1000,
                        padding: '20px',
                        borderRadius: '8px',
                        width: '80%',
                        maxWidth: '600px',
                    }}
                >
                    <button
                        onClick={closeSearchPopup}
                        style={{
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            backgroundColor: 'transparent',
                            border: 'none',
                            fontSize: '18px',
                            cursor: 'pointer',
                            color: '#666',
                        }}
                    >
                        ✖
                    </button>

                    <VideoSearhPopup />
                </div>
            )}
            <VideoTitleSearchRequest />
            <DefaultVideoListRequest />
            <VideoHistoryRequest />
            <GenreVideoListRequest />
        </div>
    );
};

export default VideoPage;
