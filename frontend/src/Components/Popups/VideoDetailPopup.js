import React, { useState, useEffect } from "react";
import server from "../Static/Constants";

function VideoDetailPopup({ serial, onClose }) {
  const [video, setVideo] = useState(null);
  const [error, setError] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [hoverSubmenu, setHoverSubmenu] = useState(null);

  const fetchVideo = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get/video_data/${serial}`, {
        method: "GET",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setVideo(data);

      if (data.series && data.season_metadata) {
        const firstSeason = Object.keys(data.season_metadata)[0];
        setSelectedSeason(firstSeason);
        fetchEpisodes(firstSeason);
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const fetchEpisodes = async (season) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get/episode_data/${serial}/${season}`, {
        method: "GET",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setEpisodes(data.episodes);
    } catch (error) {
      console.error("Error fetching episodes:", error);
    }
  };

  const handleSeasonChange = (event) => {
    const season = event.target.value;
    setSelectedSeason(season);
    fetchEpisodes(season);
  };

  const handleFavouriteToggle = async () => {
    const token = localStorage.getItem("token");
    const action = video.favourites ? "remove" : "add";

    try {
      const response = await fetch(`${server}/update/favourite_videos/${serial}/`, {
        method: "POST",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action }),
      });

      if (!response.ok) throw new Error("Failed to update favourites");

      setVideo((prevData) => ({
        ...prevData,
        favourites: !prevData.favourites,
      }));
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddToCustomAlbum = async (listSerial) => {
    const token = localStorage.getItem("token");

    try {
      const response = await fetch(`${server}/add/video/custom_list/${serial}/${listSerial}/`, {
        method: "POST",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ list_serial: listSerial }),
      });

      if (!response.ok) throw new Error("Failed to add to custom album");

      console.log(`Successfully added to custom album ${listSerial}`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemoveFromCustomAlbum = async (listSerial) => {
    const token = localStorage.getItem("token");

    try {
      const response = await fetch(`${server}/delete/video/custom_list/${serial}/${listSerial}/`, {
        method: "DELETE",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ list_serial: listSerial }),
      });

      if (!response.ok) throw new Error("Failed to remove from custom album");

      console.log(`Successfully removed from custom album ${listSerial}`);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchVideo(); // eslint-disable-next-line
  }, [serial]);

  if (error) {
    return (
      <div className="popup">
        <div className="popup-inner">
          <button onClick={onClose}>Close</button>
          <p>Error: {error}</p>
        </div>
      </div>
    );
  } else if (video) {
    return (
      <div className="popup">
        <div className="popup-inner">
          <button onClick={onClose}>Close</button>

          <div className="menu-container">
            <button onClick={() => setMenuOpen(!menuOpen)} className="menu-btn">⋮</button>
            {menuOpen && (
              <div className="menu-dropdown">
                <button onClick={handleFavouriteToggle}>
                  {video.favourites ? "Remove from Favourites" : "Add to Favourites"}
                </button>
                <div
                  className="submenu"
                  onMouseEnter={() => setHoverSubmenu("add")}
                  onMouseLeave={() => setHoverSubmenu(null)}
                >
                  Add to Custom Album
                  {hoverSubmenu === "add" && (
                    <div className="submenu-dropdown">
                      {video.not_in_custom_album.slice(0, 5).map((album, index) => (
                        <button key={index} onClick={() => handleAddToCustomAlbum(album.list_serial)}>
                          {album.list_name}
                        </button>
                      ))}
                      {video.not_in_custom_album.length > 5 && <div>Scroll for more...</div>}
                    </div>
                  )}
                </div>
                <div
                  className="submenu"
                  onMouseEnter={() => setHoverSubmenu("remove")}
                  onMouseLeave={() => setHoverSubmenu(null)}
                >
                  Remove from Custom Album
                  {hoverSubmenu === "remove" && (
                    <div className="submenu-dropdown">
                      {video.in_custom_album.slice(0, 5).map((album, index) => (
                        <button key={index} onClick={() => handleRemoveFromCustomAlbum(album.list_serial)}>
                          {album.list_name}
                        </button>
                      ))}
                      {video.in_custom_album.length > 5 && <div>Scroll for more...</div>}
                    </div>
                  )}
                </div>
                <button onClick={() => window.location.href = `/edit-video/${serial}`}>Edit Video</button>
              </div>
            )}
          </div>

          <div>
            <h2>{video.video_name}</h2>
            {video.video_genres && video.video_genres.length > 0 && (
              <p>Tags: {video.video_genres.join(", ")}</p>
            )}
            {video.video_directors && video.video_directors.length > 0 && (
              <p>Directors: {video.video_directors.join(", ")}</p>
            )}
            {video.video_writers && video.video_writers.length > 0 && (
              <p>Writers: {video.video_writers.join(", ")}</p>
            )}
            {video.video_stars && video.video_stars.length > 0 && (
              <p>Stars: {video.video_stars.join(", ")}</p>
            )}
            {video.video_creators && video.video_creators.length > 0 && (
              <p>Creators: {video.video_creators.join(", ")}</p>
            )}
            <p>Description: {video.video_description}</p>
            <p>Rating: {video.video_rating}</p>
            {video.series && video.season_metadata && (
              <div>
                <h3>Select Season:</h3>
                <select onChange={handleSeasonChange} value={selectedSeason}>
                  {Object.keys(video.season_metadata).map((season) => (
                    <option key={season} value={season}>
                      Season {season}
                    </option>
                  ))}
                </select>
                {episodes.length > 0 && (
                  <div>
                    <h3>Episodes:</h3>
                    <ul>
                      {episodes.map((episode) => (
                        <li key={episode.video_serial}>
                          {episode.episode} -{" "}
                          <a href={`/video/stream/?serial=${episode.video_serial}`}>
                            Play
                          </a>
                          {episode.resume && (
                            <>
                              {" "}or{" "}
                              <a href={`/video/stream/?serial=${episode.video_serial}&resume=true`}>
                                Resume
                              </a>
                            </>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            <a href={`/video/stream/?serial=${video.serial}`}>Watch Video</a>
            <br />
            {video.resume && (
              <a href={`/video/stream/?serial=${video.serial}&resume=true`}>
                Resume
              </a>
            )}
          </div>
        </div>
      </div>
    );
  } else {
    return null;
  }
}

export default VideoDetailPopup;
