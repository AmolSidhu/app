import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const ViewAllScrapersRequest = () => {
  const [scrapers, setScrapers] = useState([]);
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchScrapers = async () => {
      try {
        const response = await fetch(`${server}/get/all_scraper_statuses/`, {
          method: "GET",
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch scrapers");
        }

        const data = await response.json();

        const scraperArray = Object.entries(data.scrapers || {}).map(
          ([serial, info]) => ({
            serial,
            ...info,
          })
        );

        setScrapers(scraperArray);
      } catch (error) {
        console.error("Error fetching scrapers:", error);
        setErrorMessage("Error fetching scrapers");
      }
    };

    fetchScrapers();
  }, []);

  const handleRunScraper = async (serial) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    setLoading(true);

    try {
      const response = await fetch(`${server}/trigger/mtg_f2f_scraper/${serial}/`, {
        method: "POST",
        headers: {
          Authorization: localStorage.getItem("token"),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to trigger scraper");
      }

      setSuccessMessage(`Scraper ${serial} triggered successfully.`);
    } catch (error) {
      console.error("Error triggering scraper:", error);
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>All Scrapers</h1>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
      {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

      {scrapers.length === 0 ? (
        <p>No scrapers found.</p>
      ) : (
        <ul>
          {scrapers.map((scraper) => (
            <li key={scraper.serial} style={{ marginBottom: "1em" }}>
              <strong>{scraper.file_name}</strong> — {scraper.status} <br />
              <small>
                Created: {new Date(scraper.create_date).toLocaleString()}
              </small>
              <br />

              <button
                onClick={() => handleRunScraper(scraper.serial)}
                disabled={loading || scraper.status !== "validated"}
                style={{
                  marginTop: "0.5em",
                  marginRight: "0.5em",
                  padding: "0.4em 0.8em",
                  backgroundColor:
                    scraper.status === "validated" ? "#4CAF50" : "#aaa",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor:
                    scraper.status === "validated" && !loading
                      ? "pointer"
                      : "not-allowed",
                }}
              >
                {loading ? "Processing..." : "Run Scraper"}
              </button>

              <a
                href={`/mtg/viewscraperhistory/?serial=${scraper.serial}`}
                style={{
                  display: "inline-block",
                  padding: "0.4em 0.8em",
                  backgroundColor: "#2196F3",
                  color: "white",
                  borderRadius: "4px",
                  textDecoration: "none",
                  cursor: "pointer",
                }}
              >
                View Previous Sessions
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ViewAllScrapersRequest;