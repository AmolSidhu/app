import React, { useState } from "react";
import server from "../Static/Constants";

const ChangePasswordPopup = ({ onClose }) => {
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            setMessage("New password and confirm password do not match.");
            return;
        }

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/change/password/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: token,
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                }),
            });

            if (response.ok) {
                setMessage("Password changed successfully.");
            } else {
                const errorData = await response.json();
                setMessage(errorData.message || "Failed to change password.");
            }
        } catch (error) {
            console.error("Error changing password:", error);
            setMessage("Unexpected error occurred.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="close-button" onClick={onClose}>X</button>

                <h3>Change Password</h3>
                {message && <p>{message}</p>}

                <form onSubmit={handleSubmit}>
                    <label>
                        Current Password:
                        <input
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            required
                        />
                    </label>

                    <label>
                        New Password:
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                        />
                    </label>

                    <label>
                        Confirm New Password:
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </label>

                    <button type="submit">Change Password</button>
                </form>
            </div>
        </div>
    );
};

export default ChangePasswordPopup;
