import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import VideoStreamRequest from '../../Components/Requests/VideoStreamRequest';
import VideoSuggestionsRequest from '../../Components/Requests/VideoSuggestionsRequest';
import StreamDataRequest from '../../Components/Requests/StreamDataRequest';

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
            <StreamDataRequest />
            <VideoSuggestionsRequest />
        </div>
    )
};

export default VideoStreamPage;