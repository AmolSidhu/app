import 'dart:html' as html;
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class ArticleFileUploadForm extends StatefulWidget {
  const ArticleFileUploadForm({Key? key}) : super(key: key);

  @override
  State<ArticleFileUploadForm> createState() => _ArticleFileUploadFormState();
}

class _ArticleFileUploadFormState extends State<ArticleFileUploadForm> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  html.File? _selectedFile;
  bool _loading = false;
  String? _message;

  final List<String> _allowedExtensions = [
    '.txt',
    '.md',
    '.json',
    '.html',
    '.jsonl',
  ];

  void _pickFile() {
    final uploadInput = html.FileUploadInputElement();
    uploadInput.accept = _allowedExtensions.join(',');
    uploadInput.click();

    uploadInput.onChange.listen((event) {
      final files = uploadInput.files;
      if (files != null && files.isNotEmpty) {
        setState(() {
          _selectedFile = files.first;
          _message = null;
        });
      }
    });
  }

  Future<void> _uploadFile() async {
    if (_selectedFile == null) {
      setState(() {
        _message = 'Please select a file first.';
      });
      return;
    }

    final extension = _selectedFile!.name.substring(
      _selectedFile!.name.lastIndexOf('.'),
    );

    if (!_allowedExtensions.contains(extension.toLowerCase())) {
      setState(() {
        _message =
            'Invalid file type. Allowed: ${_allowedExtensions.join(', ')}';
      });
      return;
    }

    setState(() {
      _loading = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final formData = html.FormData();
      formData.appendBlob('file', _selectedFile!, _selectedFile!.name);

      final request = html.HttpRequest();
      request
        ..open('POST', '$server/upload/article_files/')
        ..setRequestHeader('Authorization', token ?? '')
        ..onLoadEnd.listen((_) {
          if (request.status != null &&
              request.status! >= 200 &&
              request.status! < 300) {
            final response = jsonDecode(request.responseText ?? '{}');
            setState(() {
              _message = response['message'] ?? 'File uploaded successfully!';
              _selectedFile = null;
            });
          } else {
            final response = jsonDecode(request.responseText ?? '{}');
            setState(() {
              _message = response['message'] ?? 'Error uploading file.';
            });
          }
          setState(() {
            _loading = false;
          });
        })
        ..send(formData);
    } catch (e) {
      setState(() {
        _message = 'Internal error. Please try again.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ElevatedButton(
          onPressed: _loading ? null : _pickFile,
          child: const Text('Select File'),
        ),
        if (_selectedFile != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('Selected: ${_selectedFile!.name}'),
          ),
        const SizedBox(height: 16),
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
        if (_message != null) ...[const SizedBox(height: 16), Text(_message!)],
      ],
    );
  }
}
