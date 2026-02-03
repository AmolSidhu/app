import React, { useEffect } from 'react';
import server from '../Static/Constant';
import { useLocation } from "react-router-dom";

function ShareFolderDownloaderRequest() {
    const location = useLocation();
    const search = location.search;

    useEffect(() => {
        fetchSharedFolder();
    }, []);

    const fetchSharedFolder = async () => {
        try {
            const params = new URLSearchParams(search);
            const folderSerial = params.get('folder_serial');
            const shareCode = params.get('share_code');

            if (!folderSerial || !shareCode) {
                console.error("Missing query parameters");
                return;
            }

            const response = await fetch(
                `${server}/get/helper/folder_download/${folderSerial}/${shareCode}/`,
                { method: 'GET' }
            );

            if (!response.ok) {
                throw new Error('Failed to download folder');
            }

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${folderSerial}_files.zip`;
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error downloading shared folder:', error);
        }
    };

    return (
        <div>
            <h1>Preparing your download...</h1>
        </div>
    );
}

export default ShareFolderDownloaderRequest;
