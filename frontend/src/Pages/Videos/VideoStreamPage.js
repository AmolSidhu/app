import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import VideoStreamRequest from '../../Components/Requests/VideoStreamRequest';

const VideoStreamPage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Video Stream';
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <VideoStreamRequest />
        </div>
    )
};

export default VideoStreamPage;