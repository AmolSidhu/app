import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'package:flutter_frontend/static/constants.dart';

class AddFullTrackPopup extends StatefulWidget {
  final String trackId;
  final String trackTitle;

  const AddFullTrackPopup({
    super.key,
    required this.trackId,
    required this.trackTitle,
  });

  @override
  State<AddFullTrackPopup> createState() => _AddFullTrackPopupState();
}

class _AddFullTrackPopupState extends State<AddFullTrackPopup> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool isUploading = false;
  bool useYoutubeLink = false;

  html.File? selectedFile;
  final TextEditingController youtubeController = TextEditingController();

  String statusMessage = '';

  void pickMp3File() {
    final input = html.FileUploadInputElement()
      ..accept = '.mp3'
      ..click();

    input.onChange.listen((event) {
      final files = input.files;
      if (files != null && files.isNotEmpty) {
        setState(() {
          selectedFile = files.first;
          statusMessage = 'Selected file: ${selectedFile!.name}';
        });
      }
    });
  }

  Future<void> submitFullTrack() async {
    setState(() {
      isUploading = true;
      statusMessage = 'Uploading...';
    });

    try {
      final token = await secureStorage.read(key: 'token');
      if (token == null) {
        throw Exception('Authentication token missing');
      }

      final uri = Uri.parse('$server/add/full_track/${widget.trackId}/');

      final request = http.MultipartRequest('POST', uri);
      request.headers['Authorization'] = token;

      if (useYoutubeLink) {
        if (youtubeController.text.trim().isEmpty) {
          throw Exception('YouTube link is required');
        }
        request.fields['youtube_link'] = youtubeController.text.trim();
      } else {
        if (selectedFile == null) {
          throw Exception('Please select an MP3 file');
        }

        final reader = html.FileReader();
        reader.readAsArrayBuffer(selectedFile!);
        await reader.onLoad.first;

        final bytes = reader.result as List<int>;

        request.files.add(
          http.MultipartFile.fromBytes(
            'track_file',
            bytes,
            filename: selectedFile!.name,
          ),
        );
      }

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 201) {
        setState(() {
          statusMessage = '✅ Full track added successfully';
        });
      } else {
        throw Exception(responseBody);
      }
    } catch (e) {
      setState(() {
        statusMessage = '❌ Error: $e';
      });
    } finally {
      setState(() {
        isUploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Add Full Track'),
      content: SizedBox(
        width: 420,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.trackTitle,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Use YouTube link instead of file'),
              value: useYoutubeLink,
              onChanged: isUploading
                  ? null
                  : (value) {
                      setState(() {
                        useYoutubeLink = value;
                        selectedFile = null;
                        youtubeController.clear();
                        statusMessage = '';
                      });
                    },
            ),

            const SizedBox(height: 8),

            if (useYoutubeLink)
              TextField(
                controller: youtubeController,
                decoration: const InputDecoration(
                  labelText: 'YouTube URL',
                  border: OutlineInputBorder(),
                ),
              )
            else
              ElevatedButton.icon(
                onPressed: isUploading ? null : pickMp3File,
                icon: const Icon(Icons.upload_file),
                label: const Text('Select MP3 File'),
              ),

            const SizedBox(height: 12),

            if (statusMessage.isNotEmpty)
              Text(
                statusMessage,
                style: TextStyle(
                  color: statusMessage.startsWith('✅')
                      ? Colors.green
                      : statusMessage.startsWith('❌')
                      ? Colors.red
                      : Colors.black,
                ),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: isUploading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: isUploading ? null : submitFullTrack,
          child: isUploading
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Submit'),
        ),
      ],
    );
  }
}
