import React, {useEffect} from "react";
import CustomAlbumPictureRequest from "../../Components/Requests/CustomAlbumPictureRequest";
import MainNavbar from "../../Components/Static/MainNavbar";

const CustomPicturePage = () => {
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Custom Picture';
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <CustomAlbumPictureRequest />
        </div>
    )
};

export default CustomPicturePage;