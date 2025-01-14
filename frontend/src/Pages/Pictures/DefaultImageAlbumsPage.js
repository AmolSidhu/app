import React, {useEffect} from 'react';
import DefaultImageAlbumRequest from '../../Components/Requests/DefaultImageAlbumRequest';
import MainNavbar from '../../Components/Static/MainNavbar';

const DefaultImageAlbumsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Default Image Albums';
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <DefaultImageAlbumRequest />
        </div>
    )
}

export default DefaultImageAlbumsPage;