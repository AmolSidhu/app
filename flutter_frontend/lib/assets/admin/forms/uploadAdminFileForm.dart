import 'dart:convert';
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class UploadAdminFileForm extends StatefulWidget {
  const UploadAdminFileForm({Key? key}) : super(key: key);

  @override
  State<UploadAdminFileForm> createState() => _UploadAdminFileFormState();
}

class _UploadAdminFileFormState extends State<UploadAdminFileForm> {
  final storage = const FlutterSecureStorage();

  html.File? selectedFile;
  String? fileName;

  List<String> adminOptions = [];
  String? selectedOption = "Select process";

  String error = '';
  String message = '';

  @override
  void initState() {
    super.initState();
    _fetchAdminOptions();
  }

  Future<void> _fetchAdminOptions() async {
    try {
      final token = await storage.read(key: 'token');
      final adminToken = await storage.read(key: 'adminToken');

      if (token == null || adminToken == null) {
        setState(() => error = "Not authenticated");
        return;
      }

      final res = await http.get(
        Uri.parse('$server/admins/get/admin_file_options/'),
        headers: {'Authorization': token, 'Admin-Token': adminToken},
      );

      final body = jsonDecode(res.body);

      if (res.statusCode == 200) {
        final options = List<String>.from(body['data']);
        setState(() {
          adminOptions = ["Select process", ...options];
          selectedOption = "Select process";
        });
      } else {
        setState(() => error = body['message'] ?? "Failed to load options");
      }
    } catch (e) {
      setState(() => error = "Error fetching options: $e");
    }
  }

  void _pickLargeFile() {
    final uploadInput = html.FileUploadInputElement();
    uploadInput.accept = '.json,.csv,.xlsx.jsonl';
    uploadInput.click();

    uploadInput.onChange.listen((event) {
      final file = uploadInput.files!.first;

      setState(() {
        selectedFile = file;
        fileName = file.name;
        error = '';
        message = '';
      });
    });
  }

  Future<void> _uploadLargeFile() async {
    if (selectedFile == null) {
      setState(() => error = "Please select a file first.");
      return;
    }

    if (selectedOption == null || selectedOption == "Select process") {
      setState(() => error = "Please select a valid process.");
      return;
    }

    final token = await storage.read(key: 'token');
    final adminToken = await storage.read(key: 'adminToken');

    if (token == null || adminToken == null) {
      setState(() => error = "Not authenticated");
      return;
    }

    const chunkSize = 10 * 1024 * 1024;
    int offset = 0;
    final file = selectedFile!;
    final totalSize = file.size;

    while (offset < totalSize) {
      final end = (offset + chunkSize > totalSize)
          ? totalSize
          : offset + chunkSize;
      final blob = file.slice(offset, end);
      final reader = html.FileReader();

      reader.readAsArrayBuffer(blob);
      await reader.onLoad.first;

      final chunkBytes = reader.result as List<int>;

      final uri = Uri.parse('$server/admins/add/admin_file_record/');
      final request = http.MultipartRequest('POST', uri);

      request.headers.addAll({
        'Authorization': token,
        'Admin-Token': adminToken,
      });

      request.fields['process'] = selectedOption!;
      request.fields['file_name'] = file.name;
      request.fields['chunk_start'] = offset.toString();
      request.fields['chunk_end'] = end.toString();
      request.fields['total_size'] = totalSize.toString();

      request.files.add(
        http.MultipartFile.fromBytes('file', chunkBytes, filename: file.name),
      );

      final streamed = await request.send();
      final res = await http.Response.fromStream(streamed);

      if (res.statusCode != 200) {
        setState(() => error = "Chunk upload failed: ${res.body}");
        return;
      }

      offset = end;
    }

    setState(() {
      message = "File uploaded successfully!";
      error = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButton<String>(
          value: selectedOption,
          items: adminOptions
              .map((opt) => DropdownMenuItem(value: opt, child: Text(opt)))
              .toList(),
          onChanged: (value) => setState(() => selectedOption = value),
        ),

        const SizedBox(height: 20),

        ElevatedButton(
          onPressed: _pickLargeFile,
          child: const Text('Select File'),
        ),

        if (fileName != null) Text('Selected: $fileName'),

        const SizedBox(height: 20),

        ElevatedButton(
          onPressed: _uploadLargeFile,
          child: const Text('Upload File'),
        ),

        if (error.isNotEmpty)
          Text(error, style: const TextStyle(color: Colors.red)),

        if (message.isNotEmpty)
          Text(message, style: const TextStyle(color: Colors.green)),
      ],
    );
  }
}
