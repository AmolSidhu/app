import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateCustomMusicPlaylistPopup extends StatefulWidget {
  const CreateCustomMusicPlaylistPopup({Key? key}) : super(key: key);

  @override
  State<CreateCustomMusicPlaylistPopup> createState() =>
      _CreateCustomMusicPlaylistPopupState();
}

class _CreateCustomMusicPlaylistPopupState
    extends State<CreateCustomMusicPlaylistPopup> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  bool _isCreating = false;
  String? _message;

  Future<void> _createAlbum() async {
    setState(() {
      _isCreating = true;
      _message = null;
    });

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.post(
        Uri.parse('$server/create/custom_music_playlist/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'playlist_name': _nameController.text.trim(),
          'playlist_description': _descriptionController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
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
      title: const Text('Create Custom Music Album'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _nameController,
            decoration: const InputDecoration(labelText: 'Album Name'),
          ),
          TextField(
            controller: _descriptionController,
            decoration: const InputDecoration(labelText: 'Album Description'),
          ),
          if (_message != null) ...[
            const SizedBox(height: 10),
            Text(_message!, style: const TextStyle(color: Colors.red)),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isCreating ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isCreating ? null : _createAlbum,
          child: _isCreating
              ? const CircularProgressIndicator()
              : const Text('Create'),
        ),
      ],
    );
  }
}
