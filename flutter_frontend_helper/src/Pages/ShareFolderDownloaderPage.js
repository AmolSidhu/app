import React, { useEffect } from 'react';
import ShareFolderDownloaderRequest from '../Components/Requests/ShareFolderDownloaderRequest';

function ShareFolderDownloaderPage() {
  useEffect(() => {
    document.title = "Share Folder Downloader";
  }, []);
    return (
    <div>
      <h1>Share Folder Downloader</h1>
      <ShareFolderDownloaderRequest />
    </div>
  );
}

export default ShareFolderDownloaderPage;