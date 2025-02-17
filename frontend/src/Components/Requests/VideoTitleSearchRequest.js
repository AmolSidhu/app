import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const VideoTitleSearchRequest = () => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/video/search/v/?title=${query}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="search-form">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
        className="search-input"
      />
      <button type="submit" className="search-button">
        Search
      </button>
    </form>
  );
};

export default VideoTitleSearchRequest;
