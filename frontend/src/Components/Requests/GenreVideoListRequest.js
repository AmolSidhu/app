import React, { useState, useEffect } from "react";
import server from "../Static/Constants";
import VideoDetailPopup from "../Popups/VideoDetailPopup";

function GenreVideoListRequest() {
  const [genres, setGenres] = useState([]);
  const [error, setError] = useState(null);
  const [videosByGenre, setVideosByGenre] = useState({});
  const [selectedSerial, setSelectedSerial] = useState(null);
  const [currentPages, setCurrentPages] = useState({});

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get/genres/`, {
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
        setGenres(data.genres.map((genre) => genre.genre));
        data.genres.forEach((genre) => {
          fetchVideosByGenre(genre.genre, 1);
        });
      } catch (error) {
        setError(error.message);
      }
    };

    fetchGenres();
  }, []);

  const fetchVideosByGenre = async (genre, page) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get/videos_by_genre/${genre}?page=${page}&limit=5`, {
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

      for (let video of data.data.videos) {
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

      setVideosByGenre((prevVideosByGenre) => ({
        ...prevVideosByGenre,
        [genre]: { videos: fetchedVideos, hasMore: data.data.has_more },
      }));
      setCurrentPages((prevPages) => ({
        ...prevPages,
        [genre]: page,
      }));
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

  const handlePrevPage = (genre) => {
    if (currentPages[genre] > 1) {
      fetchVideosByGenre(genre, currentPages[genre] - 1);
    }
  };

  const handleNextPage = (genre) => {
    if (videosByGenre[genre].hasMore) {
      fetchVideosByGenre(genre, currentPages[genre] + 1);
    }
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      {genres.map((genre, index) => (
        <div key={index}>
          <h2>{genre}</h2>
          <div className="video-scroll-container">
            {videosByGenre[genre] &&
              videosByGenre[genre].videos.map((video, index) => (
                <div
                  key={index}
                  className="video-item"
                  onClick={() => openPopup(video.serial)}
                >
                  <img src={video.image_url} alt={video.title} />
                </div>
              ))}
          </div>
          <div className="pagination-controls">
            <button onClick={() => handlePrevPage(genre)} disabled={currentPages[genre] === 1}>
              Previous
            </button>
            <button onClick={() => handleNextPage(genre)} disabled={!videosByGenre[genre]?.hasMore}>
              Next
            </button>
          </div>
        </div>
      ))}
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

export default GenreVideoListRequest;
