import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const ServerDataRequest = () => {
  const [patchData, setPatchData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchServerData = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get/server/patch_data/`, {
          headers: { Authorization: token },
        });

        const result = await response.json();

        if (response.ok) {
          setPatchData(result.data || {});
        } else {
          setError(result.message || "Failed to fetch patch notes.");
        }
      } catch (err) {
        console.error("Error fetching patch data:", err);
        setError("Internal error. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchServerData();
  }, []);

  if (loading) return <div>Loading patch notes...</div>;
  if (error) return <div style={{ color: "red" }}>Error: {error}</div>;

  const sortedEntries = Object.entries(patchData).sort(
    ([dateA], [dateB]) => new Date(dateB) - new Date(dateA)
  );

  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "2rem auto",
        padding: "1.5rem",
        background: "#fff",
        borderRadius: "10px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
      }}
    >
      <h2 style={{ marginBottom: "1.5rem", textAlign: "center" }}>
        Server Patch Updates
      </h2>

      {sortedEntries.length === 0 ? (
        <p>No patch notes available.</p>
      ) : (
        sortedEntries.map(([date, updates], index) => (
          <div
            key={date}
            style={{
              borderBottom: "1px solid #eee",
              paddingBottom: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            <h3 style={{ color: "#007bff" }}>
              Update {sortedEntries.length - index} — {date}
            </h3>
            <ul style={{ marginTop: "0.5rem", paddingLeft: "1.5rem" }}>
              {updates.map((item, i) => (
                <li key={i} style={{ lineHeight: "1.6" }}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  );
};

export default ServerDataRequest;
