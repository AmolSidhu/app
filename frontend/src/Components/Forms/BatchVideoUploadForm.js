import React, { Component } from "react";
import { Form, Button, Alert, Badge } from "react-bootstrap";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import server from "../Static/Constants";

class BatchVideoUploadForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      videoData: [],
      thumbnailFiles: [],
      private: false,
      permission: 2,
      existingSeries: false,
      master_serial: "",
      errorMessage: "",
      message: "",
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
      criticRating: 0,
      title: "",
    };
  }

  handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    this.setState({
      [name]: type === "checkbox" ? checked : value,
    });
  };

  handleFilesChange = (event) => {
    const files = Array.from(event.target.files);
    const videoData = files.map((file) => ({
      file,
      name: file.name,
      episode: "",
      season: "",
    }));
    this.setState({
      videoData,
    });
  };

  handleImageChange = (event) => {
    this.setState({
      thumbnailFiles: Array.from(event.target.files),
    });
  };

  handleTagClick = (tag) => {
    this.setState((prevState) => ({
      [tag]: !prevState[tag],
    }));
  };

  handleCustomTagChange = (event) => {
    this.setState({
      customTag: event.target.value,
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

  handleVideoDataChange = (index, field, value) => {
    this.setState((prevState) => ({
      videoData: prevState.videoData.map((data, i) =>
        i === index ? { ...data, [field]: value } : data
      ),
    }));
  };

  handlePersonChange = (field, index, value) => {
    this.setState((prevState) => ({
      [field]: prevState[field].map((person, i) =>
        i === index ? value : person
      ),
    }));
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

  handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();

    this.state.videoData.forEach((data, index) => {
      formData.append(`videos`, data.file);
      formData.append(`episode_${index}`, data.episode);
      formData.append(`season_${index}`, data.season);
    });

    formData.append(`thumbnail`, this.state.thumbnailFiles[0]);

    formData.append(`tags`, JSON.stringify(this.state.tags));
    formData.append(`private`, this.state.private.toString());
    formData.append(`permission`, this.state.permission.toString());
    formData.append(`existing_series`, this.state.existingSeries.toString());
    formData.append(`description`, this.state.description);
    formData.append(`imdbLink`, this.state.imdbLink);
    formData.append(`directors`, JSON.stringify(this.state.directors));
    formData.append(`stars`, JSON.stringify(this.state.stars));
    formData.append(`writers`, JSON.stringify(this.state.writers));
    formData.append(`creators`, JSON.stringify(this.state.creators));
    formData.append(`criticRating`, this.state.criticRating);
    formData.append(`title`, this.state.title);

    if (this.state.existingSeries) {
      formData.append(`master_serial`, this.state.master_serial);
    } else {
      formData.append(`master_serial`, null);
    }

    const token = localStorage.getItem("token");
    const url = `${server}/upload/batch_video/`;

    const config = {
      method: "POST",
      headers: {
        Authorization: token,
      },
      body: formData,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error("An error occurred while uploading the videos.");
      }

      const responseData = await response.json();
      this.setState({ message: responseData.message });
    } catch (error) {
      this.setState({ errorMessage: error.message });
    }
  };

  onDragEnd = (result) => {
    const { source, destination } = result;

    if (!destination) {
      return;
    }

    const reorderedVideoData = Array.from(this.state.videoData);
    const [movedVideo] = reorderedVideoData.splice(source.index, 1);
    reorderedVideoData.splice(destination.index, 0, movedVideo);

    this.setState({ videoData: reorderedVideoData });
  };

  render() {
    const {
      errorMessage,
      message,
      customTag,
      videoData,
      directors,
      stars,
      writers,
      creators,
    } = this.state;

    return (
      <div>
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
            <Form.Label>Videos:</Form.Label>
            <Form.Control
              type="file"
              multiple
              onChange={this.handleFilesChange}
            />
          </Form.Group>

          <DragDropContext onDragEnd={this.onDragEnd}>
            <Droppable droppableId="videoData">
              {(provided) => (
                <div {...provided.droppableProps} ref={provided.innerRef}>
                  {videoData.map((data, index) => (
                    <Draggable
                      key={data.file.name}
                      draggableId={data.file.name}
                      index={index}
                    >
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="mb-3"
                        >
                          <h5>Video {index + 1}</h5>
                          <p>{data.name}</p>
                          <Form.Group controlId={`episode${index}`}>
                            <Form.Label>Episode:</Form.Label>
                            <Form.Control
                              type="text"
                              value={data.episode}
                              onChange={(e) =>
                                this.handleVideoDataChange(
                                  index,
                                  "episode",
                                  e.target.value
                                )
                              }
                            />
                          </Form.Group>
                          <Form.Group controlId={`season${index}`}>
                            <Form.Label>Season:</Form.Label>
                            <Form.Control
                              type="text"
                              value={data.season}
                              onChange={(e) =>
                                this.handleVideoDataChange(
                                  index,
                                  "season",
                                  e.target.value
                                )
                              }
                            />
                          </Form.Group>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>

          <Form.Group controlId="thumbnail">
            <Form.Label>Thumbnails:</Form.Label>
            <Form.Control type="file" onChange={this.handleImageChange} />
          </Form.Group>

          <Form.Group controlId="tags">
            <Form.Label>Tags:</Form.Label>
            <div>
              {this.state.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant={this.state[tag] ? "primary" : "secondary"}
                  className="mr-2 mb-2 clickable"
                  onClick={() => this.handleTagClick(tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </Form.Group>

          <Form.Group controlId="customTag">
            <Form.Label>Add Custom Tag:</Form.Label>
            <Form.Control
              type="text"
              value={customTag}
              onChange={this.handleCustomTagChange}
            />
            <Button
              variant="primary"
              onClick={this.handleAddCustomTag}
              className="mt-2"
            >
              Add Tag
            </Button>
          </Form.Group>

          <Form.Group controlId="description">
            <Form.Label>Description:</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={this.state.description}
              onChange={this.handleInputChange}
              name="description"
            />
          </Form.Group>

          <Form.Group controlId="imdbLink">
            <Form.Label>IMDB Link:</Form.Label>
            <Form.Control
              type="text"
              value={this.state.imdbLink}
              onChange={this.handleInputChange}
              name="imdbLink"
            />
          </Form.Group>

          {/* Render Directors */}
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

          {/* Render Stars */}
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

          <Form.Group controlId="title">
            <Form.Label>Title:</Form.Label>
            <Form.Control
              type="text"
              value={this.state.title}
              onChange={this.handleInputChange}
              name="title"
            />
          </Form.Group>

          <Form.Group controlId="existingSeries">
            <Form.Check
              type="checkbox"
              label="Existing Series"
              checked={this.state.existingSeries}
              onChange={this.handleInputChange}
              name="existingSeries"
            />
          </Form.Group>

          {this.state.existingSeries && (
            <Form.Group controlId="masterSerial">
              <Form.Label>Master Serial:</Form.Label>
              <Form.Control
                type="text"
                value={this.state.master_serial}
                onChange={this.handleInputChange}
                name="master_serial"
              />
            </Form.Group>
          )}

          <Button variant="primary" type="submit">
            Upload Videos
          </Button>
        </Form>
      </div>
    );
  }
}

export default BatchVideoUploadForm;
