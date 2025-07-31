import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const EditDataSourceForm = () => {
    const [dataSources, setDataSources] = useState([]);
    const [selectedSerial, setSelectedSerial] = useState("");
    const [tableData, setTableData] = useState([]);
    const [headers, setHeaders] = useState([]);
    const [editableTypes, setEditableTypes] = useState({});

    const [cleaningOptions, setCleaningOptions] = useState({ columns: [], rows: [] });
    const [columnCleaning, setColumnCleaning] = useState({});
    const [rowCleaning, setRowCleaning] = useState("");
    const [overrideColumnWithRow, setOverrideColumnWithRow] = useState(false);

    useEffect(() => {
        const fetchDataSources = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}/get/data_sources/`, {
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });
                const result = await response.json();
                if (result.data) setDataSources(result.data);
            } catch (error) {
                console.error("Error fetching data sources:", error);
            }
        };

        fetchDataSources();
    }, []);

    useEffect(() => {
        const fetchCleaningOptions = async () => {
            if (!selectedSerial) return;
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${server}/get/data_source_cleaning_methods/${selectedSerial}/`, {
                    headers: {
                        Authorization: token,
                        "Content-Type": "application/json",
                    },
                });
                const result = await response.json();
                console.log("Cleaning Options Response:", result);

                if (response.ok) {
                    setCleaningOptions({
                        columns: Array.isArray(result.columns) ? result.columns : [],
                        rows: Array.isArray(result.rows) ? result.rows : [],
                    });

                    if (result.selected_columns !== null && typeof result.selected_columns === "object") {
                        setColumnCleaning(result.selected_columns);
                    } else {
                        setColumnCleaning({});
                    }

                    if (typeof result.selected_rows === "string") {
                        setRowCleaning(result.selected_rows);
                    } else {
                        setRowCleaning("");
                    }

                    if (typeof result.selected_override === "boolean") {
                        setOverrideColumnWithRow(result.selected_override);
                    } else {
                        setOverrideColumnWithRow(false);
                    }
                } else {
                    console.warn("Failed to fetch cleaning options:", result.message);
                }
            } catch (error) {
                console.error("Error fetching cleaning options:", error);
            }
        };

        fetchCleaningOptions();
    }, [selectedSerial]);

    const fetchDataSourceLines = async (serial) => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/get/data_source_lines/${serial}/`, {
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });
            const result = await response.json();

            if (result.data && result.data.length > 0) {
                setTableData(result.data);
                const keys = Object.keys(result.data[0]);
                setHeaders(keys);

                const colMap = {};
                for (const key in result.rows) {
                    const [colName, type] = result.rows[key];
                    colMap[colName] = type;
                }

                setEditableTypes(colMap);
            } else {
                setTableData([]);
                setHeaders([]);
                setEditableTypes({});
            }
        } catch (error) {
            console.error("Error fetching lines:", error);
        }
    };

    const handleDataSourceChange = (e) => {
        const serial = e.target.value;
        setSelectedSerial(serial);
        if (serial) fetchDataSourceLines(serial);
        else {
            setTableData([]);
            setHeaders([]);
            setEditableTypes({});
            setColumnCleaning({});
            setRowCleaning("");
            setOverrideColumnWithRow(false);
        }
    };

    const handleCellChange = (rowIndex, key, value) => {
        const expectedType = editableTypes[key];
        let isValid = true;

        if (expectedType === "int64") isValid = /^-?\d+$/.test(value);
        else if (expectedType === "float64") isValid = /^-?\d+(\.\d+)?$/.test(value);

        if (!isValid) {
            alert(`Invalid value for "${key}". Must be ${expectedType}.`);
            return;
        }

        const updated = [...tableData];
        updated[rowIndex] = { ...updated[rowIndex], [key]: value };
        setTableData(updated);
    };

    const handleTypeChange = (col, type) => {
        setEditableTypes((prev) => ({ ...prev, [col]: type }));
    };

    const handleCleaningChange = (col, method) => {
        setColumnCleaning((prev) => ({ ...prev, [col]: method }));
    };

    const handleSaveCleaning = async () => {
        if (!selectedSerial) return alert("Please select a data source first.");
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/update/data_source_cleaning_methods/${selectedSerial}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    column_cleaning_methods: columnCleaning,
                    row_cleaning_method: rowCleaning,
                    override_column_with_row: overrideColumnWithRow,
                }),
            });
            const result = await response.json();
            if (response.ok) {
                alert("Cleaning methods saved!");
            } else {
                alert(result.message || "Failed to save cleaning methods.");
            }
        } catch (err) {
            console.error("Cleaning save error:", err);
            alert("Error saving cleaning methods.");
        }
    };

    const handleSave = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/update/data_source_lines/${selectedSerial}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    data: tableData,
                    column_types: editableTypes,
                }),
            });
            const result = await response.json();
            if (response.ok) alert("Data saved!");
            else alert(result.message || "Failed to save.");
        } catch (err) {
            console.error("Save error:", err);
            alert("Error saving data.");
        }
    };

    const handleReset = async () => {
        if (!selectedSerial) return;
        if (!window.confirm("Reset data to original?")) return;

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${server}/reset/data_source_lines/${selectedSerial}/`, {
                method: "DELETE",
                headers: {
                    Authorization: token,
                    "Content-Type": "application/json",
                },
            });
            const result = await response.json();
            if (response.ok) {
                alert("Data reset!");
                fetchDataSourceLines(selectedSerial);
            } else {
                alert(result.message || "Failed to reset.");
            }
        } catch (err) {
            console.error("Reset error:", err);
            alert("Error resetting data.");
        }
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Edit Data Source</h2>

            <select onChange={handleDataSourceChange} value={selectedSerial}>
                <option value="">Select Data Source</option>
                {dataSources.map((ds) => (
                    <option key={ds.serial} value={ds.serial}>
                        {ds.data_source_name} ({ds.file_name})
                    </option>
                ))}
            </select>

            <div style={{ border: "1px solid #ccc", padding: "15px", marginTop: "20px" }}>
                <h3>Cleaning Methods</h3>

                <div style={{ marginBottom: "10px" }}>
                    <label><strong>Override Column Cleaning with Row Cleaning:</strong></label>{" "}
                    <input
                        type="checkbox"
                        checked={overrideColumnWithRow}
                        onChange={(e) => setOverrideColumnWithRow(e.target.checked)}
                    />
                </div>

                <div style={{ marginBottom: "10px" }}>
                    <label><strong>Row Cleaning Method:</strong></label>{" "}
                    <select value={rowCleaning} onChange={(e) => setRowCleaning(e.target.value)}>
                        <option value="">Select</option>
                        {cleaningOptions.rows.map((opt) => (
                            <option key={opt} value={opt}>
                                {opt}
                            </option>
                        ))}
                    </select>
                </div>

                {headers.length > 0 && (
                    <div>
                        <label><strong>Column Cleaning Methods:</strong></label>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginTop: "10px" }}>
                            {headers.map((col) => (
                                <div key={col}>
                                    <label>{col}</label>
                                    <select
                                        value={columnCleaning[col] || ""}
                                        onChange={(e) => handleCleaningChange(col, e.target.value)}
                                    >
                                        <option value="">Select</option>
                                        {cleaningOptions.columns.map((opt) => (
                                            <option key={opt} value={opt}>
                                                {opt}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <button
                    onClick={handleSaveCleaning}
                    style={{ marginTop: "10px", backgroundColor: "#4caf50", color: "white" }}
                >
                    Save Cleaning Methods
                </button>
            </div>

            {headers.length > 0 && (
                <div style={{ marginTop: "20px", overflowX: "auto" }}>
                    <table border="1" style={{ borderCollapse: "collapse", minWidth: "800px" }}>
                        <thead>
                            <tr>
                                {headers.map((header) => (
                                    <th key={header}>
                                        {header}
                                        <br />
                                        <select
                                            value={editableTypes[header]}
                                            onChange={(e) => handleTypeChange(header, e.target.value)}
                                        >
                                            <option value="int64">int</option>
                                            <option value="float64">float</option>
                                            <option value="object">string</option>
                                        </select>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {headers.map((key) => (
                                        <td key={key}>
                                            <input
                                                type="text"
                                                value={row[key]}
                                                onChange={(e) => handleCellChange(rowIndex, key, e.target.value)}
                                                style={{ width: "100px" }}
                                            />
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div style={{ marginTop: "10px" }}>
                        <button onClick={handleSave} style={{ marginRight: "10px" }}>
                            Save
                        </button>
                        <button
                            onClick={handleReset}
                            style={{ backgroundColor: "#f44336", color: "white" }}
                        >
                            Reset Data
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EditDataSourceForm;
