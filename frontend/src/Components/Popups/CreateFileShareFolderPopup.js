import React, { useState} from "react";
import server from "../Static/Constants";

const CreateFileShareFolderPopup = ({ onClose, onCreateSuccess }) => {
    const [folderName, setFolderName] = useState("");
    const [description, setDescription] = useState("");
    const [sharable, setSharable] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!folderName) {
            alert("Please enter a folder name.");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(`${server}/create/upload_folder/`, {
                method: "POST",
                headers: {
                    "Authorization": localStorage.getItem("token") || "",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    folder_name: folderName,
                    folder_description: description,
                    sharable: sharable ? "True" : "False"
                })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Failed to create folder");
            }

            alert("Folder created successfully!");
            onCreateSuccess();
            onClose();
        } catch (error) {
            console.error("Error creating folder:", error);
            alert(error.message || "Error creating folder. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Create New Folder</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Folder Name"
                        value={folderName}
                        onChange={(e) => setFolderName(e.target.value)}
                        required
                    />
                    <textarea
                        placeholder="Description"
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
                    <button type="submit" disabled={loading}>
                        {loading ? "Creating..." : "Create Folder"}
                    </button>
                    <button type="button" onClick={onClose} disabled={loading}>
                        Cancel
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateFileShareFolderPopup;
