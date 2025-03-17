import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const EditVideoForm = () => {
    const [video, setVideo] = useState(null);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({});
    const [seasonOptions, setSeasonOptions] = useState([]);
    const [selectedSeason, setSelectedSeason] = useState("");
    const [episodes, setEpisodes] = useState([]);
    const [successMessage, setSuccessMessage] = useState("");
    const location = useLocation();
    const search = location.search;

    useEffect(() => {
        const fetchVideo = async () => {
            try {
                const token = localStorage.getItem("token");
                const params = new URLSearchParams(search);
                const query = params.get("serial");

                if (!query) {
                    setError("Video parameter is missing");
                    return;
                }

                const videoResponse = await fetch(`${server}/get/single_video_record/${query}`, {
                    method: "GET",
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });

                if (!videoResponse.ok) {
                    throw new Error("Failed to fetch video");
                }

                const videoData = await videoResponse.json();
                if (videoData.data) {
                    setVideo(videoData.data);
                    setFormData({
                        title: videoData.data.title || "",
                        description: videoData.data.description || "",
                        tags: videoData.data.tags ? videoData.data.tags.split(", ") : [],
                        directors: videoData.data.directors ? videoData.data.directors.split(", ") : [],
                        stars: videoData.data.stars ? videoData.data.stars.split(", ") : [],
                        writers: videoData.data.writers ? videoData.data.writers.split(", ") : [],
                        creators: videoData.data.creators ? videoData.data.creators.split(", ") : [],
                    });

                    if (videoData.data.series && videoData.data.season_metadata) {
                        setSeasonOptions(Object.keys(JSON.parse(videoData.data.season_metadata)));
                    }
                } else {
                    setError("No video found");
                }
            } catch (error) {
                setError(error.message);
            }
        };

        fetchVideo();
    }, [search]);

    useEffect(() => {
        if (selectedSeason) {
            const fetchEpisodes = async () => {
                try {
                    const token = localStorage.getItem("token");
                    const params = new URLSearchParams(search);
                    const query = params.get("serial");

                    if (!query) {
                        console.error("No video ID found.");
                        return;
                    }

                    const seasonInt = parseInt(selectedSeason, 10);
                    if (isNaN(seasonInt)) {
                        console.error("Invalid season number");
                        return;
                    }

                    const response = await fetch(`${server}/get/episode_records/${query}/${seasonInt}/`, {
                        method: "GET",
                        headers: {
                            Authorization: token,
                            "Content-Type": "application/json",
                        },
                    });

                    if (!response.ok) throw new Error("Failed to fetch episodes");

                    const data = await response.json();
                    if (data.data) {
                        setEpisodes(data.data);
                    } else {
                        setEpisodes([]);
                    }
                } catch (error) {
                    console.error(error);
                }
            };

            fetchEpisodes();
        }
    }, [selectedSeason, search]);

    const handleEpisodeChange = (e, index, field) => {
        const updatedEpisodes = [...episodes];
        updatedEpisodes[index][field] = e.target.value;
        setEpisodes(updatedEpisodes);
    };

    const handleEpisodeSave = async (episode, index) => {
        try {
            const token = localStorage.getItem("token");
            const query = new URLSearchParams(search).get("serial");

            if (!query) {
                setError("Invalid request. No video ID found.");
                return;
            }

            const response = await fetch(`${server}/update/video_episode/${query}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    current_season: episode.season,
                    current_episode: episode.episode,
                    video_serial: episode.video_serial,
                    new_episode: episode.new_episode,
                    new_season: episode.new_season,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to update episode.");
            }

            setSuccessMessage(`Episode ${episode.episode} updated successfully!`);
        } catch (error) {
            setError(error.message);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSuccessMessage("");
        setError("");

        try {
            const token = localStorage.getItem("token");
            const query = new URLSearchParams(search).get("serial");

            if (!query) {
                setError("Invalid request. No video ID found.");
                return;
            }

            const response = await fetch(`${server}/update/video_record/${query}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    title: formData.title,
                    description: formData.description,
                    tags: formData.tags.join(", "),
                    directors: formData.directors.join(", "),
                    stars: formData.stars.join(", "),
                    writers: formData.writers.join(", "),
                    creators: formData.creators.join(", "),
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to update video details.");
            }

            setSuccessMessage("Video details updated successfully!");
        } catch (error) {
            setError(error.message);
        }
    };

    const handleChange = (e, field, index) => {
        const updatedData = { ...formData };
        updatedData[field][index] = e.target.value;
        setFormData(updatedData);
    };

    const handleRemoveField = (field, index) => {
        const updatedData = { ...formData };
        updatedData[field].splice(index, 1);
        setFormData(updatedData);
    };

    const handleAddField = (field) => {
        const updatedData = { ...formData };
        updatedData[field].push("");
        setFormData(updatedData);
    };

    return (
        <div>
            {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
            {video && (
                <>
                    <form onSubmit={handleSubmit}>
                        <label>
                            Title:
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            />
                        </label>
                        <label>
                            Description:
                            <input
                                type="text"
                                name="description"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </label>

                        {["tags", "directors", "stars", "writers", "creators"].map((field) => (
                            <div key={field}>
                                <h4>{field.charAt(0).toUpperCase() + field.slice(1)}</h4>
                                {formData[field].map((item, index) => (
                                    <div key={index}>
                                        <input type="text" value={item} onChange={(e) => handleChange(e, field, index)} />
                                        <button type="button" onClick={() => handleRemoveField(field, index)}>
                                            Remove
                                        </button>
                                    </div>
                                ))}
                                <button type="button" onClick={() => handleAddField(field)}>
                                    Add {field.slice(0, -1)}
                                </button>
                            </div>
                        ))}

                        <button type="submit">Save Changes</button>
                    </form>

                    {video.series && seasonOptions.length > 0 && (
                        <div>
                            <label>
                                Season:
                                <select value={selectedSeason} onChange={(e) => setSelectedSeason(e.target.value)}>
                                    <option value="">Select a season</option>
                                    {seasonOptions.map((season) => (
                                        <option key={season} value={season}>
                                            {season}
                                        </option>
                                    ))}
                                </select>
                            </label>
                        </div>
                    )}

                    {selectedSeason && episodes.length > 0 && (
                        <div>
                            <h4>Episodes</h4>
                            <ul>
                                {episodes.map((episode, index) => (
                                    <li key={index}>
                                        <input
                                            type="number"
                                            value={episode.episode}
                                            onChange={(e) => handleEpisodeChange(e, index, "episode")}
                                        />
                                        <input
                                            type="number"
                                            value={episode.season}
                                            onChange={(e) => handleEpisodeChange(e, index, "season")}
                                        />
                                        <input
                                            type="number"
                                            value={episode.new_episode || ""}
                                            onChange={(e) => handleEpisodeChange(e, index, "new_episode")}
                                            placeholder="New Episode"
                                        />
                                        <input
                                            type="number"
                                            value={episode.new_season || ""}
                                            onChange={(e) => handleEpisodeChange(e, index, "new_season")}
                                            placeholder="New Season"
                                        />
                                        <button type="button" onClick={() => handleEpisodeSave(episode, index)}>
                                            Save
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default EditVideoForm;
