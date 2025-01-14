import React, {useEffect} from 'react';
import CustomImageAlbumRequest from '../../Components/Requests/CustomImageAlbumRequest';
import MainNavbar from '../../Components/Static/MainNavbar';

const CustomImageAlbumsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Custom Image Albums';
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <CustomImageAlbumRequest />
        </div>
    )
};

export default CustomImageAlbumsPage;