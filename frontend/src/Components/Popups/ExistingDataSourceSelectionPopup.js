import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const ExistingDataSourceSelectionPopup = () => {
    const [dataSources, setDataSources] = useState([]);
    const [selectedDataSource, setSelectedDataSource] = useState("");
    const [file, setFile] = useState(null);
    const [dataSourceName, setDataSourceName] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        fetchDataSources();
    }, []);

    const fetchDataSources = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}get/data_sources/`, {
                method: "GET",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });
            const result = await response.json();
            if (result.data) {
                setDataSources(result.data);
            } else {
                setMessage(result.message);
            }
        } catch (error) {
            console.error("Error fetching data sources:", error);
        }
    };

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

            const response = await fetch(`${server}upload/data_source/`, {
                method: "POST",
                headers: {
                    Authorization: token,
                },
                body: formData,
            });

            const result = await response.json();
            setMessage(result.message);
            if (response.status === 201) {
                fetchDataSources();
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            setMessage("Error uploading file.");
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-xl font-bold mb-4">Select or Upload Data Source</h1>
            <form>
                <label className="block mb-2">Select Existing Data Source:</label>
                <select
                    value={selectedDataSource}
                    onChange={(e) => setSelectedDataSource(e.target.value)}
                    className="border p-2 w-full mb-4"
                >
                    <option value="">Select Data Source</option>
                    {dataSources.map((ds) => (
                        <option key={ds.serial} value={ds.serial}>
                            {ds.data_source_name}
                        </option>
                    ))}
                </select>
            </form>

            <form onSubmit={handleUpload} className="mt-4">
                <label className="block mb-2">Upload New CSV Data Source:</label>
                <input
                    type="text"
                    placeholder="Data Source Name"
                    value={dataSourceName}
                    onChange={(e) => setDataSourceName(e.target.value)}
                    className="border p-2 w-full mb-2"
                    required
                />
                <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="border p-2 w-full mb-2"
                    required
                />
                <button
                    type="submit"
                    className="bg-blue-500 text-white p-2 rounded"
                >
                    Upload Data Source
                </button>
            </form>

            {message && <p className="mt-4 text-red-500">{message}</p>}
        </div>
    );
};

export default ExistingDataSourceSelectionPopup;