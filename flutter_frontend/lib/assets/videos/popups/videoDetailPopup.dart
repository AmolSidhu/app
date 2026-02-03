import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/videos/videoStreamPage.dart';

class VideoDetailPopup extends StatefulWidget {
  final String serial;

  const VideoDetailPopup({Key? key, required this.serial}) : super(key: key);

  @override
  State<VideoDetailPopup> createState() => _VideoDetailPopupState();
}

class _VideoDetailPopupState extends State<VideoDetailPopup> {
  final _storage = const FlutterSecureStorage();
  OverlayEntry? _submenuOverlay;

  Map<String, dynamic>? _video;
  List<Map<String, dynamic>> _episodes = [];
  String? _selectedSeason;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchVideo();
  }

  @override
  void dispose() {
    _removeSubmenu();
    super.dispose();
  }

  /* ===================== API ===================== */

  Future<void> _fetchVideo() async {
    final token = await _storage.read(key: 'token');
    final res = await http.get(
      Uri.parse('$server/get/video_data/${widget.serial}'),
      headers: {'Authorization': token!, 'Content-Type': 'application/json'},
    );

    final data = jsonDecode(res.body);
    setState(() {
      _video = data;
      _loading = false;

      if (data['series'] == true && data['season_metadata'] != null) {
        _selectedSeason = (data['season_metadata'] as Map).keys.first;
        _fetchEpisodes(_selectedSeason!);
      }
    });
  }

  Future<void> _fetchEpisodes(String season) async {
    final token = await _storage.read(key: 'token');
    final res = await http.get(
      Uri.parse('$server/get/episode_data/${widget.serial}/$season'),
      headers: {'Authorization': token!, 'Content-Type': 'application/json'},
    );

    final data = jsonDecode(res.body);
    setState(() {
      _episodes = List<Map<String, dynamic>>.from(data['episodes']);
    });
  }

  Future<void> _toggleFavourite() async {
    final token = await _storage.read(key: 'token');
    final action = _video!['favourites'] ? 'remove' : 'add';

    await http.post(
      Uri.parse('$server/update/favourite_videos/${widget.serial}/'),
      headers: {'Authorization': token!, 'Content-Type': 'application/json'},
      body: jsonEncode({'action': action}),
    );

    setState(() {
      _video!['favourites'] = !_video!['favourites'];
    });
  }

  Future<void> _addToAlbum(String listSerial) async {
    final token = await _storage.read(key: 'token');
    await http.post(
      Uri.parse('$server/add/video/custom_list/${widget.serial}/$listSerial/'),
      headers: {'Authorization': token!, 'Content-Type': 'application/json'},
    );
  }

  Future<void> _removeFromAlbum(String listSerial) async {
    final token = await _storage.read(key: 'token');
    await http.delete(
      Uri.parse(
        '$server/delete/video/custom_list/${widget.serial}/$listSerial/',
      ),
      headers: {'Authorization': token!, 'Content-Type': 'application/json'},
    );
  }

  /* ===================== SUBMENU ===================== */

  Offset _getWidgetPosition(BuildContext context) {
    final RenderBox box = context.findRenderObject() as RenderBox;
    return box.localToGlobal(Offset.zero);
  }

  void _showSubmenu({
    required Offset position,
    required List albums,
    required bool add,
  }) {
    _removeSubmenu();

    _submenuOverlay = OverlayEntry(
      builder: (_) => Positioned(
        left: position.dx + 180,
        top: position.dy,
        child: MouseRegion(
          onExit: (_) => _removeSubmenu(),
          child: Material(
            elevation: 4,
            child: SizedBox(
              width: 240,
              child: ListView(
                padding: EdgeInsets.zero,
                shrinkWrap: true,
                children: albums.map<Widget>((album) {
                  return ListTile(
                    title: Text(album['list_name']),
                    onTap: () {
                      add
                          ? _addToAlbum(album['list_serial'])
                          : _removeFromAlbum(album['list_serial']);
                      _removeSubmenu();
                    },
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ),
    );

    Overlay.of(context).insert(_submenuOverlay!);
  }

  void _removeSubmenu() {
    _submenuOverlay?.remove();
    _submenuOverlay = null;
  }

  /* ===================== PLAY ===================== */

  Future<void> _play(String serial, bool resume) async {
    await _storage.write(key: 'videoSerial', value: serial);
    await _storage.write(key: 'videoResume', value: resume.toString());
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => VideoStreamPage()),
    );
  }

  /* ===================== UI ===================== */

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return Material(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            /* HEADER */
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _video!['video_name'],
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    PopupMenuButton(
                      onCanceled: _removeSubmenu,
                      itemBuilder: (context) => [
                        PopupMenuItem(
                          child: ListTile(
                            title: Text(
                              _video!['favourites']
                                  ? 'Remove from Favourites'
                                  : 'Add to Favourites',
                            ),
                            onTap: () {
                              Navigator.pop(context);
                              _toggleFavourite();
                            },
                          ),
                        ),
                        PopupMenuItem(
                          child: Builder(
                            builder: (ctx) => MouseRegion(
                              onEnter: (_) {
                                final pos = _getWidgetPosition(ctx);
                                _showSubmenu(
                                  position: pos,
                                  albums: _video!['not_in_custom_album'],
                                  add: true,
                                );
                              },
                              child: const ListTile(
                                title: Text('Add to Custom Album'),
                              ),
                            ),
                          ),
                        ),
                        PopupMenuItem(
                          child: Builder(
                            builder: (ctx) => MouseRegion(
                              onEnter: (_) {
                                final pos = _getWidgetPosition(ctx);
                                _showSubmenu(
                                  position: pos,
                                  albums: _video!['in_custom_album'],
                                  add: false,
                                );
                              },
                              child: const ListTile(
                                title: Text('Remove from Custom Album'),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 10),
            Text('Description: ${_video!['video_description']}'),
            Text('Rating: ${_video!['video_rating']}'),

            const SizedBox(height: 20),

            if (_video!['series'] == true)
              DropdownButton<String>(
                value: _selectedSeason,
                items: (_video!['season_metadata'] as Map).keys
                    .map<DropdownMenuItem<String>>(
                      (s) =>
                          DropdownMenuItem(value: s, child: Text('Season $s')),
                    )
                    .toList(),
                onChanged: (val) {
                  setState(() {
                    _selectedSeason = val;
                    _episodes.clear();
                  });
                  _fetchEpisodes(val!);
                },
              ),

            Expanded(
              child: ListView(
                children: _episodes.map((e) {
                  return ListTile(
                    title: Text('Episode ${e['episode']}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        TextButton(
                          onPressed: () => _play(e['video_serial'], false),
                          child: const Text('Play'),
                        ),
                        if (e['resume'] == true)
                          TextButton(
                            onPressed: () => _play(e['video_serial'], true),
                            child: const Text('Resume'),
                          ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),

            ElevatedButton(
              onPressed: () => _play(_video!['serial'], false),
              child: const Text('Watch Video'),
            ),
            if (_video!['resume'] == true)
              ElevatedButton(
                onPressed: () => _play(_video!['serial'], true),
                child: const Text('Resume'),
              ),
          ],
        ),
      ),
    );
  }
}
