import React, { useEffect } from 'react';
import server from '../Static/Constant';
import { useLocation } from "react-router-dom";

function ShareFileDownloaderRequest() {
    const location = useLocation();
    const search = location.search;

    useEffect(() => {
        fetchSharedFile();
    }, []);

    const fetchSharedFile = async () => {
        try {
            const params = new URLSearchParams(search);
            const fileSerial = params.get('file_serial');
            const shareCode = params.get('share_code');

            if (!fileSerial || !shareCode) {
                console.error("Missing query parameters");
                return;
            }

            const response = await fetch(
                `${server}/get/helper/file_download/${fileSerial}/${shareCode}/`,
                { method: 'GET' }
            );

            if (!response.ok) {
                throw new Error('Failed to download file');
            }

            const disposition = response.headers.get('Content-Disposition');
            let filename = 'downloaded_file';

            if (disposition && disposition.includes('filename=')) {
                filename = decodeURIComponent(
                    disposition
                        .split('filename=')[1]
                        .replace(/"/g, '')
                );
            }

            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error downloading shared file:', error);
        }
    };

    return (
        <div>
            <h1>Preparing your download...</h1>
        </div>
    );
}

export default ShareFileDownloaderRequest;
