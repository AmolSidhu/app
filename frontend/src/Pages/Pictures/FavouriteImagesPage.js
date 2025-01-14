import React, {useEffect} from 'react';
import FavouriteImagesRequest from '../../Components/Requests/FavouriteImagesRequest';
import MainNavbar from '../../Components/Static/MainNavbar';

const FavouriteImagesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Favourite Images';
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <FavouriteImagesRequest />
        </div>
    )
};

export default FavouriteImagesPage;