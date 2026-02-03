import React, {useEffect} from 'react';
import ShareFileDownloaderRequest from '../Components/Requests/ShareFileDownloaderRequest';

function ShareFileDownloaderPage() {
  useEffect(() => {
    document.title = "Share File Downloader";
  }, []);
  return (
    <div>
      <h1>Share File Downloader</h1>
      <ShareFileDownloaderRequest />
    </div>
  );
}

export default ShareFileDownloaderPage;