import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import VideoSearchRequest from '../../Components/Requests/VideoSearchRequest';

const VideoSearchPage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Search';
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <VideoSearchRequest />
        </div>
    )
};

export default VideoSearchPage;