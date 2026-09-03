import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class UploadFolderShareFilePopup extends StatefulWidget {
  final String? folderSerial;

  const UploadFolderShareFilePopup({super.key, this.folderSerial});

  @override
  State<UploadFolderShareFilePopup> createState() =>
      _UploadFolderShareFilePopupState();
}

class _UploadFolderShareFilePopupState
    extends State<UploadFolderShareFilePopup> {
  final _storage = const FlutterSecureStorage();
  final _descriptionController = TextEditingController();

  PlatformFile? _selectedFile;
  bool _sharable = false;
  bool _loading = false;
  String? _error;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(withData: true);

    if (result != null && result.files.isNotEmpty) {
      setState(() {
        _selectedFile = result.files.first;
      });
    }
  }

  Future<void> _uploadFile() async {
    if (_selectedFile == null) {
      setState(() {
        _error = "Please select a file to upload.";
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$server/upload/file/'),
      );

      request.headers['Authorization'] = token ?? '';

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          _selectedFile!.bytes as Uint8List,
          filename: _selectedFile!.name,
        ),
      );

      request.fields['file_description'] = _descriptionController.text;
      request.fields['sharable'] = _sharable ? 'True' : 'False';

      if (widget.folderSerial != null) {
        request.fields['folder_serial'] = widget.folderSerial!;
      }

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode != 200 && response.statusCode != 201) {
        throw Exception(responseBody);
      }

      Navigator.of(context).pop(true);
    } catch (e) {
      setState(() {
        _error = "Error uploading file: $e";
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
      title: const Text('Upload File'),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton(
              onPressed: _pickFile,
              child: const Text('Select File'),
            ),
            if (_selectedFile != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_selectedFile!.name),
              ),
            const SizedBox(height: 12),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'File description'),
            ),
            const SizedBox(height: 8),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Sharable'),
              value: _sharable,
              onChanged: (value) {
                setState(() {
                  _sharable = value ?? false;
                });
              },
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _loading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _loading ? null : _uploadFile,
          child: _loading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Upload'),
        ),
      ],
    );
  }
}
