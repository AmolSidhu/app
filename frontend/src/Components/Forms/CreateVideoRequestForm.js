import React, {useEffect, useState} from "react";
import server from "../Static/Constants";

function CreateVideoRequestForm() {
    const [videoTitle, setVideoTitle] = useState("");
    const [videoDescription, setVideoDescription] = useState("");
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Create Video Request";
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem("token");
        try {
            const response = await fetch(`${server}/create/video_request/`, {
                method: "POST",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    request_title: videoTitle,
                    request_description: videoDescription,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            setSuccessMessage(data.message);
            setError(null);
        } catch (error) {
            setError(error.message);
            setSuccessMessage(null);
        }
    }

    return (
        <div className="create-video-request-form">
            <h1>Create Video Request</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="videoTitle">Video Title:</label>
                    <input
                        type="text"
                        id="videoTitle"
                        value={videoTitle}
                        onChange={(e) => setVideoTitle(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="videoDescription">Video Description:</label>
                    <textarea
                        id="videoDescription"
                        value={videoDescription}
                        onChange={(e) => setVideoDescription(e.target.value)}
                        required
                    ></textarea>
                </div>
                {error && <p className="error-message">{error}</p>}
                {successMessage && <p className="success-message">{successMessage}</p>}
                <button type="submit">Submit Request</button>
            </form>
        </div>
    );
}

export default CreateVideoRequestForm;