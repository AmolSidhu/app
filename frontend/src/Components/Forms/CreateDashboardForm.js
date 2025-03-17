import React, {useEffect, useState} from "react";
import server from "../Static/Constants";

const CreateDashboardForm = () => {
    const [title, setTitle] = useState("");
    const [dataSources, setDataSources] = useState("");

    useEffect(() => {
        const fetchDataSources = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}api/data_sources/`, {
                    method: "GET",
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });
                const data = await response.json();
                setDataSources(data);
            } catch (error) {
                console.error("Error fetching data sources:", error);
            }
        };
            fetchDataSources();
        }, []);
    
    return (
        <div>
            <h1>Create Dashboard</h1>
            <form>
                <label>Title</label>
                <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
                <label>Data Sources</label>
                <select
                    value={dataSources}
                    onChange={(e) => setDataSources(e.target.value)}
                >
                    <option value="">Select Data Source</option>
                    {dataSources.map((dataSource) => (
                        <option key={dataSource.id} value={dataSource.id}>
                            {dataSource.name}
                        </option>
                    ))}
                </select>
                <button type="submit">Create Dashboard</button>
            </form>
        </div>
    );
};

export default CreateDashboardForm;

