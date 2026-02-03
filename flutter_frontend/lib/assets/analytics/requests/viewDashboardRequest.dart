import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class ViewDashboardRequest extends StatefulWidget {
  const ViewDashboardRequest({super.key});

  @override
  State<ViewDashboardRequest> createState() => _ViewDashboardRequestState();
}

class _ViewDashboardRequestState extends State<ViewDashboardRequest> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool loading = true;
  String error = '';
  Map<String, dynamic>? dashboardData;

  @override
  void initState() {
    super.initState();
    fetchDashboardData();
  }

  Future<void> fetchDashboardData() async {
    try {
      final token = await secureStorage.read(key: 'token');
      final dashboardSerial = await secureStorage.read(key: 'dashboardSerial');

      if (token == null) {
        throw Exception('Authentication token missing');
      }

      if (dashboardSerial == null) {
        throw Exception('No dashboard serial provided');
      }

      final response = await http.get(
        Uri.parse('$server/get/dashboard_item_serials/$dashboardSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        final err = jsonDecode(response.body);
        throw Exception(err['message'] ?? 'Failed to fetch dashboard items');
      }

      final json = jsonDecode(response.body);
      final Map<String, dynamic> items = json['dashboard_items'];

      final List<Map<String, dynamic>> itemDetails = [];

      for (final itemSerial in items.keys) {
        try {
          final itemResponse = await http.get(
            Uri.parse(
              '$server/get/dashboard_item/$dashboardSerial/$itemSerial/',
            ),
            headers: {
              'Authorization': token,
              'Content-Type': 'application/json',
            },
          );

          if (itemResponse.statusCode != 200) {
            continue;
          }

          final itemJson = jsonDecode(itemResponse.body);
          itemDetails.add({'serial': itemSerial, ...itemJson['data']});
        } catch (_) {}
      }

      setState(() {
        dashboardData = {
          'dashboardSerial': dashboardSerial,
          'items': itemDetails,
        };
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (error.isNotEmpty) {
      return Scaffold(body: Center(child: Text('Error: $error')));
    }

    final items = dashboardData!['items'] as List<dynamic>;

    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard: ${dashboardData!['dashboardSerial']}'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView.builder(
          itemCount: items.length,
          itemBuilder: (context, index) {
            final item = items[index];

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${item['data_item_name']} (${item['item_type']})',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 4),
                    Text(item['data_item_description'] ?? ''),

                    const SizedBox(height: 12),

                    if (item['item_type'] == 'Graph') ...[
                      Text('Graph: ${item['graph_title']}'),
                      Text('X: ${item['column_1']}, Y: ${item['column_2']}'),
                      Text('Type: ${item['current_graph_type']}'),
                    ],

                    if (item['item_type'] == 'Table') ...[
                      const Text('Table:'),
                      const SizedBox(height: 4),
                      ...List<Widget>.from(
                        (item['data_lines'] as List<dynamic>).map(
                          (line) => Text(
                            '${line['column_name']} '
                            '(Order: ${line['column_order']}) '
                            '- ${line['operation']}',
                          ),
                        ),
                      ),
                    ],

                    if (item['item_type'] == 'Text') ...[
                      Text(
                        item['text_header'] ?? '',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: 4),
                      Text(item['text_body'] ?? ''),
                    ],
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
