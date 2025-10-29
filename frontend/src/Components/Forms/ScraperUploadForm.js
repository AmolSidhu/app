import React, { useState } from "react";
import server from "../Static/Constants";

const ScraperUploadForm = () => {
  const [file, setFile] = useState(null);
  const [scraperName, setScraperName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    if (!file.name.endsWith(".csv")) {
      setMessage("Invalid file type. Only CSV files are allowed.");
      return;
    }

    if (!scraperName.trim()) {
      setMessage("Please enter a scraper name.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("scraper_name", scraperName);

      const response = await fetch(`${server}/create/scraper/`, {
        method: "POST",
        headers: {
          Authorization: localStorage.getItem("token"),
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || "File uploaded successfully!");
        setFile(null);
        setScraperName("");
      } else {
        setMessage(data.error || "Error uploading file.");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setMessage("Internal error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    setDownloading(true);
    setMessage("");

    try {
      const response = await fetch(`${server}/get/default_template/`, {
        method: "GET",
        headers: {
          Authorization: localStorage.getItem("token"),
        },
      });

      if (!response.ok) {
        const data = await response.json();
        setMessage(data.error || "Failed to download template.");
        setDownloading(false);
        return;
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "default_template.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setMessage("Template downloaded successfully!");
    } catch (err) {
      console.error("Download error:", err);
      setMessage("Error downloading template.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "500px", margin: "auto" }}>
      <h2>Upload Scraper File</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "10px" }}>
          <label>Scraper Name:</label>
          <input
            type="text"
            value={scraperName}
            onChange={(e) => setScraperName(e.target.value)}
            placeholder="Enter scraper name"
            style={{ width: "100%", padding: "5px", marginTop: "5px" }}
          />
        </div>

        <div>
          <input type="file" accept=".csv" onChange={handleFileChange} />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{ marginTop: "10px" }}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      <hr style={{ margin: "20px 0" }} />

      <button onClick={handleDownloadTemplate} disabled={downloading}>
        {downloading ? "Downloading..." : "Download Template"}
      </button>

      {message && <p style={{ marginTop: "15px" }}>{message}</p>}
    </div>
  );
};

export default ScraperUploadForm;