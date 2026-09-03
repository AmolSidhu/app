import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'dart:convert';

class ViewOption {
  final String userView;
  final String fieldName;

  ViewOption({required this.userView, required this.fieldName});
}

class MagicColumnsViewOptionsPopup extends StatefulWidget {
  final VoidCallback? onSaved;

  const MagicColumnsViewOptionsPopup({Key? key, this.onSaved})
    : super(key: key);

  @override
  State<MagicColumnsViewOptionsPopup> createState() =>
      _MagicColumnsViewOptionsPopupState();
}

class _MagicColumnsViewOptionsPopupState
    extends State<MagicColumnsViewOptionsPopup> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<ViewOption> used = [];
  List<ViewOption> unused = [];
  bool loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchOptions();
  }

  Future<void> _fetchOptions() async {
    setStateIfMounted(() {
      loading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/magic_card_all_view_options/'),
        headers: {'Authorization': token ?? ''},
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        List<ViewOption> parseFromObjects(dynamic list) {
          if (list is List) {
            return list.map<ViewOption>((item) {
              if (item is Map<String, dynamic>) {
                final userView = item['user_view']?.toString() ?? '';
                final fieldName = item['field_name']?.toString() ?? '';
                return ViewOption(userView: userView, fieldName: fieldName);
              }
              return ViewOption(
                userView: item.toString(),
                fieldName: item.toString(),
              );
            }).toList();
          }
          return [];
        }

        List<ViewOption> parseFromStrings(dynamic list) {
          if (list is List) {
            return list
                .map<ViewOption>(
                  (e) => ViewOption(
                    userView: e.toString(),
                    fieldName: e.toString(),
                  ),
                )
                .toList();
          }
          return [];
        }

        List<ViewOption> newUsed = [];
        List<ViewOption> newUnused = [];

        if (data.containsKey('used_options') ||
            data.containsKey('unused_options')) {
          newUsed = parseFromObjects(data['used_options']);
          newUnused = parseFromObjects(data['unused_options']);
        } else if (data.containsKey('used_fields') ||
            data.containsKey('unused_fields')) {
          newUsed = parseFromStrings(data['used_fields']);
          newUnused = parseFromStrings(data['unused_fields']);
        } else if (data.containsKey('data')) {
          final inner = data['data'];
          if (inner is Map<String, dynamic>) {
            if (inner.containsKey('used_options') ||
                inner.containsKey('unused_options')) {
              newUsed = parseFromObjects(inner['used_options']);
              newUnused = parseFromObjects(inner['unused_options']);
            } else {
              newUsed = parseFromStrings(inner['used_fields']);
              newUnused = parseFromStrings(inner['unused_fields']);
            }
          }
        }

        setStateIfMounted(() {
          used = newUsed;
          unused = newUnused;
          loading = false;
        });
      } else {
        setStateIfMounted(() {
          _error = 'Failed to load view options (${response.statusCode})';
          loading = false;
        });
      }
    } catch (e) {
      setStateIfMounted(() {
        _error = 'Internal server error loading view options';
        loading = false;
      });
    }
  }

  Future<void> _save() async {
    try {
      final token = await _storage.read(key: 'token');

      final body = {
        "active_fields": used
            .map((e) => e.fieldName.isNotEmpty ? e.fieldName : e.userView)
            .toList(),
      };

      final response = await http.patch(
        Uri.parse('$server/update/magic_card_view_options/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200 || response.statusCode == 204) {
        widget.onSaved?.call();
      } else {
        setStateIfMounted(() {
          _error = 'Failed to save (${response.statusCode})';
        });
      }
    } catch (e) {
      setStateIfMounted(() {
        _error = 'Internal server error saving view options';
      });
    }
  }

  Future<void> _reset() async {
    try {
      final token = await _storage.read(key: 'token');

      final response = await http.delete(
        Uri.parse('$server/reset/magic_card_view_options/'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode == 200) {
        await _fetchOptions();
        widget.onSaved?.call();
      } else {
        setStateIfMounted(() {
          _error = 'Failed to reset (${response.statusCode})';
        });
      }
    } catch (e) {
      setStateIfMounted(() {
        _error = 'Internal server error resetting view options';
      });
    }
  }

  void moveUp(List<ViewOption> list, int index) {
    if (index == 0) return;
    setStateIfMounted(() {
      final item = list.removeAt(index);
      list.insert(index - 1, item);
    });
  }

  void moveDown(List<ViewOption> list, int index) {
    if (index == list.length - 1) return;
    setStateIfMounted(() {
      final item = list.removeAt(index);
      list.insert(index + 1, item);
    });
  }

  void moveToOtherList(
    List<ViewOption> from,
    List<ViewOption> to,
    ViewOption item,
  ) {
    setStateIfMounted(() {
      from.remove(item);
      to.add(item);
    });
  }

  void setStateIfMounted(VoidCallback fn) {
    if (!mounted) return;
    setState(fn);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("View Options"),
      content: SizedBox(
        width: 700,
        height: 450,
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
            ? Center(child: Text(_error!))
            : Row(
                children: [
                  Expanded(child: _buildList("Unused", unused, false)),
                  const VerticalDivider(),
                  Expanded(child: _buildList("Used", used, true)),
                ],
              ),
      ),
      actions: [
        TextButton(onPressed: _reset, child: const Text("Reset")),
        TextButton(
          onPressed: () async {
            await _save();
            if (mounted) Navigator.of(context).pop();
          },
          child: const Text("Save"),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text("Close"),
        ),
      ],
    );
  }

  Widget _buildList(String title, List<ViewOption> list, bool isUsedList) {
    return Column(
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Expanded(
          child: ListView.builder(
            itemCount: list.length,
            itemBuilder: (context, index) {
              final item = list[index];

              return Card(
                child: ListTile(
                  title: Text(item.userView),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.arrow_upward),
                        onPressed: () => moveUp(list, index),
                      ),
                      IconButton(
                        icon: const Icon(Icons.arrow_downward),
                        onPressed: () => moveDown(list, index),
                      ),
                      IconButton(
                        icon: Icon(
                          isUsedList ? Icons.arrow_back : Icons.arrow_forward,
                        ),
                        onPressed: () {
                          if (isUsedList) {
                            moveToOtherList(used, unused, item);
                          } else {
                            moveToOtherList(unused, used, item);
                          }
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
