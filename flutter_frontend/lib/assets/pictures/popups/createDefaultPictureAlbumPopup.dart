import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateDefaultPictureAlbumPopup extends StatefulWidget {
  const CreateDefaultPictureAlbumPopup({Key? key}) : super(key: key);

  @override
  State<CreateDefaultPictureAlbumPopup> createState() =>
      _CreateDefaultPictureAlbumPopupState();
}

class _CreateDefaultPictureAlbumPopupState
    extends State<CreateDefaultPictureAlbumPopup> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _tagController = TextEditingController();

  final List<String> _tags = [];

  bool _isCreating = false;
  String? _message;

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

  Future<void> _createAlbum() async {
    setState(() {
      _isCreating = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.post(
        Uri.parse('$server/create/album/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'album_name': _nameController.text.trim(),
          'album_description': _descriptionController.text.trim(),
          'tags': _tags,
        }),
      );

      if (response.statusCode == 201) {
        Navigator.of(context).pop(true);
      } else {
        final data = jsonDecode(response.body);
        setState(() {
          _message = data['message'] ?? 'Failed to create album';
          _isCreating = false;
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Internal server error';
        _isCreating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Album'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Album Name'),
            ),
            const SizedBox(height: 12),

            TextField(
              controller: _descriptionController,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Album Description'),
            ),
            const SizedBox(height: 12),

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

            if (_message != null) ...[
              const SizedBox(height: 12),
              Text(_message!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isCreating ? null : () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isCreating ? null : _createAlbum,
          child: _isCreating
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create Album'),
        ),
      ],
    );
  }
}
