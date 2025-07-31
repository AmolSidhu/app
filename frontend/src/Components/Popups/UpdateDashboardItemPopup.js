import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const UpdateDashboardItemPopup = ({ dashboardSerial, dashboardItemSerial, onClose }) => {
  const [itemType, setItemType] = useState("");
  const [itemOrder, setItemOrder] = useState("");
  const [dataItemName, setDataItemName] = useState("");

  const [graphType, setGraphType] = useState("");
  const [graphTypeOptions, setGraphTypeOptions] = useState([]);
  const [columns, setColumns] = useState([]);
  const [column1, setColumn1] = useState("");
  const [column2, setColumn2] = useState("");
  const [graphTitle, setGraphTitle] = useState("");
  const [xAxisTitle, setXAxisTitle] = useState("");
  const [yAxisTitle, setYAxisTitle] = useState("");

  const [dataLines, setDataLines] = useState([]);
  const [textHeader, setTextHeader] = useState("");
  const [textBody, setTextBody] = useState("");

  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${server}/get/dashboard_item_data/${dashboardSerial}/${dashboardItemSerial}/`, {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        });

        if (response.ok) {
          const { data } = await response.json();
          setItemType(data.item_type);
          setItemOrder(data.item_order);
          setDataItemName(data.data_item_name || "");

          if (data.item_type === "Graph") {
            setGraphTypeOptions(data.graph_type || []);
            setGraphType((data.current_graph_type || "").toLowerCase());
            setColumn1(data.column_1 || "");
            setColumn2(data.column_2 || "");
            setGraphTitle(data.graph_title || "");
            setXAxisTitle(data.x_axis_title || "");
            setYAxisTitle(data.y_axis_title || "");
          } else if (data.item_type === "Table") {
            setDataLines(data.data_lines || []);
          } else if (data.item_type === "Text") {
            setTextHeader(data.text_header || "");
            setTextBody(data.text_body || "");
          }
        } else {
          const errorData = await response.json();
          setError(errorData.message || "Failed to fetch dashboard item.");
        }
      } catch (err) {
        console.error("Error fetching dashboard item:", err);
        setError("Unexpected error occurred.");
      }
    };

    const fetchColumnMetadata = async () => {
      try {
        const response = await fetch(`${server}/get/data_source_detials/${dashboardSerial}/`, {
          method: "GET",
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        });

        if (response.ok) {
          const result = await response.json();
          const rawData = result.data || {};
          const processedColumns = Object.entries(rawData).map(([key, [name, type]]) => ({
            key,
            name,
            type,
          }));
          setColumns(processedColumns);
          fetchData();
        }
      } catch (e) {
        console.error("Failed to fetch column metadata", e);
      }
    };

    fetchColumnMetadata();
  }, [dashboardSerial, dashboardItemSerial]);

  const isNumeric = (colName) => {
    const column = columns.find((col) => col.name === colName);
    return column && (column.type === "int64" || column.type === "float64");
  };

  const updateLine = (index, field, value) => {
    const newLines = [...dataLines];
    newLines[index][field] = value;

    if (field === "source_1" && !isNumeric(value)) {
      newLines[index].source_2 = "";
      newLines[index].operation = "";
    }

    setDataLines(newLines);
  };

  const handleSubmitUpdate = async () => {
    const basePayload = {
      item_type: itemType,
      item_order: itemOrder,
      data_item_name: dataItemName,
      data_item_type: itemType,
      data_item_description: "",
    };

    let extraPayload = {};

    if (itemType === "Graph") {
      extraPayload = {
        graph_type: graphType.toLowerCase(),
        columns: columns.map((c) => c.name),
        column_1: column1,
        column_2: column2,
        graph_title: graphTitle,
        x_axis_title: xAxisTitle,
        y_axis_title: yAxisTitle,
      };
    } else if (itemType === "Table") {
      extraPayload = {
        data_lines: dataLines.map((line, index) => ({
          serial: line.serial || index,
          column_order: Number(line.column_order || index),
          column_name: line.column_name || "",
          source_1: line.source_1 || "",
          source_2: line.source_2 || "",
          operation: line.operation || "",
        })),
      };
    } else if (itemType === "Text") {
      extraPayload = {
        text_header: textHeader,
        text_body: textBody,
      };
    }

    try {
      const response = await fetch(`${server}/update/dashboard_item/${dashboardSerial}/${dashboardItemSerial}/`, {
        method: "PATCH",
        headers: {
          Authorization: localStorage.getItem("token"),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...basePayload, ...extraPayload }),
      });

      if (response.ok) {
        alert("Dashboard item updated successfully!");
        onClose();
      } else {
        const errorData = await response.json();
        setError(errorData.message || "Update failed.");
      }
    } catch (e) {
      console.error("Update error", e);
      setError("Unexpected error occurred.");
    }
  };

  return (
    <div className="analytics-popup">
      <div className="analytics-popup-inner">
        <h3>Update Dashboard Item</h3>

        {error && <p className="analytics-popup-error">{error}</p>}

        <label>Item Order</label>
        <input type="number" value={itemOrder} onChange={(e) => setItemOrder(e.target.value)} />

        <label>Data Item Name</label>
        <input type="text" value={dataItemName} onChange={(e) => setDataItemName(e.target.value)} />

        {itemType === "Graph" && (
          <>
            <label>Graph Type</label>
            <select value={graphType} onChange={(e) => setGraphType(e.target.value)}>
              <option value="">--Select Graph Type--</option>
              {graphTypeOptions.map((type) => (
                <option key={type} value={type.toLowerCase()}>
                  {type}
                </option>
              ))}
            </select>

            <label>Column 1</label>
            <select value={column1} onChange={(e) => setColumn1(e.target.value)}>
              <option value="">--Select Column--</option>
              {columns.map((col) => (
                <option key={col.key} value={col.name}>
                  {col.name} ({col.type})
                </option>
              ))}
            </select>

            <label>Column 2</label>
            <select value={column2} onChange={(e) => setColumn2(e.target.value)}>
              <option value="">--Select Column--</option>
              {columns.map((col) => (
                <option key={col.key} value={col.name}>
                  {col.name} ({col.type})
                </option>
              ))}
            </select>

            <label>Graph Title</label>
            <input type="text" value={graphTitle} onChange={(e) => setGraphTitle(e.target.value)} />

            <label>X Axis Title</label>
            <input type="text" value={xAxisTitle} onChange={(e) => setXAxisTitle(e.target.value)} />

            <label>Y Axis Title</label>
            <input type="text" value={yAxisTitle} onChange={(e) => setYAxisTitle(e.target.value)} />
          </>
        )}

        {itemType === "Table" && (
          <>
            <label>Data Lines</label>
            {dataLines.map((line, idx) => {
              const isNum = isNumeric(line.source_1);
              return (
                <div key={idx} className="analytics-popup-line">
                  <input
                    type="number"
                    placeholder="Order"
                    value={line.column_order}
                    onChange={(e) => updateLine(idx, "column_order", e.target.value)}
                  />
                  <input
                    placeholder="Column Name"
                    value={line.column_name}
                    onChange={(e) => updateLine(idx, "column_name", e.target.value)}
                  />
                  <select
                    value={line.source_1}
                    onChange={(e) => updateLine(idx, "source_1", e.target.value)}
                  >
                    <option value="">-- Source 1 --</option>
                    {columns.map((col) => (
                      <option key={col.name} value={col.name}>
                        {col.name}
                      </option>
                    ))}
                  </select>
                  <select
                    value={line.source_2}
                    onChange={(e) => updateLine(idx, "source_2", e.target.value)}
                    disabled={!isNum}
                  >
                    <option value="">-- Source 2 --</option>
                    {columns
                      .filter((c) => isNumeric(c.name))
                      .map((col) => (
                        <option key={col.name} value={col.name}>
                          {col.name}
                        </option>
                      ))}
                  </select>
                  <select
                    value={line.operation}
                    onChange={(e) => updateLine(idx, "operation", e.target.value)}
                    disabled={!isNum}
                  >
                    <option value="">-- Operation --</option>
                    <option value="add">Add</option>
                    <option value="subtract">Subtract</option>
                    <option value="multiply">Multiply</option>
                    <option value="divide">Divide</option>
                  </select>
                  <button onClick={() => setDataLines(dataLines.filter((_, i) => i !== idx))}>❌</button>
                </div>
              );
            })}
            <button
              onClick={() =>
                setDataLines([
                  ...dataLines,
                  { column_order: dataLines.length + 1, column_name: "", source_1: "", source_2: "", operation: "" },
                ])
              }
            >
              Add Line
            </button>
          </>
        )}

        {itemType === "Text" && (
          <>
            <label>Text Header</label>
            <input type="text" value={textHeader} onChange={(e) => setTextHeader(e.target.value)} />

            <label>Text Body</label>
            <textarea rows="4" value={textBody} onChange={(e) => setTextBody(e.target.value)} />
          </>
        )}

        <div className="analytics-popup-buttons">
          <button onClick={handleSubmitUpdate}>Update</button>
          <button onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default UpdateDashboardItemPopup;
