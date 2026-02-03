import 'dart:html' as html;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import 'package:flutter_frontend/static/constants.dart';

class UploadScraperForm extends StatefulWidget {
  const UploadScraperForm({Key? key}) : super(key: key);

  @override
  State<UploadScraperForm> createState() => _UploadScraperFormState();
}

class _UploadScraperFormState extends State<UploadScraperForm> {
  final _storage = const FlutterSecureStorage();
  final TextEditingController _scraperNameController = TextEditingController();

  Uint8List? _fileBytes;
  String? _fileName;

  String? _message;
  bool _loading = false;
  bool _downloading = false;

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
    if (_fileBytes == null) {
      setState(() => _message = 'Please select a CSV file.');
      return;
    }

    if (_scraperNameController.text.trim().isEmpty) {
      setState(() => _message = 'Please enter a scraper name.');
      return;
    }

    setState(() {
      _loading = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      final uri = Uri.parse('$server/create/scraper/');
      final request = http.MultipartRequest('POST', uri)
        ..headers['Authorization'] = token ?? ''
        ..fields['scraper_name'] = _scraperNameController.text.trim()
        ..files.add(
          http.MultipartFile.fromBytes(
            'file',
            _fileBytes!,
            filename: _fileName,
            contentType: MediaType('text', 'csv'),
          ),
        );

      final response = await request.send();
      final responseBody = await http.Response.fromStream(response);

      if (response.statusCode == 201) {
        setState(() {
          _message = 'File uploaded successfully!';
          _fileBytes = null;
          _fileName = null;
          _scraperNameController.clear();
        });
      } else {
        setState(() {
          _message =
              'Upload failed: ${responseBody.body.isNotEmpty ? responseBody.body : response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Internal error. Please try again.';
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _downloadTemplate() async {
    setState(() {
      _downloading = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      final uri = Uri.parse('$server/get/default_template/');
      final response = await http.get(
        uri,
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode == 200) {
        final bytes = response.bodyBytes;
        final blob = html.Blob([bytes], 'text/csv');
        final url = html.Url.createObjectUrlFromBlob(blob);
        html.AnchorElement(href: url)
          ..setAttribute('download', 'default_template.csv')
          ..click();
        html.Url.revokeObjectUrl(url);

        setState(() => _message = 'Template downloaded successfully!');
      } else {
        setState(() {
          _message =
              'Failed to download template. Status code: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() => _message = 'Error downloading template.');
    } finally {
      setState(() => _downloading = false);
    }
  }

  @override
  void dispose() {
    _scraperNameController.dispose();
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
                const Text(
                  'Upload Scraper File',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),

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
                  controller: _scraperNameController,
                  decoration: const InputDecoration(
                    labelText: 'Scraper Name',
                    hintText: 'Enter scraper name',
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

                const SizedBox(height: 16),

                ElevatedButton(
                  onPressed: _downloading ? null : _downloadTemplate,
                  child: _downloading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Download Template'),
                ),

                if (_message != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 16),
                    child: Text(
                      _message!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.black87),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
