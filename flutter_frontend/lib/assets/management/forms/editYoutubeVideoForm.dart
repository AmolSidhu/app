import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class EditVideoForm extends StatefulWidget {
  const EditVideoForm({Key? key}) : super(key: key);

  @override
  State<EditVideoForm> createState() => _EditVideoFormState();
}

class _EditVideoFormState extends State<EditVideoForm> {
  final _formKey = GlobalKey<FormState>();
  final storage = const FlutterSecureStorage();

  bool _loading = true;
  bool _submitting = false;
  String? _error;
  String? _successMessage;

  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  String? _videoSerial;

  @override
  void initState() {
    super.initState();
    _fetchVideo();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _fetchVideo() async {
    try {
      final token = await storage.read(key: 'token');
      final serial = await storage.read(key: 'editYoutubeVideoSerial');

      if (token == null || serial == null) {
        throw Exception('Missing token or video serial');
      }

      final response = await http.get(
        Uri.parse('$server/get/youtube_stream_data/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final responseBody = jsonDecode(response.body);
        final data = responseBody['data'];

        setState(() {
          _videoSerial = data['serial'];
          _titleController.text = data['title'] ?? '';
          _descriptionController.text = data['description'] ?? '';
          _loading = false;
        });
      } else {
        throw Exception('Failed to load video data');
      }
    } catch (e) {
      setState(() {
        _error = 'Error fetching video data: $e';
        _loading = false;
      });
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _submitting = true;
      _error = null;
      _successMessage = null;
    });

    try {
      final token = await storage.read(key: 'token');
      if (token == null || _videoSerial == null) {
        throw Exception('Missing token or video serial');
      }

      final response = await http.patch(
        Uri.parse('$server/update/youtube_video_details/$_videoSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'title': _titleController.text.trim(),
          'description': _descriptionController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          _successMessage = 'Video details updated successfully.';
        });
      } else {
        throw Exception(jsonDecode(response.body)['message']);
      }
    } catch (e) {
      setState(() {
        _error = 'Update failed: $e';
      });
    } finally {
      setState(() {
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Edit YouTube Video',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 24),

            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),

            if (_successMessage != null)
              Text(
                _successMessage!,
                style: const TextStyle(color: Colors.green),
              ),

            const SizedBox(height: 16),

            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Title'),
              validator: (value) =>
                  value == null || value.isEmpty ? 'Title is required' : null,
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 5,
            ),
            const SizedBox(height: 24),

            ElevatedButton(
              onPressed: _submitting ? null : _submitForm,
              child: _submitting
                  ? const CircularProgressIndicator()
                  : const Text('Save Changes'),
            ),
          ],
        ),
      ),
    );
  }
}
