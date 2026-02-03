import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class VideoItem {
  final Uint8List bytes;
  final String name;

  final TextEditingController episode = TextEditingController();
  final TextEditingController season = TextEditingController();

  VideoItem({required this.bytes, required this.name});
}

class BatchVideoUploadForm extends StatefulWidget {
  const BatchVideoUploadForm({Key? key}) : super(key: key);

  @override
  State<BatchVideoUploadForm> createState() => _BatchVideoUploadFormState();
}

class _BatchVideoUploadFormState extends State<BatchVideoUploadForm> {
  final storage = const FlutterSecureStorage();

  List<VideoItem> videos = [];
  Uint8List? thumbnailBytes;
  String? thumbnailName;

  bool isPrivate = false;
  int permission = 2;
  bool existingSeries = false;
  bool loadingSeries = false;
  String masterSerial = '';

  List<dynamic> seriesOptions = [];

  String error = '';
  String message = '';

  final titleController = TextEditingController();
  final imdbController = TextEditingController();
  final descriptionController = TextEditingController();
  final criticRatingController = TextEditingController();
  final customTagController = TextEditingController();

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
    for (var t in tags) {
      selectedTags[t] = false;
    }
  }

  Future<void> pickVideos() async {
    final result = await FilePicker.platform.pickFiles(
      allowMultiple: true,
      withData: true,
      type: FileType.video,
    );

    if (result != null) {
      setState(() {
        videos = result.files
            .where((f) => f.bytes != null)
            .map((f) => VideoItem(bytes: f.bytes!, name: f.name))
            .toList();
      });
    }
  }

  Future<void> pickThumbnail() async {
    final result = await FilePicker.platform.pickFiles(
      withData: true,
      type: FileType.image,
    );

    if (result != null && result.files.single.bytes != null) {
      setState(() {
        thumbnailBytes = result.files.single.bytes;
        thumbnailName = result.files.single.name;
      });
    }
  }

  void addCustomTag() {
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

  Future<void> fetchSeries() async {
    setState(() => loadingSeries = true);
    try {
      final token = await storage.read(key: 'token');
      final res = await http.get(
        Uri.parse('$server/get/existing_series_serials/'),
        headers: {'Authorization': token ?? ''},
      );
      final data = jsonDecode(res.body);
      setState(() => seriesOptions = data['data'] ?? []);
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      setState(() => loadingSeries = false);
    }
  }

  Future<void> submit() async {
    try {
      final token = await storage.read(key: 'token');

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$server/upload/batch_video/'),
      );
      request.headers['Authorization'] = token ?? '';

      for (int i = 0; i < videos.length; i++) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'videos',
            videos[i].bytes,
            filename: videos[i].name,
          ),
        );
        request.fields['episode_$i'] = videos[i].episode.text;
        request.fields['season_$i'] = videos[i].season.text;
      }

      if (thumbnailBytes != null) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'thumbnail',
            thumbnailBytes!,
            filename: thumbnailName,
          ),
        );
      }

      request.fields.addAll({
        'title': titleController.text,
        'description': descriptionController.text,
        'imdbLink': imdbController.text,
        'criticRating': criticRatingController.text,
        'private': isPrivate.toString(),
        'permission': permission.toString(),
        'existing_series': existingSeries.toString(),
        'master_serial': existingSeries ? masterSerial : '',
        'tags': jsonEncode(
          selectedTags.entries.where((e) => e.value).map((e) => e.key).toList(),
        ),
        'directors': jsonEncode(directors.map((e) => e.text).toList()),
        'stars': jsonEncode(stars.map((e) => e.text).toList()),
        'writers': jsonEncode(writers.map((e) => e.text).toList()),
        'creators': jsonEncode(creators.map((e) => e.text).toList()),
      });

      final res = await request.send();
      final body = await res.stream.bytesToString();

      if (res.statusCode != 201) {
        throw Exception(body);
      }

      setState(() => message = jsonDecode(body)['message']);
    } catch (e) {
      setState(() => error = e.toString());
    }
  }

  Widget peopleSection(String title, List<TextEditingController> list) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        ...list.asMap().entries.map(
          (e) => Row(
            children: [
              Expanded(child: TextField(controller: e.value)),
              IconButton(
                icon: const Icon(Icons.remove_circle, color: Colors.red),
                onPressed: () => setState(() => list.removeAt(e.key)),
              ),
            ],
          ),
        ),
        TextButton(
          onPressed: () => setState(() => list.add(TextEditingController())),
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
            onPressed: pickVideos,
            child: const Text('Select Videos'),
          ),

          ...videos.map(
            (v) => Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      v.name,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    TextField(
                      controller: v.episode,
                      decoration: const InputDecoration(labelText: 'Episode'),
                    ),
                    TextField(
                      controller: v.season,
                      decoration: const InputDecoration(labelText: 'Season'),
                    ),
                  ],
                ),
              ),
            ),
          ),

          ElevatedButton(
            onPressed: pickThumbnail,
            child: const Text('Select Thumbnail'),
          ),

          const SizedBox(height: 12),
          const Text('Tags', style: TextStyle(fontWeight: FontWeight.bold)),

          Wrap(
            spacing: 8,
            children: tags.map((t) {
              return FilterChip(
                label: Text(t),
                selected: selectedTags[t] ?? false,
                onSelected: (v) => setState(() => selectedTags[t] = v),
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
                  onSubmitted: (_) => addCustomTag(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: addCustomTag,
                child: const Text('Add Tag'),
              ),
            ],
          ),

          TextField(
            controller: titleController,
            decoration: const InputDecoration(labelText: 'Title'),
          ),
          TextField(
            controller: imdbController,
            decoration: const InputDecoration(labelText: 'IMDB Link'),
          ),
          TextField(
            controller: descriptionController,
            decoration: const InputDecoration(labelText: 'Description'),
          ),
          TextField(
            controller: criticRatingController,
            decoration: const InputDecoration(labelText: 'Critic Rating'),
          ),

          SwitchListTile(
            title: const Text('Existing Series'),
            value: existingSeries,
            onChanged: (v) {
              setState(() => existingSeries = v);
              if (v) fetchSeries();
            },
          ),

          if (existingSeries)
            loadingSeries
                ? const CircularProgressIndicator()
                : DropdownButton<String>(
                    value: masterSerial.isEmpty ? null : masterSerial,
                    hint: const Text('Select Series'),
                    items: seriesOptions.map<DropdownMenuItem<String>>((s) {
                      final serial = s['serial'] as String;
                      return DropdownMenuItem<String>(
                        value: serial,
                        child: Text('${s['title']} ($serial)'),
                      );
                    }).toList(),
                    onChanged: (v) => setState(() => masterSerial = v ?? ''),
                  ),

          peopleSection('Directors', directors),
          peopleSection('Stars', stars),
          peopleSection('Writers', writers),
          peopleSection('Creators', creators),

          const SizedBox(height: 20),
          ElevatedButton(onPressed: submit, child: const Text('Upload')),
        ],
      ),
    );
  }
}
