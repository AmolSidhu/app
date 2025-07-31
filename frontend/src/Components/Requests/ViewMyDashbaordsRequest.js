import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import CreateDashboardItemPopup from "../Popups/CreateDashboardItemPopup";
import UpdateDashboardItemPopup from "../Popups/UpdateDashboardItemPopup";

const ViewMyDashboardsRequest = () => {
    const [dashboards, setDashboards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState({});
    const [dashboardItems, setDashboardItems] = useState({});
    const [showPopup, setShowPopup] = useState(false);
    const [activeDashboardSerial, setActiveDashboardSerial] = useState(null);
    const [editingItemSerial, setEditingItemSerial] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "My Dashboards";
            fetchDashboards();
        }
    }, []);

    const fetchDashboards = async () => {
        try {
            const response = await fetch(`${server}/get/dashboards/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            if (response.ok) {
                const json = await response.json();
                if (json && Array.isArray(json.data)) {
                    setDashboards(json.data);
                } else {
                    console.error("Unexpected response format:", json);
                    setDashboards([]);
                }
            } else {
                const errorData = await response.json();
                console.error("Failed to fetch dashboards:", errorData.message);
                setDashboards([]);
            }
        } catch (error) {
            console.error("Error fetching dashboards:", error);
            setDashboards([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchDashboardItems = async (serial) => {
        try {
            const response = await fetch(`${server}/get/dashboard_items/${serial}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            if (response.ok) {
                const json = await response.json();
                setDashboardItems((prev) => ({
                    ...prev,
                    [serial]: json.data,
                }));
            } else {
                const errorData = await response.json();
                console.error("Failed to fetch dashboard items:", errorData.message);
            }
        } catch (error) {
            console.error("Error fetching dashboard items:", error);
        }
    };

    const toggleExpand = async (serial) => {
        setExpanded((prev) => ({
            ...prev,
            [serial]: !prev[serial],
        }));

        if (!dashboardItems[serial]) {
            await fetchDashboardItems(serial);
        }
    };

    const handleOpenPopup = (serial) => {
        setActiveDashboardSerial(serial);
        setShowPopup(true);
    };

    const handleClosePopup = () => {
        setShowPopup(false);
        if (activeDashboardSerial) {
            fetchDashboardItems(activeDashboardSerial);
        }
        setActiveDashboardSerial(null);
    };

    const handleEditItem = (dashboardSerial, itemSerial) => {
        setActiveDashboardSerial(dashboardSerial);
        setEditingItemSerial(itemSerial);
    };

    const handleCloseEditPopup = () => {
        if (activeDashboardSerial) {
            fetchDashboardItems(activeDashboardSerial);
        }
        setEditingItemSerial(null);
        setActiveDashboardSerial(null);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>My Dashboards</h1>
            {Array.isArray(dashboards) && dashboards.length > 0 ? (
                <ul>
                    {dashboards.map((dashboard) => (
                        <li key={dashboard.dashboard_serial}>
                            <h2>{dashboard.dashboard_name}</h2>
                            <p>Created on: {new Date(dashboard.date_created).toLocaleDateString()}</p>
                            <a href={`/analytics/view/?dashboard=${dashboard.dashboard_serial}`}>View Dashboard</a>
                            <br />
                            <button onClick={() => toggleExpand(dashboard.dashboard_serial)}>
                                {expanded[dashboard.dashboard_serial] ? "Collapse" : "Expand"}
                            </button>

                            {expanded[dashboard.dashboard_serial] && (
                                <div style={{ marginTop: "10px", marginLeft: "20px" }}>
                                    <h3>Dashboard Items</h3>
                                    {dashboardItems[dashboard.dashboard_serial] ? (
                                        <ul>
                                            {dashboardItems[dashboard.dashboard_serial].map((item) => (
                                                <li key={item.dashboard_item_serial}>
                                                    Type: {item.item_type}, Order: {item.item_order}
                                                    <br />
                                                    <button
                                                        onClick={() =>
                                                            handleEditItem(
                                                                dashboard.dashboard_serial,
                                                                item.dashboard_item_serial
                                                            )
                                                        }
                                                    >
                                                        Edit Item
                                                    </button>
                                                </li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <p>Loading items...</p>
                                    )}
                                    <button onClick={() => handleOpenPopup(dashboard.dashboard_serial)}>
                                        Add Dashboard Item
                                    </button>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No dashboards found.</p>
            )}

            {showPopup && activeDashboardSerial && (
                <CreateDashboardItemPopup
                    dashboardSerial={activeDashboardSerial}
                    onClose={handleClosePopup}
                />
            )}

            {editingItemSerial && activeDashboardSerial && (
                <UpdateDashboardItemPopup
                    dashboardSerial={activeDashboardSerial}
                    dashboardItemSerial={editingItemSerial}
                    onClose={handleCloseEditPopup}
                />
            )}
        </div>
    );
};

export default ViewMyDashboardsRequest;
