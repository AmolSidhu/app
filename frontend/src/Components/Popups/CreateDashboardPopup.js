import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const CreateDashboardPopup = ({ onClose }) => {
  const [dataSources, setDataSources] = useState([]);
  const [dashboardName, setDashboardName] = useState("");
  const [selectedDataSource, setSelectedDataSource] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchDataSources();
  }, []);

  const fetchDataSources = async () => {
    try {
      const response = await fetch(`${server}/get/cleaned_data_sources/`, {
        method: "GET",
        headers: {
          Authorization: localStorage.getItem("token"),
        },
      });
      const result = await response.json();
      if (response.ok) {
        setDataSources(result.data);
      } else {
        console.error(result.message || "Failed to fetch data sources");
      }
    } catch (error) {
      console.error("Error fetching data sources:", error);
    }
  };

  const handleCreateDashboard = async (e) => {
    e.preventDefault();
    if (!dashboardName || !selectedDataSource) return;
    setCreating(true);

    try {
      const response = await fetch(`${server}/create/dashboard/`, {
        method: "POST",
        headers: {
          Authorization: localStorage.getItem("token"),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dashboard_name: dashboardName,
          data_source_serial: selectedDataSource,
        }),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Dashboard created successfully!");
        onClose();
      } else {
        alert(result.message || "Failed to create dashboard.");
      }
    } catch (error) {
      console.error("Error creating dashboard:", error);
      alert("An error occurred.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h2>Create New Dashboard</h2>
        <form onSubmit={handleCreateDashboard}>
          <input
            type="text"
            placeholder="Dashboard Name"
            value={dashboardName}
            onChange={(e) => setDashboardName(e.target.value)}
            required
            style={styles.input}
          />
          <select
            value={selectedDataSource}
            onChange={(e) => setSelectedDataSource(e.target.value)}
            required
            style={styles.input}
          >
            <option value="">Select Data Source</option>
            {dataSources.map((source) => (
              <option key={source.serial} value={source.serial}>
                {source.data_source_name} ({source.file_name})
              </option>
            ))}
          </select>
          <div style={styles.buttonGroup}>
            <button type="submit" disabled={creating} style={styles.button}>
              {creating ? "Creating..." : "Create"}
            </button>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    height: "100vh",
    width: "100vw",
    backgroundColor: "rgba(0, 0, 0, 0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "10px",
    minWidth: "400px",
    maxWidth: "90%",
    boxShadow: "0 5px 15px rgba(0,0,0,0.3)",
  },
  input: {
    width: "100%",
    padding: "10px",
    margin: "10px 0",
    boxSizing: "border-box",
  },
  buttonGroup: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: "15px",
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  cancelButton: {
    padding: "10px 20px",
    backgroundColor: "#6c757d",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
};

export default CreateDashboardPopup;
