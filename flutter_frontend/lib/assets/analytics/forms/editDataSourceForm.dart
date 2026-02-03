import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:pluto_grid/pluto_grid.dart';
import 'package:flutter_frontend/static/constants.dart';

class EditDataSourceForm extends StatefulWidget {
  const EditDataSourceForm({Key? key}) : super(key: key);

  @override
  State<EditDataSourceForm> createState() => _EditDataSourceFormState();
}

class _EditDataSourceFormState extends State<EditDataSourceForm> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> dataSources = [];
  String? selectedSerial;
  List<Map<String, dynamic>> tableData = [];
  List<String> headers = [];
  Map<String, String> editableTypes = {};

  List<String> columnCleaningOptions = [];
  List<String> rowCleaningOptions = [];
  Map<String, String?> columnCleaning = {};
  String? rowCleaning;
  bool overrideColumnWithRow = false;

  PlutoGridStateManager? stateManager;

  @override
  void initState() {
    super.initState();
    fetchDataSources();
  }

  Future<String> _getToken() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('Token missing');
    return token;
  }

  Future<void> fetchDataSources() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/data_sources/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );
      final result = jsonDecode(response.body);
      if (!mounted) return;
      setState(() {
        dataSources = List<Map<String, dynamic>>.from(result['data'] ?? []);
      });
    } catch (e) {
      debugPrint('Error fetching data sources: $e');
    }
  }

  Future<void> fetchCleaningOptions() async {
    if (selectedSerial == null) return;
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/data_source_cleaning_methods/$selectedSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );
      final result = jsonDecode(response.body);
      if (!mounted) return;

      setState(() {
        columnCleaningOptions = List<String>.from(result['columns'] ?? []);
        rowCleaningOptions = List<String>.from(result['rows'] ?? []);
        columnCleaning = Map<String, String?>.from(
          result['selected_columns'] ?? {},
        );
        rowCleaning = result['selected_rows'];
        overrideColumnWithRow = result['selected_override'] ?? false;
      });
    } catch (e) {
      debugPrint('Error fetching cleaning options: $e');
    }
  }

  Future<void> fetchDataSourceLines(String serial) async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/data_source_lines/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      final result = jsonDecode(response.body);
      if (!mounted) return;

      final data = List<Map<String, dynamic>>.from(result['data'] ?? []);
      setState(() {
        tableData = data;
        headers = data.isNotEmpty ? data.first.keys.toList() : [];
        editableTypes = {for (var h in headers) h: 'object'};
      });

      await fetchCleaningOptions();
    } catch (e) {
      debugPrint('Error fetching lines: $e');
    }
  }

  Future<void> saveCleaningOptions() async {
    if (selectedSerial == null) return;
    try {
      final token = await _getToken();
      final response = await http.patch(
        Uri.parse(
          '$server/update/data_source_cleaning_methods/$selectedSerial/',
        ),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'column_cleaning_methods': columnCleaning,
          'row_cleaning_method': rowCleaning,
          'override_column_with_row': overrideColumnWithRow,
        }),
      );
      final result = jsonDecode(response.body);
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cleaning methods saved!')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message'] ?? 'Failed to save cleaning methods.',
            ),
          ),
        );
      }
    } catch (e) {
      debugPrint('Error saving cleaning options: $e');
    }
  }

  Future<void> saveData() async {
    if (selectedSerial == null) return;
    try {
      final token = await _getToken();
      final response = await http.patch(
        Uri.parse('$server/update/data_source_lines/$selectedSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({'data': tableData, 'column_types': editableTypes}),
      );
      final result = jsonDecode(response.body);
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Data saved!')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'] ?? 'Failed to save data.')),
        );
      }
    } catch (e) {
      debugPrint('Error saving data: $e');
    }
  }

  Future<void> resetData() async {
    if (selectedSerial == null) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset Data'),
        content: const Text('Reset data to original?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    try {
      final token = await _getToken();
      final response = await http.delete(
        Uri.parse('$server/reset/data_source_lines/$selectedSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );
      final result = jsonDecode(response.body);
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Data reset!')));
        fetchDataSourceLines(selectedSerial!);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'] ?? 'Failed to reset data.')),
        );
      }
    } catch (e) {
      debugPrint('Error resetting data: $e');
    }
  }

  List<PlutoColumn> _buildColumns() {
    return headers
        .map(
          (h) => PlutoColumn(title: h, field: h, type: PlutoColumnType.text()),
        )
        .toList();
  }

  List<PlutoRow> _buildRows() {
    return tableData
        .map(
          (row) => PlutoRow(
            cells: {
              for (var h in headers)
                h: PlutoCell(value: row[h]?.toString() ?? ''),
            },
          ),
        )
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Edit Data Source',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 12),
            DropdownButton<String>(
              value: selectedSerial,
              hint: const Text('Select Data Source'),
              items: dataSources
                  .map(
                    (ds) => DropdownMenuItem<String>(
                      value: ds['serial'],
                      child: Text(
                        '${ds['data_source_name']} (${ds['file_name']})',
                      ),
                    ),
                  )
                  .toList(),
              onChanged: (v) {
                setState(() {
                  selectedSerial = v;
                  tableData = [];
                  headers = [];
                  editableTypes = {};
                  columnCleaning = {};
                  rowCleaning = null;
                  overrideColumnWithRow = false;
                });
                if (v != null) fetchDataSourceLines(v);
              },
            ),

            const SizedBox(height: 16),

            if (headers.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Column Cleaning Methods',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: headers
                        .map(
                          (col) => Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(col),
                              DropdownButton<String>(
                                value: columnCleaning[col],
                                items: columnCleaningOptions
                                    .map(
                                      (opt) => DropdownMenuItem<String>(
                                        value: opt,
                                        child: Text(opt),
                                      ),
                                    )
                                    .toList(),
                                onChanged: (v) {
                                  setState(() {
                                    columnCleaning[col] = v;
                                  });
                                },
                              ),
                            ],
                          ),
                        )
                        .toList(),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Row Cleaning Method',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  DropdownButton<String>(
                    value: rowCleaning,
                    items: rowCleaningOptions
                        .map(
                          (opt) => DropdownMenuItem<String>(
                            value: opt,
                            child: Text(opt),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      setState(() {
                        rowCleaning = v;
                      });
                    },
                  ),
                  Row(
                    children: [
                      Checkbox(
                        value: overrideColumnWithRow,
                        onChanged: (v) =>
                            setState(() => overrideColumnWithRow = v ?? false),
                      ),
                      const Text('Override Column Cleaning with Row Cleaning'),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: saveCleaningOptions,
                    child: const Text('Save Cleaning Methods'),
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            if (headers.isNotEmpty)
              SizedBox(
                height: 400,
                child: PlutoGrid(
                  columns: _buildColumns(),
                  rows: _buildRows(),
                  onLoaded: (event) {
                    stateManager = event.stateManager;
                  },
                  configuration: const PlutoGridConfiguration(),
                ),
              ),

            const SizedBox(height: 16),
            if (headers.isNotEmpty)
              Row(
                children: [
                  ElevatedButton(
                    onPressed: saveData,
                    child: const Text('Save Table Data'),
                  ),
                  const SizedBox(width: 12),
                  ElevatedButton(
                    onPressed: resetData,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    child: const Text('Reset Table Data'),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
