import React, { useState, useEffect } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";

function DefaultVideoListRequest() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get/videos/?page=${page}&limit=5`, {
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

    fetchVideos();
  }, [page]);

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (hasMore) {
      setPage(page + 1);
    }
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Video List</h1>
      <div
        style={{
          display: 'flex',
          flexWrap: 'nowrap',
          overflowX: 'auto',
          gap: '15px'
        }}
      >
        {videos.map((video, index) => (
          <div
            key={index}
            style={{ minWidth: '200px', cursor: 'pointer' }}
            onClick={() => openPopup(video.serial)}
          >
            <img
              src={video.image_url}
              alt={video.title}
              style={{ width: '100%', borderRadius: '8px' }}
            />
          </div>
        ))}
      </div>
      <div className="pagination-controls">
        <button onClick={handlePrevPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage} disabled={!hasMore}>Next</button>
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

export default DefaultVideoListRequest;
