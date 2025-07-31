import React, { useState } from "react";
import server from "../Static/Constants";

const CreateDashboardItemPopup = ({ dashboardSerial, onClose }) => {
    const [itemType, setItemType] = useState("Graph");
    const [itemOrder, setItemOrder] = useState("");
    const [error, setError] = useState("");
    const [step, setStep] = useState(1);
    const [dashboardItemSerial, setDashboardItemSerial] = useState(null);

    const [dataItemName, setDataItemName] = useState("");
    const [columnsMeta, setColumnsMeta] = useState({});

    const [graphType, setGraphType] = useState("bar");
    const [cleaningMethod, setCleaningMethod] = useState("drop_duplicates");
    const [columns, setColumns] = useState([]);
    const [column1, setColumn1] = useState("");
    const [column2, setColumn2] = useState("");
    const [graphTitle, setGraphTitle] = useState("");
    const [xAxisTitle, setXAxisTitle] = useState("");
    const [yAxisTitle, setYAxisTitle] = useState("");

    const [dataLines, setDataLines] = useState([
        {
            column_order: 1,
            column_name: "",
            source_1: "",
            source_2: "",
            operation: "",
        },
    ]);

    const [textHeader, setTextHeader] = useState("");
    const [textBody, setTextBody] = useState("");

    const handleCreateItem = async () => {
        if (!itemType || !itemOrder) {
            setError("Please select item type and order.");
            return;
        }

        try {
            const response = await fetch(`${server}/create/dashboard_item/${dashboardSerial}/`, {
                method: "POST",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ item_type: itemType, item_order: itemOrder }),
            });

            if (response.ok) {
                const data = await response.json();
                setDashboardItemSerial(data.dashboard_item_serial);
                await fetchColumnMetadata();
                setStep(2);
            } else {
                const errorData = await response.json();
                setError(errorData.message || "Failed to create item.");
            }
        } catch (error) {
            console.error("Error creating item:", error);
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
                setColumnsMeta(result.data || {});
            } else {
                console.warn("Could not fetch column metadata");
            }
        } catch (e) {
            console.error("Failed to fetch column metadata", e);
        }
    };

    const handleSubmitDataDetails = async () => {
        const basePayload = {
            data_item_name: dataItemName,
            data_item_type: itemType,
        };

        let extraPayload = {};

        if (itemType === "Graph") {
            extraPayload = {
                graph_type: graphType,
                cleaning_method: cleaningMethod,
                columns,
                column_1: column1,
                column_2: column2,
                graph_title: graphTitle,
                x_axis_title: xAxisTitle,
                y_axis_title: yAxisTitle,
            };
        } else if (itemType === "Table") {
            extraPayload = { data_lines: dataLines };
        } else if (itemType === "Text") {
            extraPayload = { text_header: textHeader, text_body: textBody };
        }

        try {
            const response = await fetch(
                `${server}/create/dashboard_item_data/${dashboardSerial}/${dashboardItemSerial}/`,
                {
                    method: "POST",
                    headers: {
                        Authorization: localStorage.getItem("token"),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ ...basePayload, ...extraPayload }),
                }
            );

            if (response.ok) {
                alert("Dashboard item and data created!");
                onClose();
            } else {
                const errorData = await response.json();
                setError(errorData.message || "Failed to submit item data.");
            }
        } catch (e) {
            console.error("Submission failed", e);
            setError("Unexpected error occurred.");
        }
    };

    const numericColumns = Object.entries(columnsMeta)
        .filter(([_, [, type]]) => type === "int64" || type === "float64")
        .map(([_, [name]]) => name);

    const allColumns = Object.entries(columnsMeta).map(([_, [name]]) => name);

    const isColumnNumeric = (columnName) => {
        const entry = Object.entries(columnsMeta).find(([_, [name]]) => name === columnName);
        if (!entry) return false;
        const [, [, type]] = entry;
        return type === "int64" || type === "float64";
    };

    const updateDataLine = (index, field, value) => {
        const updatedLines = [...dataLines];
        updatedLines[index][field] = value;

        if (field === "source_1") {
            const isNumeric = isColumnNumeric(value);
            if (!isNumeric) {
                updatedLines[index].source_2 = "";
                updatedLines[index].operation = "";
            }
        }

        setDataLines(updatedLines);
    };

    return (
        <div className="analytics-popup">
            <div className="analytics-popup-inner">
                {step === 1 && (
                    <>
                        <h3>Create Dashboard Item</h3>
                        {error && <p className="analytics-popup-error">{error}</p>}
                        <label>Item Type:</label>
                        <select value={itemType} onChange={(e) => setItemType(e.target.value)}>
                            <option value="Graph">Graph</option>
                            <option value="Table">Table</option>
                            <option value="Text">Text</option>
                        </select>

                        <label>Item Order:</label>
                        <input
                            type="number"
                            value={itemOrder}
                            onChange={(e) => setItemOrder(e.target.value)}
                        />

                        <div className="analytics-popup-buttons">
                            <button onClick={handleCreateItem}>Next</button>
                            <button onClick={onClose}>Cancel</button>
                        </div>
                    </>
                )}

                {step === 2 && (
                    <>
                        <h3>Configure {itemType}</h3>
                        {error && <p className="analytics-popup-error">{error}</p>}

                        <label>Data Item Name:</label>
                        <input
                            type="text"
                            value={dataItemName}
                            onChange={(e) => setDataItemName(e.target.value)}
                        />

                        {itemType === "Graph" && (
                            <>
                                <label>Graph Type:</label>
                                <select value={graphType} onChange={(e) => setGraphType(e.target.value)}>
                                    <option value="bar">Bar</option>
                                    <option value="line">Line</option>
                                    <option value="pie">Pie</option>
                                    <option value="scatter">Scatter</option>
                                    <option value="heatmap">Heatmap</option>
                                    <option value="box">Box</option>
                                    <option value="violin">Violin</option>
                                </select>

                                <label>Cleaning Method:</label>
                                <select
                                    value={cleaningMethod}
                                    onChange={(e) => setCleaningMethod(e.target.value)}
                                >
                                    <option value="drop_duplicates">Drop Duplicates</option>
                                    <option value="drop_columns">Drop Columns</option>
                                    <option value="drop_rows">Drop Rows</option>
                                    <option value="replace">Replace</option>
                                    <option value="fillna">FillNA</option>
                                </select>

                                <label>Columns:</label>
                                <select
                                    multiple
                                    value={columns}
                                    onChange={(e) =>
                                        setColumns([...e.target.selectedOptions].map((opt) => opt.value))
                                    }
                                >
                                    {allColumns.map((col) => (
                                        <option key={col} value={col}>
                                            {col}
                                        </option>
                                    ))}
                                </select>

                                <label>Column 1:</label>
                                <select value={column1} onChange={(e) => setColumn1(e.target.value)}>
                                    <option value="">--</option>
                                    {allColumns.map((col) => (
                                        <option key={col} value={col}>
                                            {col}
                                        </option>
                                    ))}
                                </select>

                                <label>Column 2:</label>
                                <select value={column2} onChange={(e) => setColumn2(e.target.value)}>
                                    <option value="">--</option>
                                    {allColumns.map((col) => (
                                        <option key={col} value={col}>
                                            {col}
                                        </option>
                                    ))}
                                </select>

                                <label>Graph Title:</label>
                                <input value={graphTitle} onChange={(e) => setGraphTitle(e.target.value)} />

                                <label>X Axis Title:</label>
                                <input value={xAxisTitle} onChange={(e) => setXAxisTitle(e.target.value)} />

                                <label>Y Axis Title:</label>
                                <input value={yAxisTitle} onChange={(e) => setYAxisTitle(e.target.value)} />
                            </>
                        )}

                        {itemType === "Table" && (
                            <>
                                <label>Data Lines:</label>
                                {dataLines.map((line, idx) => {
                                    const isNumeric = isColumnNumeric(line.source_1);
                                    return (
                                        <div className="analytics-popup-line" key={idx}>
                                            <input
                                                placeholder="Order"
                                                value={line.column_order}
                                                onChange={(e) =>
                                                    updateDataLine(idx, "column_order", e.target.value)
                                                }
                                            />
                                            <input
                                                placeholder="Name"
                                                value={line.column_name}
                                                onChange={(e) =>
                                                    updateDataLine(idx, "column_name", e.target.value)
                                                }
                                            />
                                            <select
                                                value={line.source_1}
                                                onChange={(e) =>
                                                    updateDataLine(idx, "source_1", e.target.value)
                                                }
                                            >
                                                <option value="">-- source 1 --</option>
                                                {allColumns.map((col) => (
                                                    <option key={col} value={col}>
                                                        {col}
                                                    </option>
                                                ))}
                                            </select>
                                            <select
                                                value={line.source_2}
                                                disabled={!isNumeric}
                                                onChange={(e) =>
                                                    updateDataLine(idx, "source_2", e.target.value)
                                                }
                                            >
                                                <option value="">-- source 2 --</option>
                                                {numericColumns.map((col) => (
                                                    <option key={col} value={col}>
                                                        {col}
                                                    </option>
                                                ))}
                                            </select>
                                            <select
                                                value={line.operation}
                                                disabled={!isNumeric}
                                                onChange={(e) =>
                                                    updateDataLine(idx, "operation", e.target.value)
                                                }
                                            >
                                                <option value="">-- operation --</option>
                                                <option value="add">Add</option>
                                                <option value="subtract">Subtract</option>
                                                <option value="multiply">Multiply</option>
                                                <option value="divide">Divide</option>
                                            </select>
                                        </div>
                                    );
                                })}
                                <button
                                    onClick={() =>
                                        setDataLines([
                                            ...dataLines,
                                            {
                                                column_order: dataLines.length + 1,
                                                column_name: "",
                                                source_1: "",
                                                source_2: "",
                                                operation: "",
                                            },
                                        ])
                                    }
                                >
                                    Add Line
                                </button>
                            </>
                        )}

                        {itemType === "Text" && (
                            <>
                                <label>Header:</label>
                                <input
                                    value={textHeader}
                                    onChange={(e) => setTextHeader(e.target.value)}
                                />
                                <label>Body:</label>
                                <textarea
                                    value={textBody}
                                    onChange={(e) => setTextBody(e.target.value)}
                                />
                            </>
                        )}

                        <div className="analytics-popup-buttons">
                            <button onClick={handleSubmitDataDetails}>Submit</button>
                            <button onClick={onClose}>Cancel</button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default CreateDashboardItemPopup;
