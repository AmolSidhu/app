import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

//Auth Pages
import LoginPage from "./Pages/Auth/LoginPage";
import VerificationPage from "./Pages/Auth/VerificationPage";
import RegistrationPage from "./Pages/Auth/RegisterationPage";
import ForgotPasswordPage from "./Pages/Auth/ForgotPasswordPage";

//General Pages
import HomePage from "./Pages/General/HomePage";
import ProfilePage from "./Pages/General/ProfilePage";

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
import UploadDataSourcePage from "./Pages/Analytics/UploadDataSourcePage";
import MyDashboardsPage from "./Pages/Analytics/MyDashboardsPage";

//Youtube Pages
import MyYoutubeListsPage from "./Pages/Youtube/MyYoutubeListsPage";
import YoutubeStreamPage from "./Pages/Youtube/YoutubeStreamPage";

//Music Pages
import ViewAllMusicAlbumsPage from "./Pages/Music/ViewAllMusicAlbumsPage";

//Articles Pages
import SearchArticlesPage from "./Pages/Articles/SearchArticlesPage";
import UploadArticlesPage from "./Pages/Articles/UploadArticlesPage";

//Files Pages
import UploadShareFilesPage from "./Pages/Files/UploadShareFilesPage";
import ViewFolderShareFilesPage from "./Pages/Files/ViewFolderShareFilesPage";
import DownloadFilePage from "./Pages/Files/DownloadFilePage";
import DownloadFolderPage from "./Pages/Files/DownloadFolderPage";

//MTG Pages
import UploadScraperPage from "./Pages/MTG/UploadScraperPage";
import ViewScrapersPage from "./Pages/MTG/ViewScrapersPage";
import ViewScraperHistoryPage from "./Pages/MTG/ViewScraperHistoryPage";

//Admin Pages
import AdminLoginPage from "./Pages/Admin/AdminLoginPage";
import VideoRequestApprovalPage from "./Pages/Admin/VideoRequestApprovalPage";
import AdminDataPage from "./Pages/Admin/AdminDataPage";

//Misc Pages
import NotFound from "./Pages/Misc/NotFoundPage";
import AboutPage from "./Pages/Misc/AboutPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login/" element={<LoginPage />} />
        <Route path="/register/" element={<RegistrationPage />} />
        <Route path="/verification/" element={<VerificationPage />} />
        <Route path="/forgotpassword/" element={<ForgotPasswordPage />} />


        <Route path="/home/" element={<HomePage/>} />
        <Route index element={<HomePage/>} />
        <Route path="/about/" element={<AboutPage />} />
        <Route path="/profile/" element={<ProfilePage />} />

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
        <Route path="/analytics/view/" element={<ViewDashboardPage />} />
        <Route path="/analytics/mydashboards/" element={<MyDashboardsPage />} />

        <Route path="/youtube/lists/" element={<MyYoutubeListsPage />} />
        <Route path="/youtube/stream/" element={<YoutubeStreamPage />} />

        <Route path="/music/albums/" element={<ViewAllMusicAlbumsPage />} />

        <Route path="/articles/search/" element={<SearchArticlesPage />} />
        <Route path="/articles/upload/" element={<UploadArticlesPage />} />

        <Route path="/files/uploadshare/" element={<UploadShareFilesPage />} />
        <Route path="/files/viewfolder/" element={<ViewFolderShareFilesPage />} />
        <Route path="/files/sharefile/" element={<DownloadFilePage />} />
        <Route path="/files/sharefolder/" element={<DownloadFolderPage />} />

        <Route path="/mtg/uploadscraper/" element={<UploadScraperPage />} />
        <Route path="/mtg/viewscrapers/" element={<ViewScrapersPage />} />
        <Route path="/mtg/viewscraperhistory/" element={<ViewScraperHistoryPage />} />

        <Route path="/admin/login/" element={<AdminLoginPage />} />
        <Route path="/admin/videorequests/" element={<VideoRequestApprovalPage />} />
        <Route path="/admin/data/" element={<AdminDataPage />} />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
