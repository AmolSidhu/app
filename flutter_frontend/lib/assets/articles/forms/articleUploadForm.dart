import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class ArticleUploadForm extends StatefulWidget {
  const ArticleUploadForm({Key? key}) : super(key: key);

  @override
  State<ArticleUploadForm> createState() => _ArticleUploadFormState();
}

class _ArticleUploadFormState extends State<ArticleUploadForm> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _contentController = TextEditingController();
  final TextEditingController _tagController = TextEditingController();

  final List<String> _tags = [];

  bool _loading = false;
  String? _message;
  String? _error;

  void _addTag(String value) {
    final tag = value.trim();
    if (tag.isNotEmpty && !_tags.contains(tag)) {
      setState(() {
        _tags.add(tag);
        _tagController.clear();
      });
    }
  }

  void _removeTag(String tag) {
    setState(() {
      _tags.remove(tag);
    });
  }

  Future<void> _uploadArticle() async {
    final title = _titleController.text.trim();
    final content = _contentController.text.trim();

    if (title.isEmpty || content.isEmpty) {
      setState(() {
        _error = 'All fields are required.';
        _message = null;
      });
      return;
    }

    setState(() {
      _loading = true;
      _message = null;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.post(
        Uri.parse('$server/create/single_article/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ?? '',
        },
        body: jsonEncode({'title': title, 'content': content, 'tags': _tags}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        setState(() {
          _message = data['message'] ?? 'Article created successfully!';
          _titleController.clear();
          _contentController.clear();
          _tagController.clear();
          _tags.clear();
        });
      } else {
        setState(() {
          _error = data['message'] ?? 'Error creating article.';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Internal error. Please try again.';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Article')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            const SizedBox(height: 10),

            TextField(
              controller: _contentController,
              decoration: const InputDecoration(labelText: 'Content'),
              maxLines: 5,
            ),
            const SizedBox(height: 10),

            TextField(
              controller: _tagController,
              decoration: const InputDecoration(
                labelText: 'Tags',
                hintText: 'Enter a tag and press Enter',
              ),
              onSubmitted: _addTag,
            ),
            const SizedBox(height: 8),

            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: _tags
                  .map(
                    (tag) => Chip(
                      label: Text(tag),
                      onDeleted: () => _removeTag(tag),
                    ),
                  )
                  .toList(),
            ),

            const SizedBox(height: 20),

            if (_message != null)
              Text(_message!, style: const TextStyle(color: Colors.green)),
            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),

            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _uploadArticle,
              child: _loading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Upload'),
            ),
          ],
        ),
      ),
    );
  }
}
