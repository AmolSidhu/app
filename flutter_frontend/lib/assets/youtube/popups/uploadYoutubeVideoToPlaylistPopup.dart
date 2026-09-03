import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class UploadYoutubeVideoToPlaylistPopup extends StatefulWidget {
  final String playlistSerial;

  const UploadYoutubeVideoToPlaylistPopup({
    Key? key,
    required this.playlistSerial,
  }) : super(key: key);

  @override
  State<UploadYoutubeVideoToPlaylistPopup> createState() =>
      _UploadYoutubeVideoToPlaylistPopupState();
}

class _UploadYoutubeVideoToPlaylistPopupState
    extends State<UploadYoutubeVideoToPlaylistPopup> {
  final _storage = const FlutterSecureStorage();
  final TextEditingController _videoUrlController = TextEditingController();

  String? errorMessage;
  String? successMessage;
  bool loading = false;

  Future<void> handleSubmit() async {
    final videoUrl = _videoUrlController.text.trim();

    if (videoUrl.isEmpty) {
      setState(() {
        errorMessage = 'YouTube URL is required.';
        successMessage = null;
      });
      return;
    }

    setState(() {
      loading = true;
      errorMessage = null;
      successMessage = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      if (token == null) throw Exception('Not authenticated');

      final res = await http.post(
        Uri.parse('$server/upload/youtube_video/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'youtube_link': videoUrl,
          'add_to_playlists': [widget.playlistSerial],
        }),
      );

      final body = jsonDecode(res.body);

      if (res.statusCode != 200) {
        setState(() {
          errorMessage = body['message'] ?? 'Upload failed.';
        });
        return;
      }

      Navigator.of(context, rootNavigator: true).pop();
    } catch (e) {
      setState(() {
        errorMessage = 'An unexpected error occurred.';
      });
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Add YouTube Video to Playlist',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 16),

            if (errorMessage != null)
              Text(errorMessage!, style: const TextStyle(color: Colors.red)),

            const SizedBox(height: 12),

            TextField(
              controller: _videoUrlController,
              decoration: const InputDecoration(
                hintText: 'YouTube video URL',
                border: OutlineInputBorder(),
              ),
              enabled: !loading,
            ),

            const SizedBox(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: loading
                      ? null
                      : () => Navigator.of(context, rootNavigator: true).pop(),
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: loading ? null : handleSubmit,
                  child: loading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Upload'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
