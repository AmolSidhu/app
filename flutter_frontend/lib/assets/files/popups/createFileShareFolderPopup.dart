import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateFileShareFolderPopup extends StatefulWidget {
  final VoidCallback onCreateSuccess;

  const CreateFileShareFolderPopup({Key? key, required this.onCreateSuccess})
    : super(key: key);

  @override
  State<CreateFileShareFolderPopup> createState() =>
      _CreateFileShareFolderPopupState();
}

class _CreateFileShareFolderPopupState
    extends State<CreateFileShareFolderPopup> {
  final _storage = const FlutterSecureStorage();

  final TextEditingController _folderNameController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  bool _sharable = false;
  bool _loading = false;
  String? _errorMessage;

  Future<void> _handleSubmit() async {
    if (_folderNameController.text.trim().isEmpty) {
      setState(() {
        _errorMessage = 'Please enter a folder name.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _errorMessage = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.post(
        Uri.parse('$server/create/upload_folder/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'folder_name': _folderNameController.text.trim(),
          'folder_description': _descriptionController.text.trim(),
          'sharable': _sharable ? 'True' : 'False',
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode != 200) {
        throw Exception(data['message'] ?? 'Failed to create folder');
      }

      widget.onCreateSuccess();
      Navigator.of(context).pop();
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create New Folder'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _folderNameController,
              decoration: const InputDecoration(labelText: 'Folder Name'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 3,
            ),
            const SizedBox(height: 12),
            CheckboxListTile(
              title: const Text('Sharable'),
              value: _sharable,
              onChanged: _loading
                  ? null
                  : (value) {
                      setState(() {
                        _sharable = value ?? false;
                      });
                    },
              controlAffinity: ListTileControlAffinity.leading,
            ),
            if (_errorMessage != null) ...[
              const SizedBox(height: 8),
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _loading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _loading ? null : _handleSubmit,
          child: _loading
              ? const SizedBox(
                  height: 16,
                  width: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create Folder'),
        ),
      ],
    );
  }
}
