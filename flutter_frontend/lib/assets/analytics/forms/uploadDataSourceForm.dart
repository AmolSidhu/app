import 'dart:html' as html;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import 'package:flutter_frontend/static/constants.dart';

class UploadDataSourceForm extends StatefulWidget {
  const UploadDataSourceForm({Key? key}) : super(key: key);

  @override
  State<UploadDataSourceForm> createState() => _UploadDataSourceFormState();
}

class _UploadDataSourceFormState extends State<UploadDataSourceForm> {
  final _storage = const FlutterSecureStorage();
  final TextEditingController _dataSourceNameController =
      TextEditingController();

  Uint8List? _fileBytes;
  String? _fileName;

  String? _message;
  bool _loading = false;

  void _pickCsvFile() {
    final uploadInput = html.FileUploadInputElement()..accept = '.csv';
    uploadInput.click();

    uploadInput.onChange.listen((_) {
      final file = uploadInput.files?.first;
      if (file == null) return;

      if (!file.name.endsWith('.csv')) {
        setState(() => _message = 'Please upload a valid CSV file.');
        return;
      }

      final reader = html.FileReader();
      reader.readAsArrayBuffer(file);
      reader.onLoadEnd.listen((_) {
        setState(() {
          _fileBytes = reader.result as Uint8List;
          _fileName = file.name;
          _message = null;
        });
      });
    });
  }

  Future<void> _handleUpload() async {
    if (_fileBytes == null || _dataSourceNameController.text.trim().isEmpty) {
      setState(() {
        _message = 'Both file and data source name are required.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      if (token == null) throw Exception('Not authenticated');

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$server/upload/data_source/'),
      );

      request.headers['Authorization'] = token;
      request.fields['data_source_name'] = _dataSourceNameController.text
          .trim();

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          _fileBytes!,
          filename: _fileName,
          contentType: MediaType('text', 'csv'),
        ),
      );

      final response = await request.send();
      final body = await http.Response.fromStream(response);

      setState(() {
        _message = body.body.isNotEmpty ? body.body : 'Upload successful.';
      });
    } catch (e) {
      setState(() {
        _message = 'Error uploading data source: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  void dispose() {
    _dataSourceNameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ElevatedButton(
                  onPressed: _pickCsvFile,
                  child: const Text('Choose CSV File'),
                ),

                if (_fileName != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text('Selected file: $_fileName'),
                  ),

                const SizedBox(height: 24),

                TextField(
                  controller: _dataSourceNameController,
                  decoration: const InputDecoration(
                    labelText: 'Data Source Name',
                    hintText: 'Enter data source name',
                    border: OutlineInputBorder(),
                  ),
                ),

                const SizedBox(height: 24),

                ElevatedButton(
                  onPressed: _loading ? null : _handleUpload,
                  child: _loading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Upload'),
                ),

                if (_message != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 16),
                    child: Text(_message!, textAlign: TextAlign.center),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
