import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const YoutubeStreamInfoRequest = () => {
    const location = useLocation();
    const search = location.search;

    const [streamInfo, setStreamInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchStreamInfo = async () => {
            const params = new URLSearchParams(search);
            const streamSerial = params.get("serial");

            if (!streamSerial) {
                setError("No stream serial provided in the URL.");
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(
                    `${server}/get/youtube_stream_data/${streamSerial}/`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: localStorage.getItem("token"),
                            "Content-Type": "application/json",
                        },
                    }
                );

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || "Failed to fetch stream info.");
                }

                const json = await response.json();
                setStreamInfo(json.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchStreamInfo();
    }, [search]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;

    return (
        <div>
            <h1>{streamInfo.title}</h1>
            <p>{streamInfo.description}</p>
        </div>
    );
};

export default YoutubeStreamInfoRequest;
