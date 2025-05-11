import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

//Auth Pages
import LoginPage from "./Pages/Auth/LoginPage";
import VerificationPage from "./Pages/Auth/VerificationPage";
import RegistrationPage from "./Pages/Auth/RegisterationPage";

//General Pages
import HomePage from "./Pages/General/HomePage";

//Video Pages
import VideoUploadPage from "./Pages/Videos/VideoUploadPage";
import VideoPage from "./Pages/Videos/VideoPage";
import VideoStreamPage from "./Pages/Videos/VideoStreamPage";
import VideoSearchPage from "./Pages/Videos/VideoSearchPage";
import VideoCustomListPage from "./Pages/Videos/VideoCustomListPage";
import VideoFavouritePage from "./Pages/Videos/VideoFavouritePage";
import VideoTitleSearchPage from "./Pages/Videos/VideoTitleSearchPage";
import MakeVideoRequestPage from "./Pages/Videos/MakeVideoRequestPage";

//Picture Pages
import CustomImageAlbumsPage from "./Pages/Pictures/CustomImageAlbumsPage";
import CustomPicturePage from "./Pages/Pictures/CustomPicturePage";
import DefaultImageAlbumsPage from "./Pages/Pictures/DefaultImageAlbumsPage";
import DefaultPicturePage from "./Pages/Pictures/DefaultPicturePage";
import FavouriteImagesPage from "./Pages/Pictures/FavouriteImagesPage";
import PictureSearchPage from "./Pages/Pictures/PictureSearchPage";

//Management Pages
import MyVideoUploadsPage from "./Pages/Management/MyVideoUploadsPage";
import EditVideoPage from "./Pages/Management/EditVideoPage";
import EditPicturePage from "./Pages/Management/EditPicturePage";
import ViewMyVideoRequestsPage from "./Pages/Management/ViewMyVideoRequestsPage";

//Analytics Pages
import CreateDashboardPage from "./Pages/Analytics/CreateDashboardPage";
import ViewDashboardPage from "./Pages/Analytics/ViewDashboardPage";

//Youtube Pages
import MyYoutubeListsPage from "./Pages/Youtube/MyYoutubeListsPage";
import UploadDataSourcePage from "./Pages/Analytics/UploadDataSourcePage";
import YoutubeStreamPage from "./Pages/Youtube/YoutubeStreamPage";

//Music Pages
import ViewAllMusicAlbumsPage from "./Pages/Music/ViewAllMusicAlbumsPage";

//Misc Pages
import NotFound from "./Pages/Misc/NotFoundPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login/" element={<LoginPage />} />
        <Route path="/register/" element={<RegistrationPage />} />
        <Route path="/verification/" element={<VerificationPage />} />

        <Route path="/home/" element={<HomePage/>} />
        <Route index element={<HomePage/>} />
        <Route path="/about/" element={<h1>About</h1>} />

        <Route path="/video/upload/" element={<VideoUploadPage />} />
        <Route path="/video/list" element={<VideoPage />} />
        <Route path="/video/stream/" element={<VideoStreamPage />} />
        <Route path="/video/search/" element={<VideoSearchPage />} />
        <Route path="/video/customlists/" element={<VideoCustomListPage />} />
        <Route path="/video/favourites/" element={<VideoFavouritePage />} />
        <Route path="/video/search/v/" element={<VideoTitleSearchPage />} />
        <Route path="/video/request/" element={<MakeVideoRequestPage />} />

        <Route path="/pictures/albums/" element={<DefaultImageAlbumsPage />} />
        <Route path="/pictures/" element={<DefaultPicturePage />} />
        <Route path="/pictures/myalbums/" element={<CustomImageAlbumsPage />} />
        <Route path="/mypictures/" element={<CustomPicturePage />} />
        <Route path="/pictures/favourites/" element={<FavouriteImagesPage />} />
        <Route path="/picture/search/" element={<PictureSearchPage />} />

        <Route path="/view/videouploads/" element={<MyVideoUploadsPage />} />
        <Route path="/edit/video/" element={<EditVideoPage />} />
        <Route path="/edit/picture/" element={<EditPicturePage />} />
        <Route path="/view/videorequests/" element={<ViewMyVideoRequestsPage />} />

        <Route path="/analytics/createdashboard/" element={<CreateDashboardPage />} />
        <Route path="/analytics/upload/" element={<UploadDataSourcePage />} />
        <Route path="/analytics/viewdashboard/" element={<ViewDashboardPage />} />

        <Route path="/youtube/lists/" element={<MyYoutubeListsPage />} />
        <Route path="/youtube/stream/" element={<YoutubeStreamPage />} />

        <Route path="/music/albums/" element={<ViewAllMusicAlbumsPage />} />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
