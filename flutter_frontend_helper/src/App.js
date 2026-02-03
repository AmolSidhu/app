import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import ShareFolderDownloaderPage from "./Pages/ShareFolderDownloaderPage";
import ShareFileDownloaderPage from "./Pages/ShareFileDownloaderPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/share-file-downloader/" element={<ShareFileDownloaderPage />} />
        <Route path="/share-folder-downloader/" element={<ShareFolderDownloaderPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
