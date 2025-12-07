import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const ArticleUploadForm = () => {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (error) setMessage("");
  }, [error]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title || !content) {
      setError("All fields are required.");
      return;
    }

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`${server}/create/single_article/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token,
        },
        body: JSON.stringify({
          title,
          content,
          tags: tags
            .split(",")
            .map((t) => t.trim())
            .filter((t) => t !== ""),
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || "Article created successfully!");
        setTitle("");
        setContent("");
        setTags("");
      } else {
        setError(data.message || "Error creating article.");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError("Internal error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        placeholder="Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <input
        type="text"
        placeholder="Tags (comma separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
};

export default ArticleUploadForm;
