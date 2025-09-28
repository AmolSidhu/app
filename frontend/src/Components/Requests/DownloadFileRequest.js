import React, { useEffect } from "react";
import server from "../Static/Constants";
import { useLocation, Link } from "react-router-dom";

const DownloadFileRequest = () => {
    const location = useLocation();
    const search = location.search;

    useEffect(() => {
        const fetchFile = async () => {
            try {
                const params = new URLSearchParams(search);
                const fileSerial = params.get("serial");
                const shareCode = params.get("share_code");
                if (!fileSerial || !shareCode) {
                    console.error("Missing serial or share_code in query string.");
                    return;
                }
                const response = await fetch(
                    `${server}/get/downloaded_file/${fileSerial}/${shareCode}/`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: localStorage.getItem("token"),
                        },
                    }
                );
                if (!response.ok) {
                    console.error("Server returned an error:", await response.text());
                    return;
                }
                const disposition = response.headers.get("Content-Disposition") || "";
                let filename = `${fileSerial}_file`;
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
                console.error("Error downloading file:", err);
            }
        };
        fetchFile();
    }, [search]);

    return (
        <div>
            <h2>Your download should start automatically.</h2>
            <p>
                If it doesn't, please{" "}
                <Link to={location.pathname + location.search}>click here to retry</Link>.
            </p>
        </div>
    );
}

export default DownloadFileRequest;