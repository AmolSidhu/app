import React, {useEffect, useState} from "react";
import DefaultAlbumPicturesRequest from "../../Components/Requests/DefaultAlbumPicturesRequest";
import MainNavbar from "../../Components/Static/MainNavbar";
import PictureSearchPopup from "../../Components/Popups/PictureSearchPopup";

const DefaultPicturePage = () => {
    const [isSearchVisible, setIsSearchVisible] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login/';
        } else {
            document.title = 'Default Pictures';
        }
    }, []);

    const toggleSearchPopup = () => {
        setIsSearchVisible(!isSearchVisible);
    };

    const closeSearchPopup = () => {
        setIsSearchVisible(false);
    };

    return (
        <div>
            <MainNavbar />
            <div style={{ padding: '10px', textAlign: 'right', position: 'relative' }}>
                <button onClick={toggleSearchPopup} style={{ cursor: 'pointer', fontSize: '16px' }}>
                    🔍 Search
                </button>
            </div>

            {isSearchVisible && (
                <div
                    style={{
                        position: 'absolute',
                        top: '60px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        backgroundColor: 'white',
                        border: '1px solid #ccc',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        zIndex: 1000,
                        padding: '20px',
                        borderRadius: '8px',
                        width: '80%',
                        maxWidth: '600px',
                    }}
                >
                    <button
                        onClick={closeSearchPopup}
                        style={{
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            backgroundColor: 'transparent',
                            border: 'none',
                            fontSize: '18px',
                            cursor: 'pointer',
                            color: '#666',
                        }}
                    >
                        ✖
                    </button>
                    <PictureSearchPopup />
                </div>
            )}
            <DefaultAlbumPicturesRequest />
        </div>
    )
};

export default DefaultPicturePage;