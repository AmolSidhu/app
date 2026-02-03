import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/files/popups/createFileShareFolderPopup.dart';
import 'package:flutter_frontend/assets/files/requests/viewAllShareFolderFilesRequest.dart';

class ViewAllShareFoldersRequest extends StatefulWidget {
  const ViewAllShareFoldersRequest({Key? key}) : super(key: key);

  @override
  State<ViewAllShareFoldersRequest> createState() =>
      _ViewAllShareFoldersRequestState();
}

class _ViewAllShareFoldersRequestState
    extends State<ViewAllShareFoldersRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> _shareFolders = [];
  bool _loading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchShareFolders();
  }

  Future<void> _fetchShareFolders() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/folders/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final Map<String, dynamic> foldersMap =
            (data['data'] as Map<String, dynamic>?) ?? {};

        final List<Map<String, dynamic>> foldersList = foldersMap.entries
            .map<Map<String, dynamic>>((entry) {
              final Map<String, dynamic> folderData = Map<String, dynamic>.from(
                entry.value as Map,
              );

              return {'serial': entry.key, ...folderData};
            })
            .toList();

        setState(() {
          _shareFolders = foldersList;
        });
      } else {
        setState(() {
          _errorMessage = data['message'] ?? 'Failed to load folders';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error fetching folders: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  void _openCreateFolderPopup() {
    showDialog(
      context: context,
      builder: (context) {
        return CreateFileShareFolderPopup(
          onCreateSuccess: () {
            Navigator.pop(context);
            _fetchShareFolders();
          },
        );
      },
    );
  }

  void _openFolder(Map<String, dynamic> folder) {
    final String folderSerial = folder['serial'];

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            ViewAllShareFolderFilesRequest(folderSerial: folderSerial),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View All Shared Folders'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _fetchShareFolders,
          ),
          IconButton(
            icon: const Icon(Icons.create_new_folder),
            onPressed: _openCreateFolderPopup,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
          ? Center(child: Text(_errorMessage!))
          : _shareFolders.isEmpty
          ? const Center(child: Text('No folders found'))
          : ListView.builder(
              itemCount: _shareFolders.length,
              itemBuilder: (context, index) {
                final folder = _shareFolders[index];

                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  child: ListTile(
                    title: Text(
                      folder['folder_name'] ?? 'Unnamed Folder',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(folder['folder_description'] ?? ''),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () => _openFolder(folder),
                  ),
                );
              },
            ),
    );
  }
}
