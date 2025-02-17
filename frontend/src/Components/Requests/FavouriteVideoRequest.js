import React, { useState, useEffect } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";

function FavouriteVideoRequest() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get/favourite_videos/`, {
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
      const fetchedVideos = [];

      for (let video of data.data) {
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
      setError(error.message);
    }
  };

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  if (videos.length === 0) {
    return (
      <div className="video-list-container">
        <h1 className="page-title">Favourites</h1>
        <p className="empty-message">You don't have any favourited videos. Add some videos to your favourites.</p>
      </div>
    );
  }

  return (
    <div className="video-list-container">
      <h1 className="page-title">Favourites</h1>
      <div className="video-grid-container">
        {videos.map((video, index) => (
          <div key={index} className="video-grid-item" onClick={() => openPopup(video.serial)}>
            <img src={video.image_url} alt={video.title} />
          </div>
        ))}
      </div>
      {selectedSerial && (
        <div className="popup">
          <div className="popup-inner">
            <button onClick={closePopup} className="popup-close-btn">Close</button>
            <VideoDetailPopup serial={selectedSerial} onClose={closePopup} />
          </div>
        </div>
      )}
    </div>
  );
}

export default FavouriteVideoRequest;
