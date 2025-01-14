import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import PictureSearchRequest from '../../Components/Requests/PictureSearchRequest';

const PictureSearchPage = () => {
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
            <PictureSearchRequest />
        </div>
    )
};

export default PictureSearchPage;