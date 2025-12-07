import React, { useState } from "react";
import server from "../Static/Constants";

const ChangeEmailPopup = ({ onClose }) => {
    const [currentEmail, setCurrentEmail] = useState("");
    const [newEmail, setNewEmail] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/change/email/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: token,
                },
                body: JSON.stringify({
                    current_email: currentEmail,
                    new_email: newEmail,
                }),
            });

            if (response.ok) {
                setMessage("Email changed successfully.");
            } else {
                setMessage("Failed to change email.");
            }
        } catch (error) {
            setMessage("An error occurred. Please try again.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="close-button" onClick={onClose}>X</button>
                <h3>Change Email</h3>
                {message && <p>{message}</p>}
                <form onSubmit={handleSubmit}>
                    <label>
                        Current Email:
                        <input
                            type="email"
                            value={currentEmail}
                            onChange={(e) => setCurrentEmail(e.target.value)}
                            required
                        />
                    </label>
                    <label>
                        New Email:
                        <input
                            type="email"
                            value={newEmail}
                            onChange={(e) => setNewEmail(e.target.value)}
                            required
                        />
                    </label>
                    <button type="submit">Change Email</button>
                </form>
            </div>
        </div>
    );
};

export default ChangeEmailPopup;
