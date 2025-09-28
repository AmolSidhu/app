import React, { useEffect } from "react";
import server from "../Static/Constants";
import { useLocation, Link } from "react-router-dom";

const DownloadFolderRequest = () => {
  const location = useLocation();
  const search = location.search;

  useEffect(() => {
    const controller = new AbortController();

    const download = async () => {
      try {
        const params = new URLSearchParams(search);
        const folderSerial = params.get("serial");
        const shareCode = params.get("share_code");

        if (!folderSerial || !shareCode) {
          console.error("Missing serial or share_code in query string.");
          return;
        }

        const response = await fetch(
          `${server}/get/folder_downloaded_files/${folderSerial}/${shareCode}/`,
          {
            method: "GET",
            headers: {
              Authorization: localStorage.getItem("token"),
            },
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          console.error("Server returned an error:", await response.text());
          return;
        }

        const disposition = response.headers.get("Content-Disposition") || "";
        let filename = `${folderSerial}_files.zip`;
        const match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^;"']+)/i);
        if (match && match[1]) {
          filename = decodeURIComponent(match[1].replace(/"/g, ""));
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error("Error downloading folder zip:", err);
        }
      }
    };

    download();
    return () => controller.abort();
  }, [search]);

  return (
    <div>
      <h2>Your download should begin automatically...</h2>
      <Link to="/">Back to Home</Link>
    </div>
  );
};

export default DownloadFolderRequest;
