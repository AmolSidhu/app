import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const EditPictureForm = () => {
    const [picture, setPicture] = useState(null);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({});
    const [successMessage, setSuccessMessage] = useState("");
    const location = useLocation();
    const search = location.search;

    useEffect(() => {
        const fetchPicture = async () => {
            try {
                const token = localStorage.getItem("token");
                const params = new URLSearchParams(search);
                const serial = params.get("serial");

                if (!serial) {
                    setError("Picture parameter is missing");
                    return;
                }

                const response = await fetch(`${server}/get/picture_record/${serial}`, {
                    method: "GET",
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch picture data.");
                }

                const responseData = await response.json();

                if (responseData.data) {
                    setPicture(responseData.data);
                    setFormData({
                        title: responseData.data.picture_title || "",
                        description: responseData.data.picture_description || "",
                        tags: responseData.data.picture_tags ? responseData.data.picture_tags.split(",") : [],
                        people: responseData.data.picture_people ? responseData.data.picture_people.split(",") : [],
                    });
                } else {
                    setError("No picture found.");
                }
            } catch (error) {
                setError(error.message);
            }
        };

        fetchPicture();
    }, [search]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSuccessMessage("");
        setError("");

        try {
            const token = localStorage.getItem("token");
            const serial = new URLSearchParams(search).get("serial");

            if (!serial) {
                setError("Invalid request. No picture serial found.");
                return;
            }

            const response = await fetch(`${server}/update/picture_record/${serial}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    picture_title: formData.title,
                    picture_description: formData.description,
                    tags: formData.tags.join(","),
                    people: formData.people.join(","),
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to update picture details.");
            }

            setSuccessMessage("Picture details updated successfully!");
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
            {picture && (
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

                        {/* Tags Section */}
                        <div>
                            <h4>Tags</h4>
                            {formData.tags.map((tag, index) => (
                                <div key={index}>
                                    <input
                                        type="text"
                                        value={tag}
                                        onChange={(e) => handleChange(e, "tags", index)}
                                    />
                                    <button type="button" onClick={() => handleRemoveField("tags", index)}>
                                        Remove
                                    </button>
                                </div>
                            ))}
                            <button type="button" onClick={() => handleAddField("tags")}>
                                Add Tag
                            </button>
                        </div>

                        {/* People Section */}
                        <div>
                            <h4>People</h4>
                            {formData.people.map((person, index) => (
                                <div key={index}>
                                    <input
                                        type="text"
                                        value={person}
                                        onChange={(e) => handleChange(e, "people", index)}
                                    />
                                    <button type="button" onClick={() => handleRemoveField("people", index)}>
                                        Remove
                                    </button>
                                </div>
                            ))}
                            <button type="button" onClick={() => handleAddField("people")}>
                                Add Person
                            </button>
                        </div>

                        <button type="submit">Save Changes</button>
                    </form>
                </>
            )}
        </div>
    );
};

export default EditPictureForm;
