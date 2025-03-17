import React, {useState, useEffect} from "react";
import server from "../Static/Constants";

const UploadDataSourceForm = () => {
    const [file, setFile] = useState(null);
    const [dataSourceName, setDataSourceName] = useState("");
    const [message, setMessage] = useState("");

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.name.endsWith(".csv")) {
            setFile(selectedFile);
            setMessage("");
        } else {
            setMessage("Please upload a valid CSV file.");
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file || !dataSourceName) {
            setMessage("Both file and data source name are required.");
            return;
        }
        try {
            const token = localStorage.getItem("token");
            const formData = new FormData();
            formData.append("file", file);
            formData.append("data_source_name", dataSourceName);

            const response = await fetch(`${server}/upload/data_source/`, {
                method: "POST",
                headers: {
                    Authorization: token,
                },
                body: formData,
            });
            const result = await response.json();
            setMessage(result.message);
        } catch (error) {
            console.error("Error uploading data source:", error);
        }
    };

    return (
        <form onSubmit={handleUpload}>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <input
                type="text"
                placeholder="Data Source Name"
                value={dataSourceName}
                onChange={(e) => setDataSourceName(e.target.value)}
            />
            <button type="submit">Upload</button>
            <p>{message}</p>
        </form>
    );
};

export default UploadDataSourceForm;