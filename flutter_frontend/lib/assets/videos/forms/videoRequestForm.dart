import 'dart:convert';
import 'dart:html' as html;

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class VideoRequestForm extends StatefulWidget {
  const VideoRequestForm({Key? key}) : super(key: key);

  @override
  State<VideoRequestForm> createState() => _VideoRequestFormState();
}

class _VideoRequestFormState extends State<VideoRequestForm> {
  final _storage = const FlutterSecureStorage();
  final _formKey = GlobalKey<FormState>();

  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  String? _error;
  String? _successMessage;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _checkAuth();
    html.document.title = 'Create Video Request';
  }

  Future<void> _checkAuth() async {
    final token = await _storage.read(key: 'token');
    if (token == null) {
      html.window.location.href = '/login/';
    }
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _loading = true;
      _error = null;
      _successMessage = null;
    });

    final token = await _storage.read(key: 'token');

    try {
      final response = await http.post(
        Uri.parse('$server/create/video_request/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'request_title': _titleController.text,
          'request_description': _descriptionController.text,
        }),
      );

      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw Exception('HTTP error! Status: ${response.statusCode}');
      }

      final data = jsonDecode(response.body);
      setState(() {
        _successMessage = data['message'];
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: 500,
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Create Video Request',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),

              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'Video Title'),
                validator: (value) =>
                    value == null || value.isEmpty ? 'Required' : null,
              ),

              const SizedBox(height: 16),

              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Video Description',
                ),
                maxLines: 4,
                validator: (value) =>
                    value == null || value.isEmpty ? 'Required' : null,
              ),

              const SizedBox(height: 16),

              if (_error != null)
                Text(_error!, style: const TextStyle(color: Colors.red)),

              if (_successMessage != null)
                Text(
                  _successMessage!,
                  style: const TextStyle(color: Colors.green),
                ),

              const SizedBox(height: 16),

              ElevatedButton(
                onPressed: _loading ? null : _handleSubmit,
                child: _loading
                    ? const CircularProgressIndicator()
                    : const Text('Submit Request'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
}
