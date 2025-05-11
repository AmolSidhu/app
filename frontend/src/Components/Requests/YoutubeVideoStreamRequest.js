import React, { useEffect, useRef } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const YoutibeVideoStreamRequest = () => {
  const videoRef = useRef(null);
  const location = useLocation();
  const search = location.search;

  useEffect(() => {
    const videoElement = videoRef.current;

    if (videoElement) {
      const params = new URLSearchParams(search);
      const serial = params.get("serial");
      const token = localStorage.getItem("token");
      const src = `${server}/watch/youtube_video/${serial}/${token}/`;

      const vjsPlayer = videojs(videoElement, {
        controls: true,
        autoplay: false,
        preload: "auto",
        fluid: true,
        sources: [
          {
            src: src,
            type: "video/mp4",
          },
        ],
      });

      vjsPlayer.ready(() => {
        fetch(src, {
          method: "GET",
          headers: {
            Authorization: token,
          },
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to fetch video stream");
            }

            const resumeTime = parseFloat(response.headers.get("Resume-Time")) || 0;

            if (resumeTime > 0) {
              vjsPlayer.currentTime(resumeTime);
            }
          })
          .catch((error) => {
            console.error("Error fetching resume time from headers:", error.message);
          });

        const updatePlaybackTime = () => {
          const currentTime = vjsPlayer.currentTime();
          fetch(`${server}/update/youtube_playback_time/${serial}/`, {
            method: "POST",
            headers: {
              Authorization: token,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              serial: serial,
              currentTime: currentTime,
            }),
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error("Failed to update playback time");
              }
            })
            .catch((error) => {
              console.error("Error updating playback time:", error.message);
            });
        };

        const timerId = setInterval(updatePlaybackTime, 5000);

        return () => {
          clearInterval(timerId);
          if (vjsPlayer) {
            vjsPlayer.dispose();
          }
        };
      });
    }
  }, [search]);

  return (
    <div>
      <div data-vjs-player>
        <video ref={videoRef} className="video-js vjs-big-play-centered" />
      </div>
    </div>
  );
};

export default YoutibeVideoStreamRequest;
