import 'dart:convert';
import 'dart:html' as html;

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/management/editVideoPage.dart';

class MyVideoUploadsRequest extends StatefulWidget {
  const MyVideoUploadsRequest({Key? key}) : super(key: key);

  @override
  State<MyVideoUploadsRequest> createState() => _MyVideoUploadsRequestState();
}

class _MyVideoUploadsRequestState extends State<MyVideoUploadsRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<dynamic> _videoUploads = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    html.document.title = 'My Video Uploads';
    _fetchVideoUploads();
  }

  Future<void> _fetchVideoUploads() async {
    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/editing_video_list/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);

        setState(() {
          _videoUploads = decoded['data'] ?? [];
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load videos (${response.statusCode})';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'An error occurred: $e';
        _loading = false;
      });
    }
  }

  Future<void> _editVideo(dynamic video) async {
    final serial = video['serial'];

    if (serial == null) return;

    await _storage.write(key: 'editVideoSerial', value: serial.toString());

    if (!mounted) return;
    Navigator.push(context, MaterialPageRoute(builder: (_) => EditVideoPage()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Uploads')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(
              child: Text(_error!, style: const TextStyle(color: Colors.red)),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _videoUploads.length,
              itemBuilder: (context, index) {
                final video = _videoUploads[index];

                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    title: Text(video['title'] ?? 'No Title'),
                    subtitle: Text(video['description'] ?? ''),
                    trailing: TextButton(
                      onPressed: () => _editVideo(video),
                      child: const Text('Edit'),
                    ),
                    onTap: () => _editVideo(video),
                  ),
                );
              },
            ),
    );
  }
}
