import 'dart:typed_data';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class SingleVideoUploadForm extends StatefulWidget {
  const SingleVideoUploadForm({Key? key}) : super(key: key);

  @override
  State<SingleVideoUploadForm> createState() => _SingleVideoUploadFormState();
}

class _SingleVideoUploadFormState extends State<SingleVideoUploadForm> {
  final storage = const FlutterSecureStorage();

  Uint8List? videoBytes;
  Uint8List? thumbnailBytes;
  String? videoName;
  String? thumbnailName;

  String error = '';
  String message = '';

  final titleController = TextEditingController();
  final imdbController = TextEditingController();
  final descriptionController = TextEditingController();
  final criticRatingController = TextEditingController();
  final customTagController = TextEditingController();

  bool isPrivate = false;
  int permission = 2;

  List<String> tags = [
    'action',
    'comedy',
    'drama',
    'horror',
    'thriller',
    'adventure',
  ];

  Map<String, bool> selectedTags = {};

  List<TextEditingController> directors = [];
  List<TextEditingController> stars = [];
  List<TextEditingController> writers = [];
  List<TextEditingController> creators = [];

  @override
  void initState() {
    super.initState();
    for (var tag in tags) {
      selectedTags[tag] = false;
    }
  }

  Future<void> _pickFile(bool isVideo) async {
    final result = await FilePicker.platform.pickFiles(
      type: isVideo ? FileType.video : FileType.image,
      withData: true,
    );

    if (result != null && result.files.single.bytes != null) {
      setState(() {
        if (isVideo) {
          videoBytes = result.files.single.bytes;
          videoName = result.files.single.name;
        } else {
          thumbnailBytes = result.files.single.bytes;
          thumbnailName = result.files.single.name;
        }
      });
    }
  }

  void _addCustomTag() {
    final tag = customTagController.text.trim().toLowerCase();

    if (tag.isEmpty) return;

    if (!tags.contains(tag)) {
      setState(() {
        tags.add(tag);
        selectedTags[tag] = true;
      });
    }

    customTagController.clear();
  }

  Future<void> _uploadVideo() async {
    try {
      final token = await storage.read(key: 'token');
      if (videoBytes == null) {
        setState(() => error = 'No video selected');
        return;
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$server/upload/video/'),
      );

      request.headers['Authorization'] = token ?? '';

      request.files.add(
        http.MultipartFile.fromBytes('video', videoBytes!, filename: videoName),
      );

      if (thumbnailBytes != null) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'thumbnail',
            thumbnailBytes!,
            filename: thumbnailName,
          ),
        );
      }

      request.fields['title'] = titleController.text;
      request.fields['description'] = descriptionController.text;
      request.fields['imdbLink'] = imdbController.text;
      request.fields['criticRating'] = criticRatingController.text;
      request.fields['private'] = isPrivate.toString();
      request.fields['permission'] = permission.toString();

      request.fields['tags'] = jsonEncode(
        selectedTags.entries.where((e) => e.value).map((e) => e.key).toList(),
      );

      request.fields['directors'] = jsonEncode(
        directors.map((e) => e.text).toList(),
      );
      request.fields['stars'] = jsonEncode(stars.map((e) => e.text).toList());
      request.fields['writers'] = jsonEncode(
        writers.map((e) => e.text).toList(),
      );
      request.fields['creators'] = jsonEncode(
        creators.map((e) => e.text).toList(),
      );

      final response = await request.send();
      final body = await response.stream.bytesToString();

      if (response.statusCode != 200) {
        throw Exception(body);
      }

      setState(() {
        error = '';
        message = jsonDecode(body)['message'] ?? 'Upload successful';
      });
    } catch (e) {
      setState(() {
        error = e.toString();
      });
    }
  }

  Widget _peopleSection(String label, List<TextEditingController> list) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
        ...list.asMap().entries.map(
          (entry) => Row(
            children: [
              Expanded(child: TextField(controller: entry.value)),
              IconButton(
                icon: const Icon(Icons.remove_circle, color: Colors.red),
                onPressed: () {
                  setState(() => list.removeAt(entry.key));
                },
              ),
            ],
          ),
        ),
        TextButton(
          onPressed: () {
            setState(() => list.add(TextEditingController()));
          },
          child: const Text('Add'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (error.isNotEmpty)
            Text(error, style: const TextStyle(color: Colors.red)),
          if (message.isNotEmpty)
            Text(message, style: const TextStyle(color: Colors.green)),

          ElevatedButton(
            onPressed: () => _pickFile(true),
            child: const Text('Select Video'),
          ),
          ElevatedButton(
            onPressed: () => _pickFile(false),
            child: const Text('Select Thumbnail'),
          ),

          TextField(
            controller: imdbController,
            decoration: const InputDecoration(labelText: 'IMDB Link'),
          ),
          TextField(
            controller: titleController,
            decoration: const InputDecoration(labelText: 'Title'),
          ),
          TextField(
            controller: descriptionController,
            decoration: const InputDecoration(labelText: 'Description'),
          ),
          TextField(
            controller: criticRatingController,
            decoration: const InputDecoration(labelText: 'Critic Rating'),
          ),

          const SizedBox(height: 12),

          const Text('Tags', style: TextStyle(fontWeight: FontWeight.bold)),
          Wrap(
            spacing: 8,
            children: tags.map((tag) {
              return FilterChip(
                label: Text(tag),
                selected: selectedTags[tag] ?? false,
                onSelected: (val) {
                  setState(() => selectedTags[tag] = val);
                },
              );
            }).toList(),
          ),

          const SizedBox(height: 8),

          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: customTagController,
                  decoration: const InputDecoration(
                    labelText: 'Add custom tag',
                  ),
                  onSubmitted: (_) => _addCustomTag(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _addCustomTag,
                child: const Text('Add Tag'),
              ),
            ],
          ),

          const SizedBox(height: 16),

          _peopleSection('Directors', directors),
          _peopleSection('Stars', stars),
          _peopleSection('Writers', writers),
          _peopleSection('Creators', creators),

          SwitchListTile(
            title: const Text('Private'),
            value: isPrivate,
            onChanged: (v) => setState(() => isPrivate = v),
          ),

          DropdownButton<int>(
            value: permission,
            onChanged: (v) => setState(() => permission = v!),
            items: [1, 2, 3, 4]
                .map((e) => DropdownMenuItem(value: e, child: Text('$e')))
                .toList(),
          ),

          const SizedBox(height: 20),
          ElevatedButton(onPressed: _uploadVideo, child: const Text('Upload')),
        ],
      ),
    );
  }
}
