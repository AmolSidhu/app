import React, { useState } from "react";
import server from "../Static/Constants";

const ArticleFileUploadForm = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    const allowedExtensions = [".txt", ".md", ".json", ".html", ".jsonl"];
    const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setMessage(`Invalid file type. Allowed: ${allowedExtensions.join(", ")}`);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${server}/upload/article_files/`, {
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
      } else {
        setMessage(data.message || "Error uploading file.");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setMessage("Internal error. Please try again.");
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".txt,.md,.json,.html,.jsonl"
        onChange={handleFileChange}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};

export default ArticleFileUploadForm;
