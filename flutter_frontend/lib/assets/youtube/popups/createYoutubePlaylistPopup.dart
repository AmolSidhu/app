import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CreateYoutubePlaylistPopup extends StatefulWidget {
  final VoidCallback onClose;

  const CreateYoutubePlaylistPopup({Key? key, required this.onClose})
    : super(key: key);

  @override
  State<CreateYoutubePlaylistPopup> createState() =>
      _CreateYoutubePlaylistPopupState();
}

class _CreateYoutubePlaylistPopupState
    extends State<CreateYoutubePlaylistPopup> {
  final _storage = const FlutterSecureStorage();

  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  String? errorMessage;
  String? successMessage;
  bool loading = false;

  Future<void> handleSubmit() async {
    final title = _titleController.text.trim();
    final description = _descriptionController.text.trim();

    if (title.isEmpty || description.isEmpty) {
      setState(() {
        errorMessage = "Please fill in all fields.";
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
      if (token == null) throw Exception("Not authenticated");

      final res = await http.post(
        Uri.parse('$server/create/youtube_playlist/'),
        headers: {"Authorization": token, "Content-Type": "application/json"},
        body: jsonEncode({"title": title, "description": description}),
      );

      if (res.statusCode == 200) {
        setState(() {
          successMessage = "Playlist created successfully!";
          errorMessage = null;
        });

        _titleController.clear();
        _descriptionController.clear();
      } else {
        final data = jsonDecode(res.body);
        setState(() {
          errorMessage =
              data["message"] ?? "An error occurred during playlist creation.";
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = "An error occurred during playlist creation.";
      });
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("Create YouTube Playlist"),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(labelText: "Playlist Title"),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _descriptionController,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: "Playlist Description",
            ),
          ),
          if (errorMessage != null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ),
          if (successMessage != null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                successMessage!,
                style: const TextStyle(color: Colors.green),
              ),
            ),
        ],
      ),
      actions: [
        TextButton(onPressed: widget.onClose, child: const Text("Cancel")),
        ElevatedButton(
          onPressed: loading ? null : handleSubmit,
          child: loading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text("Create Playlist"),
        ),
      ],
    );
  }
}
