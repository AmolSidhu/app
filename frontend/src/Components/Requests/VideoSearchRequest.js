import React, { useState, useEffect } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

function VideoSearchRequest() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);
  const location = useLocation();
  const search = location.search;
  const params = new URLSearchParams(search);
  const query = params.get("searchId");

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/fetch/video_search/${query}/`, {
          method: "GET",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const responseData = await response.json();

        const videos = responseData.data;

        if (!Array.isArray(videos)) {
          throw new Error("API response 'data' is not an array");
        }

        const fetchedVideos = [];

        for (let video of videos) {
          try {
            const thumbnailResponse = await fetch(`${server}/get/video_thumbnail/${video.serial}`, {
              method: "GET",
              headers: {
                Authorization: token,
              },
            });

            if (!thumbnailResponse.ok) {
              throw new Error(`Thumbnail fetch error! Status: ${thumbnailResponse.status}`);
            }

            const thumbnailBlob = await thumbnailResponse.blob();
            const thumbnailUrl = URL.createObjectURL(thumbnailBlob);

            fetchedVideos.push({
              ...video,
              image_url: thumbnailUrl,
            });
          } catch (thumbnailError) {
            console.error(`Error fetching thumbnail for video ${video.serial}:`, thumbnailError);
            fetchedVideos.push(video);
          }
        }

        setVideos(fetchedVideos);
      } catch (error) {
        console.error("Error fetching videos:", error);
        setError(error.message);
      }
    };

    fetchVideos();
  }, [query]);

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Video List</h1>
      <div
        style={{
          display: "flex",
          flexWrap: "nowrap",
          overflowX: "auto",
          gap: "15px",
        }}
      >
        {videos.map((video, index) => (
          <div
            key={index}
            style={{ minWidth: "200px", cursor: "pointer" }}
            onClick={() => openPopup(video.serial)}
          >
            <img
              src={video.image_url || "https://via.placeholder.com/200"}
              alt={video.title}
              style={{ width: "100%", borderRadius: "8px" }}
            />
            <div style={{ textAlign: "center", marginTop: "8px" }}>
              <strong>{video.title}</strong>
              <p style={{ fontSize: "12px", color: "#555" }}>{video.description}</p>
            </div>
          </div>
        ))}
      </div>
      {selectedSerial && (
        <div className="popup">
          <div className="popup-inner">
            <button onClick={closePopup}>Close</button>
            <VideoDetailPopup serial={selectedSerial} onClose={closePopup} />
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoSearchRequest;
