import React, { useEffect } from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import FavouriteVideoRequest from '../../Components/Requests/FavouriteVideoRequest';

const VideoFavouritePage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Favourite Videos';
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>Favourite Videos</h1>
            <FavouriteVideoRequest />
        </div>
    );
}

export default VideoFavouritePage;
