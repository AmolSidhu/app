import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class UpdateDashboardItemPopup extends StatefulWidget {
  final String dashboardSerial;
  final String dashboardItemSerial;
  final VoidCallback onClose;

  const UpdateDashboardItemPopup({
    super.key,
    required this.dashboardSerial,
    required this.dashboardItemSerial,
    required this.onClose,
  });

  @override
  State<UpdateDashboardItemPopup> createState() =>
      _UpdateDashboardItemPopupState();
}

class _UpdateDashboardItemPopupState extends State<UpdateDashboardItemPopup> {
  final _storage = const FlutterSecureStorage();

  bool loading = true;
  String error = '';

  String itemType = '';
  String graphType = '';

  List<Map<String, String>> columns = [];
  List<String> graphTypeOptions = [];
  List<Map<String, dynamic>> dataLines = [];

  final itemOrderCtrl = TextEditingController();
  final dataItemNameCtrl = TextEditingController();
  final graphTitleCtrl = TextEditingController();
  final xAxisTitleCtrl = TextEditingController();
  final yAxisTitleCtrl = TextEditingController();
  final textHeaderCtrl = TextEditingController();
  final textBodyCtrl = TextEditingController();

  String column1 = '';
  String column2 = '';

  static const operations = ['add', 'subtract', 'multiply', 'divide'];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    itemOrderCtrl.dispose();
    dataItemNameCtrl.dispose();
    graphTitleCtrl.dispose();
    xAxisTitleCtrl.dispose();
    yAxisTitleCtrl.dispose();
    textHeaderCtrl.dispose();
    textBodyCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    await _fetchColumns();
    await _fetchItem();
    setState(() => loading = false);
  }

  Future<void> _fetchColumns() async {
    final token = await _storage.read(key: 'token');
    final res = await http.get(
      Uri.parse('$server/get/data_source_detials/${widget.dashboardSerial}/'),
      headers: {'Authorization': token ?? ''},
    );

    final decoded = jsonDecode(res.body)['data'] ?? {};
    columns = decoded.entries.map<Map<String, String>>((e) {
      final List v = e.value;
      return {
        'key': e.key.toString(),
        'name': v[0].toString(),
        'type': v[1].toString(),
      };
    }).toList();
  }

  Future<void> _fetchItem() async {
    final token = await _storage.read(key: 'token');
    final res = await http.get(
      Uri.parse(
        '$server/get/dashboard_item_data/${widget.dashboardSerial}/${widget.dashboardItemSerial}/',
      ),
      headers: {'Authorization': token ?? ''},
    );

    final data = jsonDecode(res.body)['data'];

    itemType = data['item_type'];
    itemOrderCtrl.text = data['item_order'].toString();
    dataItemNameCtrl.text = data['data_item_name'] ?? '';

    if (itemType == 'Graph') {
      graphTypeOptions = List<String>.from(data['graph_type'] ?? []);
      graphType = data['current_graph_type'] ?? '';
      column1 = data['column_1'] ?? '';
      column2 = data['column_2'] ?? '';
      graphTitleCtrl.text = data['graph_title'] ?? '';
      xAxisTitleCtrl.text = data['x_axis_title'] ?? '';
      yAxisTitleCtrl.text = data['y_axis_title'] ?? '';
    }

    if (itemType == 'Table') {
      dataLines = List<Map<String, dynamic>>.from(data['data_lines'] ?? []);
    }

    if (itemType == 'Text') {
      textHeaderCtrl.text = data['text_header'] ?? '';
      textBodyCtrl.text = data['text_body'] ?? '';
    }
  }

  bool isNumeric(String? name) {
    if (name == null) return false;
    final col = columns.firstWhere((c) => c['name'] == name, orElse: () => {});
    return col['type'] == 'int64' || col['type'] == 'float64';
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.all(24),
      child: SizedBox(
        width: 1100,
        child: loading
            ? const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            : SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Update Dashboard Item',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 20),
                    _commonFields(),
                    const SizedBox(height: 24),
                    if (itemType == 'Graph') _graphSection(),
                    if (itemType == 'Table') _tableSection(),
                    if (itemType == 'Text') _textSection(),
                    const SizedBox(height: 32),
                    _actions(),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _commonFields() => Column(
    children: [
      TextField(
        controller: itemOrderCtrl,
        decoration: const InputDecoration(labelText: 'Item Order'),
        keyboardType: TextInputType.number,
      ),
      const SizedBox(height: 12),
      TextField(
        controller: dataItemNameCtrl,
        decoration: const InputDecoration(labelText: 'Data Item Name'),
      ),
    ],
  );

  Widget _graphSection() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      _sectionTitle('Graph Settings'),
      _dropdown(
        label: 'Graph Type',
        value: graphTypeOptions.contains(graphType) ? graphType : null,
        items: graphTypeOptions,
        onChanged: (v) => setState(() => graphType = v ?? ''),
      ),
      _dropdown(
        label: 'Column 1',
        value: column1.isNotEmpty ? column1 : null,
        items: columns.map((c) => c['name']).whereType<String>().toList(),
        onChanged: (v) => setState(() => column1 = v ?? ''),
      ),
      _dropdown(
        label: 'Column 2',
        value: column2.isNotEmpty ? column2 : null,
        items: columns.map((c) => c['name']).whereType<String>().toList(),
        onChanged: (v) => setState(() => column2 = v ?? ''),
      ),
      TextField(
        controller: graphTitleCtrl,
        decoration: const InputDecoration(labelText: 'Graph Title'),
      ),
      TextField(
        controller: xAxisTitleCtrl,
        decoration: const InputDecoration(labelText: 'X Axis Title'),
      ),
      TextField(
        controller: yAxisTitleCtrl,
        decoration: const InputDecoration(labelText: 'Y Axis Title'),
      ),
    ],
  );

  Widget _tableSection() {
    final List<String> colNames = columns
        .map((c) => c['name'])
        .whereType<String>()
        .toList();

    final List<String> numericColNames = columns
        .where((c) => isNumeric(c['name']))
        .map((c) => c['name'])
        .whereType<String>()
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('Table Columns'),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Column(
            children: [
              for (int i = 0; i < dataLines.length; i++)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    children: [
                      _fixedText(
                        label: 'Order',
                        value: dataLines[i]['column_order'],
                        width: 80,
                        onChanged: (v) =>
                            setState(() => dataLines[i]['column_order'] = v),
                      ),
                      _fixedText(
                        label: 'Name',
                        value: dataLines[i]['column_name'],
                        width: 160,
                        onChanged: (v) =>
                            setState(() => dataLines[i]['column_name'] = v),
                      ),
                      _fixedDropdown(
                        label: 'Source 1',
                        value: colNames.contains(dataLines[i]['source_1'])
                            ? dataLines[i]['source_1']
                            : null,
                        items: colNames,
                        width: 200,
                        onChanged: (v) => setState(() {
                          dataLines[i]['source_1'] = v ?? '';
                          if (!isNumeric(v)) {
                            dataLines[i]['source_2'] = '';
                            dataLines[i]['operation'] = '';
                          }
                        }),
                      ),
                      _fixedDropdown(
                        label: 'Source 2',
                        value:
                            numericColNames.contains(dataLines[i]['source_2'])
                            ? dataLines[i]['source_2']
                            : null,
                        items: numericColNames,
                        width: 200,
                        enabled: isNumeric(dataLines[i]['source_1']),
                        onChanged: (v) =>
                            setState(() => dataLines[i]['source_2'] = v ?? ''),
                      ),
                      _fixedDropdown(
                        label: 'Op',
                        value: operations.contains(dataLines[i]['operation'])
                            ? dataLines[i]['operation']
                            : null,
                        items: operations,
                        width: 140,
                        enabled: isNumeric(dataLines[i]['source_1']),
                        onChanged: (v) =>
                            setState(() => dataLines[i]['operation'] = v ?? ''),
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete),
                        onPressed: () => setState(() => dataLines.removeAt(i)),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        ElevatedButton.icon(
          icon: const Icon(Icons.add),
          label: const Text('Add Line'),
          onPressed: () {
            setState(() {
              dataLines.add({
                'column_order': dataLines.length + 1,
                'column_name': '',
                'source_1': '',
                'source_2': '',
                'operation': '',
              });
            });
          },
        ),
      ],
    );
  }

  Widget _textSection() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      _sectionTitle('Text Content'),
      TextField(
        controller: textHeaderCtrl,
        decoration: const InputDecoration(labelText: 'Header'),
      ),
      const SizedBox(height: 12),
      TextField(
        controller: textBodyCtrl,
        maxLines: 5,
        decoration: const InputDecoration(labelText: 'Body'),
      ),
    ],
  );

  Widget _sectionTitle(String t) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 12),
    child: Text(
      t,
      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
    ),
  );

  Widget _dropdown({
    required String label,
    required String? value,
    required List<String> items,
    required Function(String?) onChanged,
  }) => DropdownButtonFormField<String>(
    value: value,
    decoration: InputDecoration(labelText: label),
    items: items
        .map((v) => DropdownMenuItem(value: v, child: Text(v)))
        .toList(),
    onChanged: onChanged,
  );

  Widget _fixedText({
    required String label,
    required dynamic value,
    required double width,
    required Function(String) onChanged,
  }) => SizedBox(
    width: width,
    child: TextField(
      controller: TextEditingController(text: value?.toString() ?? ''),
      onChanged: onChanged,
      decoration: InputDecoration(labelText: label),
    ),
  );

  Widget _fixedDropdown({
    required String label,
    required String? value,
    required List<String> items,
    required double width,
    required Function(String?) onChanged,
    bool enabled = true,
  }) => SizedBox(
    width: width,
    child: DropdownButtonFormField<String>(
      value: value,
      decoration: InputDecoration(labelText: label),
      items: items
          .map((v) => DropdownMenuItem(value: v, child: Text(v)))
          .toList(),
      onChanged: enabled ? onChanged : null,
    ),
  );

  Widget _actions() => Row(
    mainAxisAlignment: MainAxisAlignment.end,
    children: [
      TextButton(onPressed: widget.onClose, child: const Text('Cancel')),
      const SizedBox(width: 12),
      ElevatedButton(onPressed: () {}, child: const Text('Update')),
    ],
  );
}
