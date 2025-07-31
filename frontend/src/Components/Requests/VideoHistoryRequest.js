import React, { useState, useEffect } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";

function VideoHistoryRequest() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchVideos(currentPage);
  }, [currentPage]);

  const fetchVideos = async (page) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get/recently_viewed_videos/?page=${page}&limit=5`, {
        method: "GET",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const { data } = await response.json();
      const fetchedVideos = [];

      for (let video of data.videos) {
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
      setHasMore(data.has_more);
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

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (hasMore) {
      setCurrentPage(currentPage + 1);
    }
  };

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  if (videos.length === 0) {
    return (
      <div className="video-list-container">
        <h1>Video History</h1>
        <p>No recently viewed videos found.</p>
      </div>
    );
  }

  return (
    <div className="video-list-container">
      <h1>Video History</h1>
      <div className="video-navigation">
        <button onClick={handlePrevPage} disabled={currentPage === 1} className="nav-arrow">
          &#9665;
        </button>
        <div className="video-list">
          {videos.map((video, index) => (
            <div
              key={index}
              className="video-item"
              onClick={() => openPopup(video.serial)}
            >
              <img src={video.image_url} alt={video.title} />
            </div>
          ))}
        </div>
        <button onClick={handleNextPage} disabled={!hasMore} className="nav-arrow">
          &#9655;
        </button>
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

export default VideoHistoryRequest;
