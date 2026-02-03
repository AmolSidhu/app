import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

import 'package:flutter_frontend/assets/analytics/popups/createDashboardItemPopup.dart';
import 'package:flutter_frontend/assets/analytics/popups/updateDashboardItemPopup.dart';

import 'package:flutter_frontend/pages/analytics/viewDashboardPage.dart';

class ViewDashboardsRequest extends StatefulWidget {
  const ViewDashboardsRequest({super.key});

  @override
  State<ViewDashboardsRequest> createState() => _ViewDashboardsRequestState();
}

class _ViewDashboardsRequestState extends State<ViewDashboardsRequest> {
  final _storage = const FlutterSecureStorage();

  bool loading = true;

  List<dynamic> dashboards = [];
  Map<String, bool> expanded = {};
  Map<String, List<dynamic>> dashboardItems = {};

  String? activeDashboardSerial;
  String? editingItemSerial;

  @override
  void initState() {
    super.initState();
    _checkAuthAndLoad();
  }

  Future<void> _checkAuthAndLoad() async {
    final token = await _storage.read(key: 'token');
    if (token == null) {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
      }
      return;
    }
    await fetchDashboards();
  }

  Future<void> fetchDashboards() async {
    try {
      final token = await _storage.read(key: 'token');

      final res = await http.get(
        Uri.parse('$server/get/dashboards/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (res.statusCode == 200) {
        final json = jsonDecode(res.body);
        setState(() {
          dashboards = json['data'] ?? [];
          loading = false;
        });
      }
    } catch (e) {
      setState(() => loading = false);
    }
  }

  Future<void> fetchDashboardItems(String serial) async {
    try {
      final token = await _storage.read(key: 'token');

      final res = await http.get(
        Uri.parse('$server/get/dashboard_items/$serial/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (res.statusCode == 200) {
        final json = jsonDecode(res.body);
        setState(() {
          dashboardItems[serial] = List<dynamic>.from(json['data'] ?? []);
        });
      }
    } catch (_) {}
  }

  void toggleExpand(String serial) async {
    setState(() {
      expanded[serial] = !(expanded[serial] ?? false);
    });

    if (!dashboardItems.containsKey(serial)) {
      await fetchDashboardItems(serial);
    }
  }

  void openCreatePopup(String serial) {
    setState(() => activeDashboardSerial = serial);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => CreateDashboardItemPopup(
        dashboardSerial: serial,
        onClose: () {
          Navigator.pop(context);
          fetchDashboardItems(serial);
          setState(() => activeDashboardSerial = null);
        },
      ),
    );
  }

  void openEditPopup(String dashboardSerial, String itemSerial) {
    setState(() {
      activeDashboardSerial = dashboardSerial;
      editingItemSerial = itemSerial;
    });

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => UpdateDashboardItemPopup(
        dashboardSerial: dashboardSerial,
        dashboardItemSerial: itemSerial,
        onClose: () {
          Navigator.pop(context);
          fetchDashboardItems(dashboardSerial);
          setState(() {
            activeDashboardSerial = null;
            editingItemSerial = null;
          });
        },
      ),
    );
  }

  Future<void> openViewDashboard(String serial) async {
    await _storage.write(key: 'dashboardSerial', value: serial);

    if (!mounted) return;

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => ViewDashboardPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('My Dashboards')),
      body: dashboards.isEmpty
          ? const Center(child: Text('No dashboards found.'))
          : ListView.builder(
              itemCount: dashboards.length,
              itemBuilder: (context, index) {
                final dashboard = dashboards[index];
                final serial = dashboard['dashboard_serial'];

                return Card(
                  margin: const EdgeInsets.all(10),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          dashboard['dashboard_name'],
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Created on: ${DateTime.parse(dashboard['date_created']).toLocal().toString().split(' ').first}',
                        ),
                        TextButton(
                          onPressed: () => openViewDashboard(serial),
                          child: const Text('View Dashboard'),
                        ),
                        TextButton(
                          onPressed: () => toggleExpand(serial),
                          child: Text(
                            expanded[serial] == true ? 'Collapse' : 'Expand',
                          ),
                        ),
                        if (expanded[serial] == true)
                          Padding(
                            padding: const EdgeInsets.only(left: 16, top: 10),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Dashboard Items',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                if (!dashboardItems.containsKey(serial))
                                  const Padding(
                                    padding: EdgeInsets.all(8),
                                    child: CircularProgressIndicator(),
                                  )
                                else
                                  Column(
                                    children: dashboardItems[serial]!
                                        .map(
                                          (item) => ListTile(
                                            contentPadding: EdgeInsets.zero,
                                            title: Text(
                                              'Type: ${item['item_type']}, Order: ${item['item_order']}',
                                            ),
                                            trailing: TextButton(
                                              onPressed: () => openEditPopup(
                                                serial,
                                                item['dashboard_item_serial'],
                                              ),
                                              child: const Text('Edit Item'),
                                            ),
                                          ),
                                        )
                                        .toList(),
                                  ),
                                const SizedBox(height: 10),
                                ElevatedButton(
                                  onPressed: () => openCreatePopup(serial),
                                  child: const Text('Add Dashboard Item'),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
