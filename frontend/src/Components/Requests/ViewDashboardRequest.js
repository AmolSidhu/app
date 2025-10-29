import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const ViewDashboardRequest = () => {
    const location = useLocation();
    const search = location.search;
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchDashboardData = async () => {
        const params = new URLSearchParams(search);
        const dashboardSerial = params.get("dashboard");

        if (!dashboardSerial) {
            setError("No dashboard serial provided in the URL.");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${server}/get/dashboard_item_serials/${dashboardSerial}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Failed to fetch dashboard items.");
            }

            const json = await response.json();
            const items = json.dashboard_items;

            const itemDetails = await Promise.all(
                Object.keys(items).map(async (itemSerial) => {
                    try {
                        const res = await fetch(
                            `${server}/get/dashboard_item/${dashboardSerial}/${itemSerial}/`,
                            {
                                method: "GET",
                                headers: {
                                    Authorization: localStorage.getItem("token"),
                                    "Content-Type": "application/json",
                                },
                            }
                        );

                        if (!res.ok) {
                            const err = await res.json();
                            console.error(`Error fetching item ${itemSerial}: ${err.message}`);
                            return null;
                        }

                        const itemJson = await res.json();
                        return {
                            serial: itemSerial,
                            ...itemJson.data,
                        };
                    } catch (error) {
                        console.error(`Error fetching item ${itemSerial}:`, error);
                        return null;
                    }
                })
            );

            const filteredItems = itemDetails.filter((item) => item !== null);

            setDashboardData({
                dashboardSerial,
                items: filteredItems,
            });
        } catch (err) {
            setError(err.message || "An unknown error occurred.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
    }, [search]);

    if (loading) return <div>Loading Dashboard...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>Dashboard: {dashboardData.dashboardSerial}</h2>
            {dashboardData.items.map((item, index) => (
                <div key={index} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
                    <h3>{item.data_item_name} ({item.item_type})</h3>
                    <p>{item.data_item_description}</p>
                    
                    {item.item_type === "Graph" && (
                        <div>
                            <strong>Graph:</strong> {item.graph_title}<br />
                            X: {item.column_1}, Y: {item.column_2}, Type: {item.current_graph_type}
                        </div>
                    )}
                    
                    {item.item_type === "Table" && (
                        <div>
                            <strong>Table:</strong>
                            <ul>
                                {item.data_lines.map(line => (
                                    <li key={line.serial}>
                                        {line.column_name} (Order: {line.column_order}) - {line.operation}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {item.item_type === "Text" && (
                        <div>
                            <strong>{item.text_header}</strong>
                            <p>{item.text_body}</p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default ViewDashboardRequest;