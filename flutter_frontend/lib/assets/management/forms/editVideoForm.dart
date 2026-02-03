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
  final storage = const FlutterSecureStorage();

  bool _loading = true;
  String? _error;
  String? _success;

  String? _serial;
  String? _token;

  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  late Map<String, List<TextEditingController>> _listFields;

  List<String> _seasons = [];
  String? _selectedSeason;
  List<Map<String, dynamic>> _episodes = [];

  @override
  void initState() {
    super.initState();
    _init();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    for (final list in _listFields.values) {
      for (final c in list) {
        c.dispose();
      }
    }
    super.dispose();
  }

  Future<void> _init() async {
    _token = await storage.read(key: 'token');
    _serial = await storage.read(key: 'editVideoSerial');

    if (_token == null || _serial == null) {
      setState(() {
        _error = 'Missing auth token or video serial';
        _loading = false;
      });
      return;
    }

    await _fetchVideo();
  }

  Future<void> _fetchVideo() async {
    try {
      final res = await http.get(
        Uri.parse('$server/get/single_video_record/$_serial'),
        headers: {'Authorization': _token!},
      );

      if (res.statusCode != 200) {
        throw Exception('Failed to fetch video');
      }

      final data = jsonDecode(res.body)['data'];

      setState(() {
        _titleController.text = data['title'] ?? '';
        _descriptionController.text = data['description'] ?? '';
        _listFields = _buildListFields(data);

        if (data['series'] == true && data['season_metadata'] != null) {
          final meta = jsonDecode(data['season_metadata']);
          _seasons = meta.keys.cast<String>().toList();
        }

        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Map<String, List<TextEditingController>> _buildListFields(Map data) {
    List<TextEditingController> split(String? value) {
      if (value == null || value.isEmpty) return [];
      return value
          .split(', ')
          .map((e) => TextEditingController(text: e))
          .toList();
    }

    return {
      'tags': split(data['tags']),
      'directors': split(data['directors']),
      'stars': split(data['stars']),
      'writers': split(data['writers']),
      'creators': split(data['creators']),
    };
  }

  Future<void> _fetchEpisodes(String season) async {
    try {
      final res = await http.get(
        Uri.parse('$server/get/episode_records/$_serial/$season/'),
        headers: {'Authorization': _token!},
      );

      if (res.statusCode != 200) {
        throw Exception('Failed to fetch episodes');
      }

      setState(() {
        _episodes = List<Map<String, dynamic>>.from(
          jsonDecode(res.body)['data'] ?? [],
        );
      });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _saveVideo() async {
    setState(() {
      _error = null;
      _success = null;
    });

    final body = {
      'title': _titleController.text,
      'description': _descriptionController.text,
      for (final entry in _listFields.entries)
        entry.key: entry.value.map((c) => c.text).join(', '),
    };

    final res = await http.patch(
      Uri.parse('$server/update/video_record/$_serial/'),
      headers: {'Authorization': _token!, 'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    setState(() {
      if (res.statusCode == 200) {
        _success = 'Video updated successfully';
      } else {
        _error = 'Failed to update video';
      }
    });
  }

  Future<void> _saveEpisode(Map<String, dynamic> ep) async {
    final res = await http.patch(
      Uri.parse('$server/update/video_episode/$_serial/'),
      headers: {'Authorization': _token!, 'Content-Type': 'application/json'},
      body: jsonEncode({
        'current_season': ep['season'],
        'current_episode': ep['episode'],
        'video_serial': ep['video_serial'],
        'new_season': ep['new_season'],
        'new_episode': ep['new_episode'],
      }),
    );

    setState(() {
      if (res.statusCode == 200) {
        _success = 'Episode updated successfully';
      } else {
        _error = 'Failed to update episode';
      }
    });
  }

  Widget listEditor(String label, String key) {
    final controllers = _listFields[key]!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),

        ...controllers.asMap().entries.map((entry) {
          return Row(
            children: [
              Expanded(child: TextField(controller: entry.value)),
              IconButton(
                icon: const Icon(Icons.remove_circle_outline),
                onPressed: () {
                  setState(() => controllers.removeAt(entry.key));
                },
              ),
            ],
          );
        }),

        TextButton.icon(
          icon: const Icon(Icons.add),
          label: Text('Add ${label.substring(0, label.length - 1)}'),
          onPressed: () {
            setState(() => controllers.add(TextEditingController()));
          },
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget episodeRow(Map<String, dynamic> ep) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Current: Season ${ep['season']} · Episode ${ep['episode']}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(labelText: 'New Season'),
                    keyboardType: TextInputType.number,
                    onChanged: (v) => ep['new_season'] = int.tryParse(v),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(labelText: 'New Episode'),
                    keyboardType: TextInputType.number,
                    onChanged: (v) => ep['new_episode'] = int.tryParse(v),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.save),
                  onPressed: () => _saveEpisode(ep),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_error != null)
            Text(_error!, style: const TextStyle(color: Colors.red)),
          if (_success != null)
            Text(_success!, style: const TextStyle(color: Colors.green)),

          TextField(
            controller: _titleController,
            decoration: const InputDecoration(labelText: 'Title'),
          ),
          TextField(
            controller: _descriptionController,
            decoration: const InputDecoration(labelText: 'Description'),
          ),

          const SizedBox(height: 24),
          listEditor('Tags', 'tags'),
          listEditor('Directors', 'directors'),
          listEditor('Stars', 'stars'),
          listEditor('Writers', 'writers'),
          listEditor('Creators', 'creators'),

          ElevatedButton(
            onPressed: _saveVideo,
            child: const Text('Save Video'),
          ),

          if (_seasons.isNotEmpty) ...[
            const SizedBox(height: 32),
            DropdownButton<String>(
              value: _selectedSeason,
              hint: const Text('Select Season'),
              items: _seasons
                  .map(
                    (s) => DropdownMenuItem(value: s, child: Text('Season $s')),
                  )
                  .toList(),
              onChanged: (value) {
                setState(() => _selectedSeason = value);
                _fetchEpisodes(value!);
              },
            ),
          ],

          const SizedBox(height: 16),
          for (final ep in _episodes) episodeRow(ep),
        ],
      ),
    );
  }
}
