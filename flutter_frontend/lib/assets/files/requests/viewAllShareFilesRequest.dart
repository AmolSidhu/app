import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/files/popups/uploadShareFilePopup.dart';

class ViewAllShareFilesRequest extends StatefulWidget {
  const ViewAllShareFilesRequest({Key? key}) : super(key: key);

  @override
  State<ViewAllShareFilesRequest> createState() =>
      _ViewAllShareFilesRequestState();
}

class _ViewAllShareFilesRequestState extends State<ViewAllShareFilesRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Map<String, dynamic> _files = {};

  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchFiles();
  }

  Future<String?> _token() async => await _storage.read(key: 'token');

  Future<void> _fetchFiles() async {
    try {
      setState(() {
        _loading = true;
        _error = null;
      });

      final response = await http.get(
        Uri.parse('$server/get/files/'),
        headers: {
          'Authorization': await _token() ?? '',
          'Content-Type': 'application/json',
        },
      );

      final body = jsonDecode(response.body);

      if (response.statusCode != 200) {
        throw Exception(body['message'] ?? 'Error fetching files');
      }

      setState(() {
        _files = body['data'] ?? {};
      });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _updateShareStatus(String fileId, bool sharable) async {
    try {
      final response = await http.patch(
        Uri.parse('$server/update/file_share_status/$fileId/'),
        headers: {
          'Authorization': await _token() ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'sharable': sharable}),
      );

      final body = jsonDecode(response.body);

      if (response.statusCode != 200) {
        throw Exception(body['message'] ?? 'Failed to update status');
      }

      _fetchFiles();
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error updating status: $e')));
    }
  }

  Future<void> _copyShareLink(String fileId) async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/file_share_link/$fileId/'),
        headers: {
          'Authorization': await _token() ?? '',
          'Content-Type': 'application/json',
        },
      );

      final body = jsonDecode(response.body);

      if (response.statusCode != 200) {
        throw Exception(body['message'] ?? 'Failed to retrieve link');
      }

      final String link = body['data']['share_link'];

      await Clipboard.setData(ClipboardData(text: link));

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Share link copied to clipboard')),
      );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> _openUploadPopup() async {
    final result = await showDialog(
      context: context,
      builder: (_) => const UploadShareFilePopup(),
    );

    if (result == true) {
      _fetchFiles();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View All Shared Files'),
        actions: [
          IconButton(
            icon: const Icon(Icons.upload_file),
            onPressed: _openUploadPopup,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text('Error: $_error'))
          : _files.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('No files found'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _openUploadPopup,
                    child: const Text('Upload File'),
                  ),
                ],
              ),
            )
          : ListView(
              children: _files.entries.map((entry) {
                final serial = entry.key;
                final file = entry.value;

                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          file['file_name'] ?? 'Unnamed File',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(file['file_description'] ?? ''),
                        Text(
                          'Type: ${file['file_type'] ?? ''}',
                          style: const TextStyle(color: Colors.grey),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Text('Sharable'),
                            Switch(
                              value: file['file_share_status'] == true,
                              onChanged: (val) =>
                                  _updateShareStatus(serial, val),
                            ),
                            const Spacer(),
                            TextButton.icon(
                              icon: const Icon(Icons.link),
                              label: const Text('Copy Link'),
                              onPressed: file['file_share_status'] == true
                                  ? () => _copyShareLink(serial)
                                  : null,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
    );
  }
}
