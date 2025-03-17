import React, {useEffect, useState} from "react";
import server from "../Static/Constants";

const EditDataSourceForm = () => {
    const [dataSources, setDataSources] = useState([]);
    const [selectedDataHeaders, setSelectedDataHeaders] = useState([]);

    useEffect(() => {
        const fetchDataSource = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}get/data_source/`, {
                    method: "GET",
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });
                const result = await response.json();
                if (result.data) {
                    setDataSources(result.data);
                }
            } catch (error) {
                console.error("Error fetching data sources:", error);
            }
        }
        fetchDataSource();
    }
    , []);

    const handleDataSourceChange = async (e) => {
        const dataSourceId = e.target.value;
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}get/data_source/${dataSourceId}/`, {
                method: "GET",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });
            const result = await response.json();
            if (result.data) {
                setSelectedDataHeaders(result.data.headers);
            }
        } catch (error) {
            console.error("Error fetching data source headers:", error);
        }
    }

    return (
        <div>
            <select onChange={handleDataSourceChange}>
                <option value="">Select Data Source</option>
                {dataSources.map((dataSource) => (
                    <option key={dataSource.id} value={dataSource.id}>
                        {dataSource.name}
                    </option>
                ))}
            </select>
            <table>
                <thead>
                    <tr>
                        {selectedDataHeaders.map((header) => (
                            <th key={header}>{header}</th>
                        ))}
                    </tr>
                </thead>
            </table>
        </div>
    );
}

export default EditDataSourceForm;