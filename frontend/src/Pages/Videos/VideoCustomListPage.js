import React, { useEffect, useState } from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import CreateCustomVideoListPopup from '../../Components/Popups/CreateCustomVideoListPopup';
import CustomVideoListRequest from '../../Components/Requests/CustomVideoListRequest';

const VideoCustomListPage = () => {
    const [isCreateVisible, setIsCreateVisible] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Custom Video Lists';
        }
    }, []);

    const toggleCreatePopup = () => {
        setIsCreateVisible(!isCreateVisible);
    };

    const closeCreatePopup = () => {
        setIsCreateVisible(false);
    };

    return (
        <div>
            <MainNavbar />
            <div style={{ padding: '10px', textAlign: 'right', position: 'relative' }}>
                <button onClick={toggleCreatePopup} className="create-list-btn">
                    + Create List
                </button>
            </div>

            {isCreateVisible && (
                <CreateCustomVideoListPopup isOpen={isCreateVisible} onClose={closeCreatePopup} />
            )}

            <CustomVideoListRequest />
        </div>
    );
};

export default VideoCustomListPage;
