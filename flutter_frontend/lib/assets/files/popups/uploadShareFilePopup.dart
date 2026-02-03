import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class UploadShareFilePopup extends StatefulWidget {
  const UploadShareFilePopup({super.key});

  @override
  State<UploadShareFilePopup> createState() => _UploadShareFilePopupState();
}

class _UploadShareFilePopupState extends State<UploadShareFilePopup> {
  final _storage = const FlutterSecureStorage();
  final _descriptionController = TextEditingController();

  PlatformFile? _selectedFile;
  bool _sharable = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

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

      // File
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          _selectedFile!.bytes!,
          filename: _selectedFile!.name,
        ),
      );

      request.fields['file_description'] = _descriptionController.text;
      request.fields['sharable'] = _sharable ? 'True' : 'False';

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200 || response.statusCode == 201) {
        Navigator.of(context).pop(true);
      } else {
        setState(() {
          _error = responseBody.isNotEmpty
              ? responseBody
              : 'Failed to upload file';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'An error occurred: $e';
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
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              onPressed: _pickFile,
              child: Text(
                _selectedFile == null
                    ? 'Select File'
                    : 'Selected: ${_selectedFile!.name}',
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'File description'),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Checkbox(
                  value: _sharable,
                  onChanged: (value) {
                    setState(() {
                      _sharable = value ?? false;
                    });
                  },
                ),
                const Text('Sharable'),
              ],
            ),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Text(_error!, style: const TextStyle(color: Colors.red)),
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
