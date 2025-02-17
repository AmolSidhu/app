import React, { Component } from "react";
import { Form, Button, Alert, ProgressBar, Badge } from "react-bootstrap";
import server from "../Static/Constants";

class SingleVideoUploadForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      video: null,
      thumbnail: null,
      private: false,
      permission: 2,
      errorMessage: "",
      message: "",
      progress: 0,
      customTag: "",
      tags: ["action", "comedy", "drama", "horror", "thriller", "adventure"],
      action: false,
      comedy: false,
      drama: false,
      horror: false,
      thriller: false,
      description: "",
      imdbLink: "",
      directors: [],
      stars: [],
      writers: [],
      creators: [],
      criticRating: "",
      title: "",
    };
  }

  handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    this.setState({
      [name]: type === "checkbox" ? checked : value,
    });
  };

  handleFileChange = (e) => {
    this.setState({
      video: e.target.files[0],
    });
  };

  handleImageChange = (e) => {
    this.setState({
      thumbnail: e.target.files[0],
    });
  };

  handleTagClick = (tag) => {
    this.setState(
      (prevState) => ({
        [tag]: !prevState[tag],
      }),
      () => {
        console.log(
          `Clicked ${tag}, variant: ${
            this.state[tag] ? "primary" : "secondary"
          }`
        );
      }
    );
  };

  handleCustomTagChange = (e) => {
    this.setState({
      customTag: e.target.value,
    });
  };

  handleAddCustomTag = () => {
    const { customTag, tags } = this.state;

    if (customTag && !tags.includes(customTag)) {
      this.setState((prevState) => ({
        tags: [...prevState.tags, customTag],
        [customTag]: true,
        customTag: "",
      }));
    }
  };

  handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("video", this.state.video);
    formData.append("thumbnail", this.state.thumbnail);
    formData.append(
      "tags",
      JSON.stringify(this.state.tags.filter((tag) => this.state[tag]))
    );
    formData.append("private", this.state.private);
    formData.append("permission", this.state.permission);
    formData.append("description", this.state.description);
    formData.append("imdbLink", this.state.imdbLink);
    formData.append("directors", JSON.stringify(this.state.directors));
    formData.append("stars", JSON.stringify(this.state.stars));
    formData.append("writers", JSON.stringify(this.state.writers));
    formData.append("creators", JSON.stringify(this.state.creators));
    formData.append("criticRating", this.state.criticRating);
    formData.append("title", this.state.title);

    const token = localStorage.getItem("token");
    const url = `${server}/upload/video/`;

    const config = {
      method: "POST",
      headers: {
        Authorization: `${token}`,
      },
      body: formData,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error("An error occurred while uploading the video.");
      }

      const reader = response.body.getReader();
      const contentLength = Number(response.headers.get("Content-Length"));

      let receivedLength = 0;
      let chunks = [];

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        chunks.push(value);
        receivedLength += value.length;

        this.setState({
          progress: Math.round((receivedLength / contentLength) * 100),
        });
      }

      const blob = new Blob(chunks);
      const responseData = await blob.text();

      const parsedResponse = JSON.parse(responseData);
      this.setState({ message: parsedResponse.message });
    } catch (error) {
      this.setState({ errorMessage: error.message });
    }
  };

  handleAddPerson = (field) => {
    this.setState((prevState) => ({
      [field]: [...prevState[field], ""],
    }));
  };

  handleRemovePerson = (field, index) => {
    this.setState((prevState) => ({
      [field]: prevState[field].filter((_, i) => i !== index),
    }));
  };

  handlePersonChange = (field, index, value) => {
    this.setState((prevState) => ({
      [field]: prevState[field].map((item, i) => (i === index ? value : item)),
    }));
  };

  render() {
    const {
      errorMessage,
      message,
      progress,
      customTag,
      directors,
      stars,
      writers,
      creators,
    } = this.state;

    return (
      <div className="single-video-upload-form">
        {errorMessage && <Alert variant="danger">{errorMessage}</Alert>}
        {message && (
          <Alert variant="success">
            <div
              dangerouslySetInnerHTML={{
                __html: message.replace("\n", "<br/>"),
              }}
            />
          </Alert>
        )}
        <Form onSubmit={this.handleSubmit}>
          <Form.Group controlId="video">
            <Form.Label>Video:</Form.Label>
            <Form.Control
              type="file"
              name="video"
              onChange={this.handleFileChange}
            />
          </Form.Group>
          <Form.Group controlId="thumbnail">
            <Form.Label>Image:</Form.Label>
            <Form.Control
              type="file"
              name="thumbnail"
              onChange={this.handleImageChange}
            />
          </Form.Group>
          <Form.Group controlId="imdbLink">
            <Form.Label>IMDB Link:</Form.Label>
            <p className="form-text text-muted">
              An IMDB Link will overwrite all details for Title, Tags, Directors,
              Stars, Writers, Thumbnail, and Description if valid
            </p>
            <Form.Control
              type="text"
              name="imdbLink"
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Form.Group controlId="title">
            <Form.Label>Title:</Form.Label>
            <Form.Control
              type="text"
              name="title"
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Form.Group controlId="tags">
            <Form.Label>Tags:</Form.Label>
            <div className="d-flex flex-wrap">
              {this.state.tags.map((tag) => (
                <Badge
                  key={tag}
                  pill
                  className="mr-2 mb-2 clickable"
                  onClick={() => {
                    this.handleTagClick(tag);
                  }}
                >
                  {tag}
                </Badge>
              ))}
            </div>
            <div className="d-flex align-items-center">
              <Form.Control
                type="text"
                value={customTag}
                onChange={this.handleCustomTagChange}
                placeholder="Add custom tag"
                className="d-inline-block w-auto mb-2 custom-tag-input"
              />
              <Button
                variant="primary"
                onClick={this.handleAddCustomTag}
                className="ml-2 mb-2"
              >
                Add Tag
              </Button>
            </div>
          </Form.Group>
          <Form.Group controlId="directors">
            <Form.Label>Directors:</Form.Label>
            {directors.map((director, index) => (
              <div key={index} className="d-flex align-items-center mb-2">
                <Form.Control
                  type="text"
                  value={director}
                  onChange={(e) =>
                    this.handlePersonChange("directors", index, e.target.value)
                  }
                />
                <Button
                  variant="danger"
                  className="ml-2"
                  onClick={() => this.handleRemovePerson("directors", index)}
                >
                  Remove
                </Button>
              </div>
            ))}
            <div>
              <Button
                variant="primary"
                onClick={() => this.handleAddPerson("directors")}
              >
                Add Director
              </Button>
            </div>
          </Form.Group>
          <Form.Group controlId="stars">
            <Form.Label>Stars:</Form.Label>
            {stars.map((star, index) => (
              <div key={index} className="d-flex align-items-center mb-2">
                <Form.Control
                  type="text"
                  value={star}
                  onChange={(e) =>
                    this.handlePersonChange("stars", index, e.target.value)
                  }
                />
                <Button
                  variant="danger"
                  className="ml-2"
                  onClick={() => this.handleRemovePerson("stars", index)}
                >
                  Remove
                </Button>
              </div>
            ))}
            <div>
              <Button
                variant="primary"
                onClick={() => this.handleAddPerson("stars")}
              >
                Add Star
              </Button>
            </div>
          </Form.Group>
          <Form.Group controlId="writers">
            <Form.Label>Writers:</Form.Label>
            {writers.map((writer, index) => (
              <div key={index} className="d-flex align-items-center mb-2">
                <Form.Control
                  type="text"
                  value={writer}
                  onChange={(e) =>
                    this.handlePersonChange("writers", index, e.target.value)
                  }
                />
                <Button
                  variant="danger"
                  className="ml-2"
                  onClick={() => this.handleRemovePerson("writers", index)}
                >
                  Remove
                </Button>
              </div>
            ))}
            <div>
              <Button
                variant="primary"
                onClick={() => this.handleAddPerson("writers")}
              >
                Add Writer
              </Button>
            </div>
          </Form.Group>
          <Form.Group controlId="creators">
            <Form.Label>Creators:</Form.Label>
            {creators.map((creator, index) => (
              <div key={index} className="d-flex align-items-center mb-2">
                <Form.Control
                  type="text"
                  value={creator}
                  onChange={(e) =>
                    this.handlePersonChange("creators", index, e.target.value)
                  }
                />
                <Button
                  variant="danger"
                  className="ml-2"
                  onClick={() => this.handleRemovePerson("creators", index)}
                >
                  Remove
                </Button>
              </div>
            ))}
            <div>
              <Button
                variant="primary"
                onClick={() => this.handleAddPerson("creators")}
              >
                Add Creator
              </Button>
            </div>
          </Form.Group>
          <Form.Group controlId="description">
            <Form.Label>Description:</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Form.Group controlId="criticRating">
            <Form.Label>Critic Rating:</Form.Label>
            <Form.Control
              type="text"
              name="criticRating"
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Form.Group controlId="private">
            <Form.Label>Private:</Form.Label>
            <Form.Check
              type="checkbox"
              name="private"
              checked={this.state.private}
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Form.Group controlId="permission">
            <Form.Label>Permission:</Form.Label>
            <Form.Control
              type="number"
              name="permission"
              value={this.state.permission}
              min={1}
              max={4}
              onChange={this.handleInputChange}
            />
          </Form.Group>
          <Button type="primary" variant="success">
            Upload
          </Button>
        </Form>
        {progress > 0 && (
          <div className="progress-container mt-3">
            <ProgressBar
              now={progress}
              label={`${progress}%`}
              striped
              animated
            />
          </div>
        )}
      </div>
    );
  }
}

export default SingleVideoUploadForm;
