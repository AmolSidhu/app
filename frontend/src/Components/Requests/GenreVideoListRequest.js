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
        const genreNames = data.genres.map((genre) => genre.genre);
        setGenres(genreNames);

        const initialPages = {};
        genreNames.forEach((genre) => {
          initialPages[genre] = 1;
          fetchVideosByGenre(genre, 1);
        });
        setCurrentPages(initialPages);
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
        [genre]: {
          videos: fetchedVideos,
          hasMore: data.data.has_more,
        },
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
    if (videosByGenre[genre]?.hasMore) {
      fetchVideosByGenre(genre, currentPages[genre] + 1);
    }
  };

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="video-list-container">
      {genres.map((genre, index) => (
        <div key={index} className="genre-section">
          <h2 className="genre-title">{genre}</h2>
          <div className="video-navigation">
            <button
              onClick={() => handlePrevPage(genre)}
              disabled={currentPages[genre] === 1}
              className="nav-arrow"
            >
              &#9665;
            </button>
            <div className="video-list">
              {videosByGenre[genre]?.videos.length > 0 ? (
                videosByGenre[genre].videos.map((video, index) => (
                  <div
                    key={index}
                    className="video-item"
                    onClick={() => openPopup(video.serial)}
                  >
                    <img src={video.image_url} alt={video.title} />
                  </div>
                ))
              ) : (
                <p>No videos found for this genre.</p>
              )}
            </div>
            <button
              onClick={() => handleNextPage(genre)}
              disabled={!videosByGenre[genre]?.hasMore}
              className="nav-arrow"
            >
              &#9655;
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
