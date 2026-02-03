import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class AdminVideoRequestApprovalRequest extends StatefulWidget {
  const AdminVideoRequestApprovalRequest({super.key});

  @override
  State<AdminVideoRequestApprovalRequest> createState() =>
      _AdminVideoRequestApprovalRequestState();
}

class _AdminVideoRequestApprovalRequestState
    extends State<AdminVideoRequestApprovalRequest> {
  final FlutterSecureStorage storage = const FlutterSecureStorage();

  bool loading = true;
  List<String> statuses = [];
  Map<String, List<Map<String, dynamic>>> requestData = {};

  Future<Map<String, String>> _authHeaders() async {
    return {
      'Authorization': await storage.read(key: 'token') ?? '',
      'Admin-Token': await storage.read(key: 'adminToken') ?? '',
    };
  }

  Future<void> loadStatuses() async {
    final res = await http.get(
      Uri.parse('$server/admins/video_request_options/'),
      headers: await _authHeaders(),
    );

    final data = jsonDecode(res.body);
    statuses = List<String>.from(data['data'] ?? []);
  }

  Future<List<Map<String, dynamic>>> loadRequestsForStatus(
    String status,
  ) async {
    final res = await http.get(
      Uri.parse('$server/admins/video_requests/$status/'),
      headers: await _authHeaders(),
    );

    final data = jsonDecode(res.body)['data'] ?? {};
    return List<Map<String, dynamic>>.from(data.values);
  }

  Future<void> init() async {
    setState(() => loading = true);

    await loadStatuses();

    final Map<String, List<Map<String, dynamic>>> temp = {};
    for (final status in statuses) {
      temp[status] = await loadRequestsForStatus(status);
    }

    setState(() {
      requestData = temp;
      loading = false;
    });
  }

  Future<void> updateStatus(String serial, String newStatus) async {
    await http.patch(
      Uri.parse('$server/admins/review_video_request/$serial/'),
      headers: {...(await _authHeaders()), 'Content-Type': 'application/json'},
      body: jsonEncode({'request_status': newStatus}),
    );

    await init();
  }

  @override
  void initState() {
    super.initState();
    init();
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Video Request Approval')),
      body: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: statuses.map((status) {
            final requests = requestData[status] ?? [];

            return Container(
              width: 320,
              margin: const EdgeInsets.all(12),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade400),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    status,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 10),

                  if (requests.isEmpty)
                    const Text('No requests in this status'),

                  ...requests.map((req) {
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(8),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              req['requeset_title'] ?? '',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text('User: ${req['username']}'),
                            Text('Date: ${req['request_date']}'),
                            const SizedBox(height: 6),
                            Text(req['request_description'] ?? ''),
                            const SizedBox(height: 8),

                            DropdownButton<String>(
                              value: status,
                              isExpanded: true,
                              items: statuses
                                  .map(
                                    (s) => DropdownMenuItem(
                                      value: s,
                                      child: Text(s),
                                    ),
                                  )
                                  .toList(),
                              onChanged: (value) {
                                if (value != null && value != status) {
                                  updateStatus(req['serial'].toString(), value);
                                }
                              },
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}
