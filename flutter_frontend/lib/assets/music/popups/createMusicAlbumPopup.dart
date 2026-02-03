import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class CreateMusicAlbumPopup extends StatefulWidget {
  const CreateMusicAlbumPopup({Key? key}) : super(key: key);

  @override
  State<CreateMusicAlbumPopup> createState() => _CreateMusicAlbumPopupState();
}

class _CreateMusicAlbumPopupState extends State<CreateMusicAlbumPopup> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  final TextEditingController _spotifyController = TextEditingController();
  final TextEditingController _appleController = TextEditingController();

  bool _isCreating = false;
  String? _errorMessage;
  String? _successMessage;

  Future<void> _createAlbum() async {
    setState(() {
      _isCreating = true;
      _errorMessage = null;
      _successMessage = null;
    });

    if (_spotifyController.text.isEmpty || _appleController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Please fill in all fields.';
        _isCreating = false;
      });
      return;
    }

    try {
      final token = await _storage.read(key: 'token');

      final response = await http.post(
        Uri.parse('$server/upload/music_links/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'spotify_link': _spotifyController.text.trim(),
          'apple_link': _appleController.text.trim(),
        }),
      );

      if (response.statusCode >= 200 && response.statusCode < 300) {
        setState(() {
          _successMessage =
              'Album created successfully! Album is being processed.';
          _spotifyController.clear();
          _appleController.clear();
          _isCreating = false;
        });
      } else {
        final data = jsonDecode(response.body);
        setState(() {
          _errorMessage =
              data['message'] ?? 'An error occurred during album creation.';
          _isCreating = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'An error occurred during album creation.';
        _isCreating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Music Album'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                _errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ),
          if (_successMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                _successMessage!,
                style: const TextStyle(color: Colors.green),
              ),
            ),
          TextField(
            controller: _spotifyController,
            decoration: const InputDecoration(labelText: 'Album Spotify Link'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _appleController,
            decoration: const InputDecoration(
              labelText: 'Album Apple Music Link',
            ),
            maxLines: 2,
          ),
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
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create Album'),
        ),
      ],
    );
  }
}
