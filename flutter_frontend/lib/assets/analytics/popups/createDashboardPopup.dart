import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateDashboardPopup extends StatefulWidget {
  final VoidCallback onClose;

  const CreateDashboardPopup({super.key, required this.onClose});

  @override
  State<CreateDashboardPopup> createState() => _CreateDashboardPopupState();
}

class _CreateDashboardPopupState extends State<CreateDashboardPopup> {
  final _storage = const FlutterSecureStorage();

  final TextEditingController dashboardNameController = TextEditingController();

  List<dynamic> dataSources = [];
  String selectedDataSource = '';

  bool loadingSources = true;
  bool creating = false;

  @override
  void initState() {
    super.initState();
    fetchDataSources();
  }

  Future<void> fetchDataSources() async {
    try {
      final token = await _storage.read(key: 'token');

      final res = await http.get(
        Uri.parse('$server/get/cleaned_data_sources/'),
        headers: {'Authorization': token ?? ''},
      );

      if (res.statusCode == 200) {
        final json = jsonDecode(res.body);
        setState(() {
          dataSources = json['data'] ?? [];
          loadingSources = false;
        });
      }
    } catch (_) {
      setState(() => loadingSources = false);
    }
  }

  Future<void> createDashboard() async {
    if (dashboardNameController.text.isEmpty || selectedDataSource.isEmpty) {
      return;
    }

    setState(() => creating = true);

    try {
      final token = await _storage.read(key: 'token');

      final res = await http.post(
        Uri.parse('$server/create/dashboard/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'dashboard_name': dashboardNameController.text,
          'data_source_serial': selectedDataSource,
        }),
      );

      if (res.statusCode == 200 || res.statusCode == 201) {
        widget.onClose();
      } else {
        _showError('Failed to create dashboard');
      }
    } catch (_) {
      _showError('An error occurred');
    } finally {
      setState(() => creating = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: SizedBox(
          width: 420,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Create New Dashboard',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),

              TextField(
                controller: dashboardNameController,
                decoration: const InputDecoration(
                  labelText: 'Dashboard Name',
                  border: OutlineInputBorder(),
                ),
              ),

              const SizedBox(height: 15),

              loadingSources
                  ? const Center(child: CircularProgressIndicator())
                  : DropdownButtonFormField<String>(
                      value: selectedDataSource.isEmpty
                          ? null
                          : selectedDataSource,
                      decoration: const InputDecoration(
                        labelText: 'Select Data Source',
                        border: OutlineInputBorder(),
                      ),
                      items: dataSources
                          .map(
                            (src) => DropdownMenuItem<String>(
                              value: src['serial'],
                              child: Text(
                                '${src['data_source_name']} (${src['file_name']})',
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: (v) =>
                          setState(() => selectedDataSource = v ?? ''),
                    ),

              const SizedBox(height: 25),

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton(
                    onPressed: creating ? null : widget.onClose,
                    child: const Text('Cancel'),
                  ),
                  ElevatedButton(
                    onPressed: creating ? null : createDashboard,
                    child: creating
                        ? const SizedBox(
                            height: 16,
                            width: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Create'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
