import React, { useState } from "react";
import server from "../Static/Constants";

const VideoSearchPopup = () => {
  const [searchRows, setSearchRows] = useState([
    { query: "", searchType: "Genre", matchType: "Exact Match" },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addSearchRow = () => {
    setSearchRows([...searchRows, { query: "", searchType: "Genre", matchType: "Exact Match" }]);
  };

  const handleInputChange = (index, field, value) => {
    const updatedRows = [...searchRows];
    updatedRows[index][field] = value;
    setSearchRows(updatedRows);
  };

  const removeSearchRow = (index) => {
    const updatedRows = searchRows.filter((_, i) => i !== index);
    setSearchRows(updatedRows);
  };

  const handleSearch = async () => {
    const token = localStorage.getItem("token");
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${server}/generate/video_query/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token,
        },
        body: JSON.stringify({ searchRows }),
      });

      if (response.status === 201) {
        const data = await response.json();
        const searchId = data.data;
        window.location.href = `/video/search/?searchId=${searchId}`;
      } else {
        setError("Failed to perform search. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {searchRows.map((row, index) => (
        <div key={index} style={{ display: "flex", alignItems: "center", marginBottom: "10px" }}>
          <input
            type="text"
            placeholder="Search Query"
            value={row.query}
            onChange={(e) => handleInputChange(index, "query", e.target.value)}
            style={{ marginRight: "10px" }}
          />
          <select
            value={row.searchType}
            onChange={(e) => handleInputChange(index, "searchType", e.target.value)}
            style={{ marginRight: "10px" }}
          >
            <option value="Genre">Genre</option>
            <option value="Star">Star</option>
            <option value="Writer">Writer</option>
            <option value="Director">Director</option>
            <option value="Creator">Creator</option>
          </select>
          <select
            value={row.matchType}
            onChange={(e) => handleInputChange(index, "matchType", e.target.value)}
            style={{ marginRight: "10px" }}
          >
            <option value="Exact Match">Exact Match</option>
            <option value="Similar Match">Similar Match</option>
          </select>
          <button onClick={() => removeSearchRow(index)} style={{ marginRight: "10px" }}>-</button>
        </div>
      ))}
      <button onClick={addSearchRow} style={{ marginRight: "10px" }}>+</button>
      <button onClick={handleSearch} disabled={loading}>
        {loading ? "Searching..." : "Search"}
      </button>
      {error && <div style={{ color: "red", marginTop: "10px" }}>{error}</div>}
    </div>
  );
};

export default VideoSearchPopup;
