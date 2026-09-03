import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:flutter_frontend/static/constants.dart';

class MagicCardFilterPopup extends StatefulWidget {
  final VoidCallback? onSaved;

  const MagicCardFilterPopup({Key? key, this.onSaved}) : super(key: key);

  @override
  State<MagicCardFilterPopup> createState() => _MagicCardFilterPopupState();
}

class _MagicCardFilterPopupState extends State<MagicCardFilterPopup> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Map<String, dynamic> filterSchema = {};
  Map<String, dynamic> magicParams = {};
  bool loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadFilters();
  }

  Future<void> _loadFilters() async {
    setState(() {
      loading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/magic_card_view_filters/'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        filterSchema = data['data'];

        final saved = await _storage.read(key: 'magic_params');
        if (saved != null) {
          magicParams = json.decode(saved);
        }

        setState(() => loading = false);
      } else {
        setState(() {
          _error = 'Failed to load filter schema: ${response.statusCode}';
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading filters: $e';
        loading = false;
      });
    }
  }

  String buildSqlQuery(Map<String, dynamic> params) {
    final List<String> parts = [];

    params.forEach((key, value) {
      if (key.endsWith("_op")) return;
      if (value == null) return;

      final op = params["${key}_op"];

      if (value is bool && op == null) {
        parts.add("$key=${value ? 'true' : 'false'}");
        return;
      }

      if (key.contains("_white") ||
          key.contains("_blue") ||
          key.contains("_black") ||
          key.contains("_red") ||
          key.contains("_green") ||
          key.contains("_colourless")) {
        parts.add("$key=${value ? 'true' : 'false'}");
        return;
      }

      if (op != null) {
        switch (op) {
          case "eq":
            parts.add("$key='$value'");
            break;
          case "ne":
            parts.add("$key!='$value'");
            break;
          case "gt":
            parts.add("$key>$value");
            break;
          case "gte":
            parts.add("$key>=$value");
            break;
          case "lt":
            parts.add("$key<$value");
            break;
          case "lte":
            parts.add("$key<=$value");
            break;
          case "has":
          case "con":
            parts.add("$key LIKE '%$value%'");
            break;
        }
      }
    });

    return parts.join(" AND ");
  }

  Future<void> _saveParams() async {
    final sql = buildSqlQuery(magicParams);
    await _storage.write(key: 'magic_params', value: json.encode(magicParams));
    await _storage.write(key: 'magic_sql', value: sql);

    widget.onSaved?.call();
    Navigator.pop(context);
  }

  Future<void> _resetParams() async {
    await _storage.delete(key: 'magic_params');
    await _storage.delete(key: 'magic_sql');

    setState(() {
      magicParams = {};
    });

    widget.onSaved?.call();
    Navigator.pop(context);
  }

  dynamic toggleTriState(dynamic current) {
    if (current == null) return true;
    if (current == true) return false;
    return null;
  }

  Widget operatorDropdown(String field, List<dynamic> ops) {
    return DropdownButton<String>(
      value: magicParams["${field}_op"] as String?,
      hint: const Text("Op"),
      items: ops
          .map(
            (o) => DropdownMenuItem<String>(
              value: o.toString(),
              child: Text(o.toString()),
            ),
          )
          .toList(),
      onChanged: (v) {
        setState(() => magicParams["${field}_op"] = v);
      },
    );
  }

  Widget valueInput(String field) {
    return Expanded(
      child: TextField(
        controller: TextEditingController(
          text: magicParams[field]?.toString() ?? "",
        ),
        onChanged: (v) => magicParams[field] = v,
        decoration: const InputDecoration(
          border: OutlineInputBorder(),
          isDense: true,
        ),
      ),
    );
  }

  Widget booleanTriState(String field) {
    final val = magicParams[field];

    IconData icon;
    if (val == null)
      icon = Icons.indeterminate_check_box_outlined;
    else if (val == true)
      icon = Icons.check_box;
    else
      icon = Icons.close;

    return IconButton(
      icon: Icon(icon),
      onPressed: () {
        setState(() => magicParams[field] = toggleTriState(val));
      },
    );
  }

  Widget colourSelector(String field) {
    const colours = ["white", "blue", "black", "red", "green", "colourless"];

    return Wrap(
      spacing: 8,
      children: colours.map((c) {
        final key = "${field}_$c";
        final val = magicParams[key];

        IconData icon;
        if (val == null)
          icon = Icons.circle_outlined;
        else if (val == true)
          icon = Icons.circle;
        else
          icon = Icons.cancel;

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(c),
            IconButton(
              icon: Icon(icon),
              onPressed: () {
                setState(() => magicParams[key] = toggleTriState(val));
              },
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget buildFilterRow(String field, Map<String, dynamic> meta) {
    if (meta['queryable'] != true) return const SizedBox.shrink();

    final dataType = meta['data_type'];
    final filters = meta['filters'];
    final userView = meta['user_view'];

    if (field == "colours" || field == "colour_identity") {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(userView, style: const TextStyle(fontWeight: FontWeight.bold)),
          colourSelector(field),
          const Divider(),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(userView, style: const TextStyle(fontWeight: FontWeight.bold)),
        Row(
          children: [
            if (filters != null && filters.contains("bool") == false)
              operatorDropdown(field, filters),

            if (dataType == "boolean")
              booleanTriState(field)
            else
              valueInput(field),
          ],
        ),
        const Divider(),
      ],
    );
  }

  Widget buildOrderSection() {
    final orderableFields = filterSchema.entries
        .where((e) => e.value["orderable"] == true)
        .map((e) => e.key)
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("Order By", style: TextStyle(fontWeight: FontWeight.bold)),
        DropdownButton<String>(
          value: magicParams["order_by"],
          hint: const Text("Select field"),
          items: orderableFields
              .map(
                (f) => DropdownMenuItem<String>(
                  value: f,
                  child: Text(filterSchema[f]["user_view"]),
                ),
              )
              .toList(),
          onChanged: (v) {
            setState(() => magicParams["order_by"] = v);
          },
        ),
        DropdownButton<String>(
          value: magicParams["order_dir"],
          hint: const Text("Direction"),
          items: const [
            DropdownMenuItem(value: "asc", child: Text("Ascending")),
            DropdownMenuItem(value: "desc", child: Text("Descending")),
          ],
          onChanged: (v) {
            setState(() => magicParams["order_dir"] = v);
          },
        ),
        const Divider(),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(child: Text(_error!));
    }

    return Scaffold(
      appBar: AppBar(title: const Text("Magic Card Filters")),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                buildOrderSection(),
                ...filterSchema.entries
                    .map((e) => buildFilterRow(e.key, e.value))
                    .toList(),
              ],
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    onPressed: _resetParams,
                    child: const Text("Reset"),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _saveParams,
                    child: const Text("Save"),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
