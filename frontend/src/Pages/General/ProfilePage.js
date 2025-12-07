import React, { useEffect, useState } from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ChangeEmailPopup from "../../Components/Popups/ChangeEmailPopup";
import ChangePasswordPopup from "../../Components/Popups/ChangePasswordPopup";
import ChangeUsernamePopup from "../../Components/Popups/ChangeUsernamePopup";

const ProfilePage = () => {
    const [showUsernamePopup, setShowUsernamePopup] = useState(false);
    const [showEmailPopup, setShowEmailPopup] = useState(false);
    const [showPasswordPopup, setShowPasswordPopup] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Profile";
        }
    }, []);

    return (
        <>
            <MainNavbar />
            <div>
                <h1>Profile Page</h1>

                <button onClick={() => setShowUsernamePopup(true)}>Change Username</button>
                <button onClick={() => setShowEmailPopup(true)}>Change Email</button>
                <button onClick={() => setShowPasswordPopup(true)}>Change Password</button>

                {showUsernamePopup && (
                    <ChangeUsernamePopup 
                        onClose={() => {
                            setShowUsernamePopup(false);
                            window.location.reload();
                        }} 
                    />
                )}

                {showEmailPopup && (
                    <ChangeEmailPopup 
                        onClose={() => {
                            setShowEmailPopup(false);
                            window.location.reload();
                        }} 
                    />
                )}

                {showPasswordPopup && (
                    <ChangePasswordPopup 
                        onClose={() => {
                            setShowPasswordPopup(false);
                            window.location.reload();
                        }} 
                    />
                )}
            </div>
        </>
    );
};

export default ProfilePage;
