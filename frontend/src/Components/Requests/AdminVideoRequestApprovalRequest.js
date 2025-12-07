import React, { useEffect, useState } from 'react';
import server from '../Static/Constants';

const AdminVideoRequestApprovalRequest = () => {
    const [statuses, setStatuses] = useState([]);
    const [requestData, setRequestData] = useState({});
    const [loading, setLoading] = useState(true);

    const authHeaders = {
        "Authorization": localStorage.getItem("token"),
        "Admin-Token": localStorage.getItem("adminToken"),
    };

    const loadStatuses = async () => {
        try {
            const res = await fetch(`${server}/admins/video_request_options/`, {
                method: "GET",
                headers: authHeaders
            });

            const data = await res.json();
            const options = data?.data || [];
            setStatuses(options);
            return options;
        } catch (err) {
            console.error("Failed to load status options:", err);
            return [];
        }
    };

    const loadRequestsForStatus = async (status) => {
        try {
            const res = await fetch(`${server}/admins/video_requests/${status}/`, {
                method: "GET",
                headers: authHeaders
            });

            const data = await res.json();
            return Object.values(data?.data || {});
        } catch (err) {
            console.error(`Failed to load requests for ${status}:`, err);
            return [];
        }
    };

    useEffect(() => {
        const init = async () => {
            setLoading(true);

            const options = await loadStatuses();

            const allRequestData = {};
            for (const status of options) {
                allRequestData[status] = await loadRequestsForStatus(status);
            }

            setRequestData(allRequestData);
            setLoading(false);
        };

        init();
    }, []);

    const updateStatus = async (serial, newStatus) => {
        try {
            await fetch(`${server}/admins/review_video_request/${serial}/`, {
                method: "PATCH",
                headers: {
                    ...authHeaders,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    request_status: newStatus
                }),
            });

            const refreshedData = {};
            for (const status of statuses) {
                refreshedData[status] = await loadRequestsForStatus(status);
            }

            setRequestData(refreshedData);

        } catch (err) {
            console.error("Failed to update status:", err);
        }
    };

    if (loading) return <p>Loading...</p>;

    return (
        <div style={{ display: "flex", gap: "20px", padding: "20px" }}>
            {statuses.map((status) => (
                <div key={status} style={{ width: "300px" }}>
                    <h2>{status}</h2>

                    <div style={{ border: "1px solid #aaa", padding: "10px" }}>
                        {requestData[status]?.length === 0 && (
                            <p>No requests in this status.</p>
                        )}

                        {requestData[status]?.map((req) => (
                            <div
                                key={req.serial}
                                style={{
                                    marginBottom: "15px",
                                    padding: "5px",
                                    borderBottom: "1px solid #ccc"
                                }}
                            >
                                <p><b>{req.requeset_title}</b></p>
                                <p>User: {req.username}</p>
                                <p>Date: {req.request_date}</p>
                                <p>{req.request_description}</p>

                                <select
                                    value={status}
                                    onChange={(e) =>
                                        updateStatus(req.serial, e.target.value)
                                    }
                                >
                                    {statuses.map((s) => (
                                        <option key={s} value={s}>
                                            {s}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default AdminVideoRequestApprovalRequest;
