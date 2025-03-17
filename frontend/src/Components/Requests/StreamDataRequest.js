import React, { useState, useEffect } from "react";
import server from "../Static/Constants";
import { useLocation, Link } from "react-router-dom";

function StreamDataRequest() {
  const [streams, setStreams] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const search = location.search;

  useEffect(() => {
    const fetchStreamData = async () => {
      try {
        const params = new URLSearchParams(search);
        const query = params.get("serial");
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get/next_previous_episode/${query}/`, {
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
        setStreams(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchStreamData();
  }, [search]);

  return (
    <div>
      {error ? (
        <p>Error: {error}</p>
      ) : (
        <div>
          {streams.map((stream, index) => (
            <div key={index}>
              <div>
                {stream.previous_video_serial && stream.previous_season && stream.previous_episode && (
                  <Link
                    to={`?serial=${stream.previous_video_serial}`}
                    className="previous-episode"
                  >
                    ← Previous Episode Season {stream.previous_season} Episode {stream.previous_episode}
                  </Link>
                )}

                {stream.next_video_serial && stream.next_season && stream.next_episode && (
                  <Link
                    to={`?serial=${stream.next_video_serial}`}
                    className="next-episode"
                  >
                    Next Episode Season {stream.next_season} Episode {stream.next_episode} →
                  </Link>
                )}
              </div>

              <div>
                <h3>{stream.title}</h3>
                <p>{stream.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StreamDataRequest;
