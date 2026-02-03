import 'dart:convert';
import 'dart:html' as html;

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class ViewVideoRequestsRequest extends StatefulWidget {
  const ViewVideoRequestsRequest({Key? key}) : super(key: key);

  @override
  State<ViewVideoRequestsRequest> createState() =>
      _ViewVideoRequestsRequestState();
}

class _ViewVideoRequestsRequestState extends State<ViewVideoRequestsRequest> {
  final _storage = const FlutterSecureStorage();

  List<dynamic> _videoRequests = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    html.document.title = 'My Video Requests';
    _fetchVideoRequests();
  }

  Future<void> _fetchVideoRequests() async {
    final token = await _storage.read(key: 'token');

    if (token == null) {
      html.window.location.href = '/login/';
      return;
    }

    try {
      final response = await http.get(
        Uri.parse('$server/get/video_requests/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);

        setState(() {
          _videoRequests = decoded['data'] ?? [];
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load video requests (${response.statusCode})';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'An error occurred: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'My Video Requests',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),

            if (_loading) const Center(child: CircularProgressIndicator()),

            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),

            if (!_loading && _error == null && _videoRequests.isEmpty)
              const Text('No video requests found.'),

            if (!_loading && _videoRequests.isNotEmpty)
              Expanded(
                child: ListView.builder(
                  itemCount: _videoRequests.length,
                  itemBuilder: (context, index) {
                    final request = _videoRequests[index];

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              request['request_title'] ?? '',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(request['request_description'] ?? ''),
                            const SizedBox(height: 8),
                            Text(
                              'Status: ${request['request_status']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
