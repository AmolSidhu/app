import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/files/popups/uploadFolderShareFilePopup.dart';

class ViewAllShareFolderFilesRequest extends StatefulWidget {
  final String folderSerial;

  const ViewAllShareFolderFilesRequest({Key? key, required this.folderSerial})
    : super(key: key);

  @override
  State<ViewAllShareFolderFilesRequest> createState() =>
      _ViewAllShareFolderFilesRequestState();
}

class _ViewAllShareFolderFilesRequestState
    extends State<ViewAllShareFolderFilesRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Map<String, dynamic>? _folderData;
  List<Map<String, dynamic>> _files = [];

  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAll();
  }

  Future<String?> _token() async => await _storage.read(key: 'token');

  Future<void> _loadAll() async {
    setState(() => _loading = true);
    await Future.wait([_fetchFolderData(), _fetchFiles()]);
    setState(() => _loading = false);
  }

  Future<void> _fetchFolderData() async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/folder_data/${widget.folderSerial}/'),
        headers: {'Authorization': await _token() ?? ''},
      );

      final body = jsonDecode(response.body);
      if (response.statusCode != 200) {
        throw Exception(body['message']);
      }

      setState(() => _folderData = Map<String, dynamic>.from(body['data']));
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _updateFolderSharable(bool value) async {
    try {
      await http.patch(
        Uri.parse('$server/update/folder_share_status/${widget.folderSerial}/'),
        headers: {
          'Authorization': await _token() ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'sharable': value}),
      );
      _fetchFolderData();
    } catch (e) {
      _showSnack('Failed to update folder');
    }
  }

  Future<void> _copyFolderLink() async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/folder_share_link/${widget.folderSerial}/'),
        headers: {'Authorization': await _token() ?? ''},
      );

      final body = jsonDecode(response.body);
      if (response.statusCode != 200) {
        throw Exception(body['message']);
      }

      await Clipboard.setData(ClipboardData(text: body['data']['share_link']));

      _showSnack('Folder share link copied');
    } catch (e) {
      _showSnack('Failed to copy folder link');
    }
  }

  Future<void> _fetchFiles() async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/folder_files/${widget.folderSerial}/'),
        headers: {'Authorization': await _token() ?? ''},
      );

      final body = jsonDecode(response.body);
      if (response.statusCode != 200) {
        throw Exception(body['message']);
      }

      final Map<String, dynamic> fileMap = Map<String, dynamic>.from(
        body['data'] ?? {},
      );

      setState(() {
        _files = fileMap.entries
            .map(
              (e) => {
                'file_serial': e.key,
                ...Map<String, dynamic>.from(e.value),
              },
            )
            .toList();
      });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _updateFileSharable(String fileId, bool value) async {
    try {
      await http.patch(
        Uri.parse('$server/update/file_share_status/$fileId/'),
        headers: {
          'Authorization': await _token() ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'sharable': value}),
      );
      _fetchFiles();
    } catch (e) {
      _showSnack('Failed to update file');
    }
  }

  Future<void> _copyFileLink(String fileId) async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/file_share_link/$fileId/'),
        headers: {'Authorization': await _token() ?? ''},
      );

      final body = jsonDecode(response.body);
      if (response.statusCode != 200) {
        throw Exception(body['message']);
      }

      await Clipboard.setData(ClipboardData(text: body['data']['share_link']));

      _showSnack('File share link copied');
    } catch (e) {
      _showSnack('Failed to copy file link');
    }
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_error != null) {
      return Scaffold(body: Center(child: Text('Error: $_error')));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Shared Folder')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_folderData != null) ...[
              Text(
                _folderData!['folder_name'],
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 4),
              Text(_folderData!['folder_description'] ?? ''),
              SwitchListTile(
                title: const Text('Folder Sharable'),
                value: _folderData!['sharable'],
                onChanged: _updateFolderSharable,
              ),
              ElevatedButton(
                onPressed: _folderData!['sharable'] ? _copyFolderLink : null,
                child: const Text('Copy Folder Share Link'),
              ),
              const Divider(),
            ],
            ElevatedButton(
              onPressed: () async {
                final result = await showDialog(
                  context: context,
                  builder: (_) => UploadFolderShareFilePopup(
                    folderSerial: widget.folderSerial,
                  ),
                );
                if (result == true) _fetchFiles();
              },
              child: const Text('Upload File'),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: _files.isEmpty
                  ? const Text('No files found.')
                  : ListView.builder(
                      itemCount: _files.length,
                      itemBuilder: (context, index) {
                        final file = _files[index];
                        return Card(
                          child: ListTile(
                            title: Text(file['file_name']),
                            subtitle: Text(
                              '${file['file_description']} '
                              '(${file['file_type']})',
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Switch(
                                  value: file['file_share_status'],
                                  onChanged: (v) => _updateFileSharable(
                                    file['file_serial'],
                                    v,
                                  ),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.copy),
                                  onPressed: file['file_share_status']
                                      ? () => _copyFileLink(file['file_serial'])
                                      : null,
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
