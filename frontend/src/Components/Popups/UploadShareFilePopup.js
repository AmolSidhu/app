import React, { useState } from "react";
import server from "../Static/Constants";

const UploadShareFilePopup = ({ onClose, onUploadSuccess, folderSerial = null }) => {
    const [file, setFile] = useState(null);
    const [description, setDescription] = useState("");
    const [sharable, setSharable] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) {
            alert("Please select a file to upload.");
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("file_description", description);
            formData.append("sharable", sharable ? "True" : "False");

            if (folderSerial) {
                formData.append("folder_serial", folderSerial);
            }

            const response = await fetch(`${server}/upload/file/`, {
                method: "POST",
                headers: {
                    "Authorization": localStorage.getItem("token"),
                },
                body: formData
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Failed to upload file");
            }

            alert("File uploaded successfully!");
            if (onUploadSuccess) onUploadSuccess();
            onClose();
        } catch (error) {
            console.error("Error uploading file:", error);
            alert(error.message || "Error uploading file. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Upload File</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="file"
                        onChange={(e) => setFile(e.target.files[0])}
                        required
                    />
                    <input
                        type="text"
                        placeholder="File description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />
                    <label>
                        <input
                            type="checkbox"
                            checked={sharable}
                            onChange={(e) => setSharable(e.target.checked)}
                        />
                        Sharable
                    </label>
                    <div style={{ marginTop: "10px" }}>
                        <button type="submit" disabled={loading}>
                            {loading ? "Uploading..." : "Upload"}
                        </button>
                        <button type="button" onClick={onClose}>Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UploadShareFilePopup;
