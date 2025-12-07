import React, { useState } from "react";
import { Container, Nav, Navbar, NavDropdown, Button } from "react-bootstrap";
import LogoutRequest from "../Requests/LogoutRequest";
import ServerDataPopup from "../Popups/ServerDataPopup";

const MainNavbar = () => {
  const [expanded, setExpanded] = useState(false);
  const [showServerInfo, setShowServerInfo] = useState(false);

  return (
    <>
      <Navbar
        expand="lg"
        expanded={expanded}
        bg="light"
        variant="light"
        className="main-navbar shadow-sm"
      >
        <Container fluid className="px-4">
          <Navbar.Brand href="/">Home</Navbar.Brand>

          <Navbar.Toggle
            aria-controls="basic-navbar-nav"
            onClick={() => setExpanded((v) => !v)}
          />

          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="flex-grow-1 justify-content-start flex-wrap align-items-center">
              <NavDropdown title="Pictures" id="pictures-dropdown" className="me-3">
                <NavDropdown.Item href="/pictures/albums/">Albums</NavDropdown.Item>
                <NavDropdown.Item href="/pictures/myalbums/">My Albums</NavDropdown.Item>
                <NavDropdown.Item href="/pictures/favourites/">My Favourites</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Videos" id="video-dropdown" className="me-3">
                <NavDropdown.Item href="/video/list/">Videos</NavDropdown.Item>
                <NavDropdown.Item href="/video/upload/">Upload</NavDropdown.Item>
                <NavDropdown.Item href="/video/customlists/">Custom Lists</NavDropdown.Item>
                <NavDropdown.Item href="/video/favourites/">Favourites</NavDropdown.Item>
                <NavDropdown.Item href="/video/request/">Create Video Request</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Youtube" id="youtube-dropdown" className="me-3">
                <NavDropdown.Item href="/youtube/lists/">My Videos</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Music" id="music-dropdown" className="me-3">
                <NavDropdown.Item href="/music/albums/">Music Albums</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Analytics" id="analytics-dropdown" className="me-3">
                <NavDropdown.Item href="/analytics/upload/">Upload Data Source</NavDropdown.Item>
                <NavDropdown.Item href="/analytics/mydashboards/">My Dashboard</NavDropdown.Item>
                <NavDropdown.Item href="/analytics/view/">View Dashboard</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Profile" id="profile-dropdown" className="me-3">
                <NavDropdown.Item href="/profile/">My Profile</NavDropdown.Item>
                <NavDropdown.Item href="/view/videouploads">My Video Uploads</NavDropdown.Item>
                <NavDropdown.Item href="/view/videorequests/">My Video Requests</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Articles" id="articles-dropdown" className="me-3">
                <NavDropdown.Item href="/articles/upload/">Upload Articles</NavDropdown.Item>
                <NavDropdown.Item href="/articles/search/">Search Articles</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Files" id="files-dropdown" className="me-3">
                <NavDropdown.Item href="/files/uploadshare/">Upload Files</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="MTG Scraper" id="mtg-dropdown" className="me-3">
                <NavDropdown.Item href="/mtg/uploadscraper/">Upload Scraper</NavDropdown.Item>
                <NavDropdown.Item href="/mtg/viewscrapers/">View Scrapers</NavDropdown.Item>
                <NavDropdown.Item href="/mtg/viewscraperhistory/">View Scraper History</NavDropdown.Item>
              </NavDropdown>
            </Nav>

            <div className="d-flex align-items-center ms-lg-3 mt-2 mt-lg-0 flex-shrink-0">
              <Button
                variant="outline-info"
                className="me-2"
                onClick={() => setShowServerInfo(true)}
              >
                Info
              </Button>
              <Button variant="outline-danger" onClick={LogoutRequest}>
                Logout
              </Button>
            </div>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {showServerInfo && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center"
          style={{ zIndex: 1050 }}
          onClick={() => setShowServerInfo(false)}
        >
          <div onClick={(e) => e.stopPropagation()}>
            <ServerDataPopup onClose={() => setShowServerInfo(false)} />
          </div>
        </div>
      )}
    </>
  );
};

export default MainNavbar;
