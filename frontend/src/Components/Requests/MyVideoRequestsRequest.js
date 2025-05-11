import React, { useState, useEffect } from 'react';
import server from "../Static/Constants";

function MyVideoRequestsRequest() {
    const [requests, setRequests] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "My Video Requests";
            fetchRequests(token);
        }
    }, []);

    const fetchRequests = async (token) => {
        try {
            const response = await fetch(`${server}/get/video_requests/`, {
                method: "GET",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.data) {
                setRequests(data.data);
            } else {
                setRequests([]);
            }
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div className="my-video-requests">
            <h1>My Video Requests</h1>
            {error && <p className="error">{error}</p>}
            
            {requests && requests.length === 0 ? (
                <p>No video requests found.</p>
            ) : (
                <ul>
                    {requests?.map((request, index) => (
                        <li key={index}>
                            <h2>{request.request_title}</h2>
                            <p>{request.request_description}</p>
                            <p>Status: {request.request_status}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default MyVideoRequestsRequest;
