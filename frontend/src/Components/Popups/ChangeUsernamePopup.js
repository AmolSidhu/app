import React, { useState } from "react";
import server from "../Static/Constants";

const ChangeUsernamePopup = ({ onClose }) => {
    const [newUsername, setNewUsername] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/change/username/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: token,
                },
                body: JSON.stringify({
                    new_username: newUsername,
                }),
            });

            if (response.ok) {
                setMessage("Username changed successfully.");
            } else {
                const errorData = await response.json();
                setMessage(errorData.message || "Failed to change username.");
            }
        } catch (error) {
            console.error("Error changing username:", error);
            setMessage("Unexpected error occurred.");
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="close-button" onClick={onClose}>X</button>
                <h3>Change Username</h3>
                {message && <p>{message}</p>}

                <form onSubmit={handleSubmit}>
                    <label>
                        New Username:
                        <input
                            type="text"
                            value={newUsername}
                            onChange={(e) => setNewUsername(e.target.value)}
                            required
                        />
                    </label>

                    <button type="submit">Change Username</button>
                </form>
            </div>
        </div>
    );
};

export default ChangeUsernamePopup;