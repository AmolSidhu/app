import React, { useState, useEffect } from "react";
import VideoDetailPopup from "../Popups/VideoDetailPopup";
import server from "../Static/Constants";

function CustomVideoListRequest() {
  const [videoLists, setVideoLists] = useState([]);
  const [error, setError] = useState(null);
  const [videoByList, setVideoByList] = useState({});
  const [selectedSerial, setSelectedSerial] = useState(null);
  const [currentPages, setCurrentPages] = useState({});

  useEffect(() => {
    const fetchLists = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get/custom_video_lists/`, {
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
        const lists = Array.isArray(data) ? data : data.data;
        setVideoLists(lists);

        const initialPages = {};
        lists.forEach((videoList) => {
          initialPages[videoList.list_name] = 1;
          fetchVideosByList(videoList.list_name, videoList.list_serial, 1);
        });
        setCurrentPages(initialPages);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchLists();
  }, []);

  const fetchVideosByList = async (list_name, list_serial, page) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${server}/get/custom_list_videos/${list_serial}?page=${page}&limit=5`,
        {
          method: "GET",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      const fetchedVideos = [];

      if (data && data.data && Array.isArray(data.data.videos)) {
        for (let video of data.data.videos) {
          try {
            const thumbnailResponse = await fetch(
              `${server}/get/video_thumbnail/${video.video_serial}`,
              {
                method: "GET",
                headers: {
                  Authorization: token,
                },
              }
            );

            if (!thumbnailResponse.ok) {
              throw new Error(
                `Thumbnail fetch error! Status: ${thumbnailResponse.status}`
              );
            }

            const thumbnailBlob = await thumbnailResponse.blob();
            const thumbnailUrl = URL.createObjectURL(thumbnailBlob);

            fetchedVideos.push({
              ...video,
              image_url: thumbnailUrl,
            });
          } catch (thumbnailError) {
            console.error(
              `Error fetching thumbnail for video ${video.video_serial}:`,
              thumbnailError
            );
            fetchedVideos.push(video);
          }
        }

        setVideoByList((prev) => ({
          ...prev,
          [list_name]: {
            videos: fetchedVideos,
            hasMore: data.data.has_more,
          },
        }));
        setCurrentPages((prev) => ({
          ...prev,
          [list_name]: page,
        }));
      }
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

  const handlePrevPage = (videoList) => {
    const list_serial = videoLists.find((list) => list.list_name === videoList)
      .list_serial;
    if (currentPages[videoList] > 1) {
      fetchVideosByList(videoList, list_serial, currentPages[videoList] - 1);
    }
  };

  const handleNextPage = (videoList) => {
    const list_serial = videoLists.find((list) => list.list_name === videoList)
      .list_serial;
    if (videoByList[videoList]?.hasMore) {
      fetchVideosByList(videoList, list_serial, currentPages[videoList] + 1);
    }
  };

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="video-list-container">
      <h1>Custom Video Lists</h1>
      {videoLists.map((videoList, index) => (
        <div key={index} className="genre-section">
          <h2 className="genre-title">{videoList.list_name}</h2>
          <div className="video-navigation">
            <button onClick={() => handlePrevPage(videoList.list_name)} disabled={currentPages[videoList.list_name] === 1} className="nav-arrow">
              &#9665;
            </button>
            <div className="video-list">
              {videoByList[videoList.list_name] &&
                videoByList[videoList.list_name].videos.map((video, index) => (
                  <div
                    key={index}
                    className="video-item"
                    onClick={() => openPopup(video.video_serial)}
                  >
                    <img src={video.image_url} alt={video.title} />
                  </div>
                ))}
            </div>
            <button onClick={() => handleNextPage(videoList.list_name)} disabled={!videoByList[videoList.list_name]?.hasMore} className="nav-arrow">
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

export default CustomVideoListRequest;
