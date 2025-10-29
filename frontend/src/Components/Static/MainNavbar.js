import React, { useState } from "react";
import { Container, Nav, Navbar, NavDropdown } from "react-bootstrap";
import LogoutRequest from "../Requests/LogoutRequest";

const MainNavbar = () => {
  const [expanded, setExpanded] = useState(false);

  const Logout = ({ onLogout }) => {
    return <button onClick={onLogout}>Logout</button>;
  };

  return (
    <Navbar
      expand="lg"
      expanded={expanded}
      className="main-navbar"
    >
      <Container>
        <Navbar.Brand href="/">Home</Navbar.Brand>
        <Navbar.Toggle
          aria-controls="basic-navbar-nav"
          onClick={() => setExpanded(!expanded)}
        />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="w-100 justify-content-between">
            <NavDropdown title="Pictures" id="pictures-dropdown" menuVariant="light">
              <NavDropdown.Item href="/pictures/albums/">Albums</NavDropdown.Item>
              <NavDropdown.Item href="/pictures/myalbums/">My Albums</NavDropdown.Item>
              <NavDropdown.Item href="/pictures/favourites/">My Favourites</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Videos" id="video-dropdown" menuVariant="light">
              <NavDropdown.Item href="/video/list/">Videos</NavDropdown.Item>
              <NavDropdown.Item href="/video/upload/">Upload</NavDropdown.Item>
              <NavDropdown.Item href="/video/customlists/">Custom Lists</NavDropdown.Item>
              <NavDropdown.Item href="/video/favourites/">Favourites</NavDropdown.Item>
              <NavDropdown.Item href="/video/request/">Create Video Request</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title='Youtube' id='youtube-dropdown' menuVariant='light'>
              <NavDropdown.Item href='/youtube/lists/'>My Videos</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title='Music' id='music-dropdown' menuVariant='light'>
              <NavDropdown.Item href='/music/albums/'>Music Albums</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Analytics" id="analytics-dropdown" menuVariant="light">
            <NavDropdown.Item href="/analytics/upload/">Upload Data Source</NavDropdown.Item>
              <NavDropdown.Item href="/analytics/mydashboards/">My Dashboard</NavDropdown.Item>
              <NavDropdown.Item href="/analytics/view/">View Dashboard</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Profile" id="profile-dropdown" menuVariant="light">
              <NavDropdown.Item href="/profile/">My Profile</NavDropdown.Item>
              <NavDropdown.Item href="/view/videouploads">My Video Uploads</NavDropdown.Item>
              <NavDropdown.Item href="/view/videorequests/">My Video Requests</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Articles" id="articles-dropdown" menuVariant="light">
              <NavDropdown.Item href="/articles/search/">Search Articles</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Files" id="files-dropdown" menuVariant="light">
              <NavDropdown.Item href="/files/uploadshare/">Upload Files</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="MTG Scraper" id="mtg-dropdown" menuVariant="light">
              <NavDropdown.Item href="/mtg/uploadscraper/">Upload Scraper</NavDropdown.Item>
              <NavDropdown.Item href="/mtg/viewscrapers/">View Scrapers</NavDropdown.Item>
              <NavDropdown.Item href="/mtg/viewscraperhistory/">View Scraper History</NavDropdown.Item>
            </NavDropdown>

            <Logout onLogout={LogoutRequest} />
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default MainNavbar;