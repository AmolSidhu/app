import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateDashboardItemPopup extends StatefulWidget {
  final String dashboardSerial;
  final VoidCallback onClose;

  const CreateDashboardItemPopup({
    super.key,
    required this.dashboardSerial,
    required this.onClose,
  });

  @override
  State<CreateDashboardItemPopup> createState() =>
      _CreateDashboardItemPopupState();
}

class _CreateDashboardItemPopupState extends State<CreateDashboardItemPopup> {
  final _storage = const FlutterSecureStorage();

  int step = 1;
  String error = '';

  String itemType = 'Graph';
  String itemOrder = '';
  String? dashboardItemSerial;

  String dataItemName = '';

  Map<String, dynamic> columnsMeta = {};

  // Graph
  String graphType = 'bar';
  String cleaningMethod = 'drop_duplicates';
  List<String> columns = [];
  String column1 = '';
  String column2 = '';
  String graphTitle = '';
  String xAxisTitle = '';
  String yAxisTitle = '';

  // Table
  List<Map<String, dynamic>> dataLines = [
    {
      'column_order': 1,
      'column_name': '',
      'source_1': '',
      'source_2': '',
      'operation': '',
    },
  ];

  // Text
  String textHeader = '';
  String textBody = '';

  List<String> get allColumns =>
      columnsMeta.values.map<String>((e) => e[0]).toList();

  List<String> get numericColumns => columnsMeta.values
      .where((e) => e[1] == 'int64' || e[1] == 'float64')
      .map<String>((e) => e[0])
      .toList();

  bool isNumeric(String col) => columnsMeta.values.any(
    (e) => e[0] == col && (e[1] == 'int64' || e[1] == 'float64'),
  );

  /* ------------------ API ------------------ */

  Future<void> createItem() async {
    if (itemOrder.isEmpty) {
      setState(() => error = 'Please select item type and order.');
      return;
    }

    final token = await _storage.read(key: 'token');

    final res = await http.post(
      Uri.parse('$server/create/dashboard_item/${widget.dashboardSerial}/'),
      headers: {
        'Authorization': token ?? '',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'item_type': itemType, 'item_order': itemOrder}),
    );

    if (res.statusCode == 200 || res.statusCode == 201) {
      final data = jsonDecode(res.body);
      dashboardItemSerial = data['dashboard_item_serial'];
      await fetchColumns();
      setState(() => step = 2);
    } else {
      setState(() => error = 'Failed to create item');
    }
  }

  Future<void> fetchColumns() async {
    final token = await _storage.read(key: 'token');

    final res = await http.get(
      Uri.parse('$server/get/data_source_detials/${widget.dashboardSerial}/'),
      headers: {'Authorization': token ?? ''},
    );

    if (res.statusCode == 200) {
      setState(() {
        columnsMeta = jsonDecode(res.body)['data'] ?? {};
      });
    }
  }

  Future<void> submitDetails() async {
    final token = await _storage.read(key: 'token');

    final payload = {
      'data_item_name': dataItemName,
      'data_item_type': itemType,
      if (itemType == 'Graph') ...{
        'graph_type': graphType,
        'cleaning_method': cleaningMethod,
        'columns': columns,
        'column_1': column1,
        'column_2': column2,
        'graph_title': graphTitle,
        'x_axis_title': xAxisTitle,
        'y_axis_title': yAxisTitle,
      },
      if (itemType == 'Table') 'data_lines': dataLines,
      if (itemType == 'Text') ...{
        'text_header': textHeader,
        'text_body': textBody,
      },
    };

    final res = await http.post(
      Uri.parse(
        '$server/create/dashboard_item_data/${widget.dashboardSerial}/$dashboardItemSerial/',
      ),
      headers: {
        'Authorization': token ?? '',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(payload),
    );

    if (res.statusCode == 200 || res.statusCode == 201) {
      widget.onClose();
    } else {
      setState(() => error = 'Failed to submit item data');
    }
  }

  /* ------------------ UI ------------------ */

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: step == 1 ? buildStep1() : buildStep2(),
      ),
    );
  }

  Widget buildStep1() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      const Text('Create Dashboard Item', style: TextStyle(fontSize: 18)),
      if (error.isNotEmpty)
        Text(error, style: const TextStyle(color: Colors.red)),
      dropdown('Item Type', itemType, [
        'Graph',
        'Table',
        'Text',
      ], (v) => setState(() => itemType = v)),
      textField('Item Order', (v) => itemOrder = v, number: true),
      actions(createItem),
    ],
  );

  Widget buildStep2() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text('Configure $itemType', style: const TextStyle(fontSize: 18)),
      if (error.isNotEmpty)
        Text(error, style: const TextStyle(color: Colors.red)),
      textField('Data Item Name', (v) => dataItemName = v),
      if (itemType == 'Graph') buildGraph(),
      if (itemType == 'Table') buildTable(),
      if (itemType == 'Text') buildText(),
      actions(submitDetails),
    ],
  );

  Widget buildGraph() => Column(
    children: [
      dropdown('Graph Type', graphType, [
        'bar',
        'line',
        'pie',
        'scatter',
        'heatmap',
        'box',
        'violin',
      ], (v) => setState(() => graphType = v)),
      dropdown('Cleaning Method', cleaningMethod, [
        'drop_duplicates',
        'drop_columns',
        'drop_rows',
        'replace',
        'fillna',
      ], (v) => setState(() => cleaningMethod = v)),
      multiSelect('Columns', columns),
      dropdown(
        'Column 1',
        column1,
        allColumns,
        (v) => setState(() => column1 = v),
      ),
      dropdown(
        'Column 2',
        column2,
        allColumns,
        (v) => setState(() => column2 = v),
      ),
      textField('Graph Title', (v) => graphTitle = v),
      textField('X Axis Title', (v) => xAxisTitle = v),
      textField('Y Axis Title', (v) => yAxisTitle = v),
    ],
  );

  Widget buildTable() => Column(
    children: [
      for (int i = 0; i < dataLines.length; i++)
        Row(
          children: [
            smallField(
              'Order',
              dataLines[i]['column_order'].toString(),
              (v) => dataLines[i]['column_order'] = v,
            ),
            smallField(
              'Name',
              dataLines[i]['column_name'],
              (v) => dataLines[i]['column_name'] = v,
            ),
            dropdownInline('Source 1', dataLines[i]['source_1'], allColumns, (
              v,
            ) {
              dataLines[i]['source_1'] = v;
              if (!isNumeric(v)) {
                dataLines[i]['source_2'] = '';
                dataLines[i]['operation'] = '';
              }
              setState(() {});
            }),
            dropdownInline(
              'Source 2',
              dataLines[i]['source_2'],
              numericColumns,
              (v) => setState(() => dataLines[i]['source_2'] = v),
              enabled: isNumeric(dataLines[i]['source_1']),
            ),
            dropdownInline(
              'Op',
              dataLines[i]['operation'],
              ['add', 'subtract', 'multiply', 'divide'],
              (v) => setState(() => dataLines[i]['operation'] = v),
              enabled: isNumeric(dataLines[i]['source_1']),
            ),
          ],
        ),
      ElevatedButton(
        onPressed: () => setState(() {
          dataLines.add({
            'column_order': dataLines.length + 1,
            'column_name': '',
            'source_1': '',
            'source_2': '',
            'operation': '',
          });
        }),
        child: const Text('Add Line'),
      ),
    ],
  );

  Widget buildText() => Column(
    children: [
      textField('Header', (v) => textHeader = v),
      textField('Body', (v) => textBody = v, multiline: true),
    ],
  );

  /* ------------------ Helpers ------------------ */

  Widget textField(
    String label,
    Function(String) onChange, {
    bool number = false,
    bool multiline = false,
  }) => TextField(
    decoration: InputDecoration(labelText: label),
    keyboardType: number ? TextInputType.number : TextInputType.text,
    maxLines: multiline ? 4 : 1,
    onChanged: onChange,
  );

  Widget smallField(String label, String value, Function(String) onChange) =>
      SizedBox(
        width: 80,
        child: TextField(
          decoration: InputDecoration(labelText: label),
          controller: TextEditingController(text: value),
          onChanged: onChange,
        ),
      );

  Widget dropdown(
    String label,
    String value,
    List<String> items,
    Function(String) onChange,
  ) => DropdownButtonFormField(
    decoration: InputDecoration(labelText: label),
    value: value.isEmpty ? null : value,
    items: items
        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
        .toList(),
    onChanged: (v) => onChange(v!),
  );

  Widget dropdownInline(
    String label,
    String value,
    List<String> items,
    Function(String) onChange, {
    bool enabled = true,
  }) => SizedBox(
    width: 120,
    child: DropdownButtonFormField(
      decoration: InputDecoration(labelText: label),
      value: value.isEmpty ? null : value,
      items: items
          .map((e) => DropdownMenuItem(value: e, child: Text(e)))
          .toList(),
      onChanged: enabled ? (v) => onChange(v! as String) : null,
    ),
  );

  Widget multiSelect(String label, List<String> values) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label),
      Wrap(
        children: allColumns
            .map(
              (e) => CheckboxListTile(
                title: Text(e),
                value: values.contains(e),
                onChanged: (v) => setState(() {
                  v! ? values.add(e) : values.remove(e);
                }),
              ),
            )
            .toList(),
      ),
    ],
  );

  Widget actions(VoidCallback onSubmit) => Row(
    mainAxisAlignment: MainAxisAlignment.end,
    children: [
      TextButton(onPressed: widget.onClose, child: const Text('Cancel')),
      ElevatedButton(onPressed: onSubmit, child: const Text('Submit')),
    ],
  );
}
