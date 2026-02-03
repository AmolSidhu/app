import 'dart:convert';
import 'dart:typed_data';
import 'dart:io' show File;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/music/popups/addFullTrackPopup.dart';

class MusicAlbumPopup extends StatefulWidget {
  final Map<String, dynamic> album;
  final VoidCallback onClose;

  const MusicAlbumPopup({
    super.key,
    required this.album,
    required this.onClose,
  });

  @override
  State<MusicAlbumPopup> createState() => _MusicAlbumPopupState();
}

class _MusicAlbumPopupState extends State<MusicAlbumPopup> {
  final _storage = const FlutterSecureStorage();

  Uint8List? _thumbnailBytes;
  List<Map<String, dynamic>> _tracks = [];
  String? _error;
  bool _loadingTracks = true;

  @override
  void initState() {
    super.initState();
    _fetchThumbnail();
    _fetchTracks();
  }

  Future<String> _getToken() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('Token missing');
    return token;
  }

  Future<void> _fetchThumbnail() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/album_thumbnail/${widget.album['serial']}/'),
        headers: {'Authorization': token},
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        setState(() => _thumbnailBytes = response.bodyBytes);
      } else {
        setState(() => _error = 'Failed to load thumbnail');
      }
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Error loading thumbnail');
    }
  }

  Future<void> _fetchTracks() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/track_data/${widget.album['serial']}/'),
        headers: {'Authorization': token},
      );

      if (!mounted) return;

      final data = jsonDecode(response.body);
      final tracks = List<Map<String, dynamic>>.from(data['data']);

      for (final track in tracks) {
        track['player'] = AudioPlayer();
        await _loadPreview(track, token);
        if (!mounted) return;
      }

      setState(() {
        _tracks = tracks;
        _loadingTracks = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Error fetching tracks';
        _loadingTracks = false;
      });
    }
  }

  Future<void> _loadPreview(Map<String, dynamic> track, String token) async {
    try {
      final previewUrl =
          '$server/get/track_preview/${track['track_serial']}/?token=$token';

      final player = track['player'] as AudioPlayer;

      if (kIsWeb) {
        await player.setAudioSource(
          AudioSource.uri(Uri.parse(previewUrl)),
          preload: true,
        );
      } else {
        final response = await http.get(
          Uri.parse(previewUrl),
          headers: {'Authorization': token},
        );

        if (response.statusCode == 200) {
          final dir = await getTemporaryDirectory();
          final file = File('${dir.path}/preview_${track['track_serial']}.mp3');

          await file.writeAsBytes(response.bodyBytes, flush: true);
          await player.setAudioSource(AudioSource.file(file.path));
        }
      }
    } catch (e) {
      debugPrint('Preview load failed: $e');
    }
  }

  void _playTrack(AudioPlayer current) {
    for (final t in _tracks) {
      final p = t['player'] as AudioPlayer?;
      if (p != null && p != current) {
        p.pause();
      }
    }
    current.play();
  }

  Future<List<Map<String, dynamic>>> _getNotAddedPlaylists(
    String trackSerial,
  ) async {
    final token = await _getToken();
    final response = await http.get(
      Uri.parse(
        '$server/get/not_added_to_custom_music_playlists/$trackSerial/',
      ),
      headers: {'Authorization': token},
    );

    final data = jsonDecode(response.body);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  Future<List<Map<String, dynamic>>> _getAddedPlaylists(
    String trackSerial,
  ) async {
    final token = await _getToken();
    final response = await http.get(
      Uri.parse('$server/get/added_to_custom_music_playlists/$trackSerial/'),
      headers: {'Authorization': token},
    );

    final data = jsonDecode(response.body);
    return List<Map<String, dynamic>>.from(data['data'] ?? []);
  }

  Future<void> _addTrackToPlaylist(
    String playlistSerial,
    String trackSerial,
  ) async {
    final token = await _getToken();
    await http.post(
      Uri.parse(
        '$server/add/track_to_custom_music_playlist/$playlistSerial/$trackSerial/',
      ),
      headers: {'Authorization': token},
    );
  }

  Future<void> _removeTrackFromPlaylist(
    String playlistSerial,
    String trackSerial,
  ) async {
    final token = await _getToken();
    await http.delete(
      Uri.parse(
        '$server/delete/track_from_custom_music_playlist/$playlistSerial/$trackSerial/',
      ),
      headers: {'Authorization': token},
    );
  }

  Future<void> _showTrackMenu(
    BuildContext context,
    Map<String, dynamic> track,
    Offset position,
  ) async {
    final notAdded = await _getNotAddedPlaylists(track['track_serial']);
    final added = await _getAddedPlaylists(track['track_serial']);

    if (!mounted) return;

    final action = await showMenu<String>(
      context: context,
      position: RelativeRect.fromLTRB(position.dx, position.dy, 0, 0),
      items: [
        PopupMenuItem(
          value: 'add',
          enabled: notAdded.isNotEmpty,
          child: const Text('Add to custom playlist  ▶'),
        ),
        PopupMenuItem(
          value: 'remove',
          enabled: added.isNotEmpty,
          child: const Text('Remove from custom playlist  ▶'),
        ),
        const PopupMenuItem(value: 'full', child: Text('Add full track')),
      ],
    );

    if (action == 'add') {
      _showPlaylistSubMenu(context, track, notAdded, true, position);
    } else if (action == 'remove') {
      _showPlaylistSubMenu(context, track, added, false, position);
    } else if (action == 'full') {
      showDialog(
        context: context,
        builder: (_) => AddFullTrackPopup(
          trackId: track['track_serial'],
          trackTitle: track['track_name'],
        ),
      );
    }
  }

  Future<void> _showPlaylistSubMenu(
    BuildContext context,
    Map<String, dynamic> track,
    List<Map<String, dynamic>> playlists,
    bool isAdd,
    Offset parentPosition,
  ) async {
    final selected = await showMenu<Map<String, dynamic>>(
      context: context,
      position: RelativeRect.fromLTRB(
        parentPosition.dx + 200,
        parentPosition.dy,
        0,
        0,
      ),
      items: playlists
          .map(
            (playlist) => PopupMenuItem<Map<String, dynamic>>(
              value: playlist,
              child: Text(playlist['playlist_name']),
            ),
          )
          .toList(),
    );

    if (selected == null) return;

    if (isAdd) {
      await _addTrackToPlaylist(selected['serial'], track['track_serial']);
    } else {
      await _removeTrackFromPlaylist(selected['serial'], track['track_serial']);
    }
  }

  String _formatDuration(Duration d) {
    final m = d.inMinutes;
    final s = d.inSeconds % 60;
    return '$m:${s.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    for (final track in _tracks) {
      (track['player'] as AudioPlayer?)?.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Align(
                alignment: Alignment.topRight,
                child: IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: widget.onClose,
                ),
              ),
              Text(
                widget.album['album_name'],
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 12),
              if (_thumbnailBytes != null)
                Image.memory(_thumbnailBytes!, height: 180, fit: BoxFit.cover),
              const SizedBox(height: 12),
              Text('Artist: ${widget.album['artist_record']}'),
              Text('Type: ${widget.album['album_type']}'),
              Text('Popularity: ${widget.album['album_popularity']}'),
              Text('Release Date: ${widget.album['release_date']}'),
              Text('Total Tracks: ${widget.album['total_tracks']}'),
              const SizedBox(height: 16),
              const Text(
                'Tracks',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              if (_loadingTracks)
                const Center(child: CircularProgressIndicator())
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _tracks.length,
                  itemBuilder: (context, index) {
                    final track = _tracks[index];
                    final player = track['player'] as AudioPlayer?;

                    if (player == null) return const SizedBox();

                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 6),
                      child: Padding(
                        padding: const EdgeInsets.all(8),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    '${track['track_number']}. ${track['track_name']}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Builder(
                                  builder: (context) {
                                    return IconButton(
                                      icon: const Icon(Icons.more_vert),
                                      onPressed: () {
                                        final box =
                                            context.findRenderObject()
                                                as RenderBox;
                                        _showTrackMenu(
                                          context,
                                          track,
                                          box.localToGlobal(Offset.zero),
                                        );
                                      },
                                    );
                                  },
                                ),
                              ],
                            ),
                            StreamBuilder<Duration>(
                              stream: player.positionStream,
                              builder: (context, snapshot) {
                                final position = snapshot.data ?? Duration.zero;
                                final duration =
                                    player.duration ?? Duration.zero;

                                return Column(
                                  children: [
                                    Slider(
                                      min: 0,
                                      max: duration.inMilliseconds
                                          .toDouble()
                                          .clamp(1, double.infinity),
                                      value: position.inMilliseconds
                                          .toDouble()
                                          .clamp(
                                            0,
                                            duration.inMilliseconds.toDouble(),
                                          ),
                                      onChanged: (value) => player.seek(
                                        Duration(milliseconds: value.toInt()),
                                      ),
                                    ),
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(_formatDuration(position)),
                                        Text(_formatDuration(duration)),
                                      ],
                                    ),
                                  ],
                                );
                              },
                            ),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.replay_10),
                                  onPressed: () => player.seek(
                                    player.position -
                                        const Duration(seconds: 10),
                                  ),
                                ),
                                StreamBuilder<PlayerState>(
                                  stream: player.playerStateStream,
                                  builder: (context, snapshot) {
                                    final playing =
                                        snapshot.data?.playing ?? false;
                                    return IconButton(
                                      iconSize: 36,
                                      icon: Icon(
                                        playing
                                            ? Icons.pause_circle
                                            : Icons.play_circle,
                                      ),
                                      onPressed: () => playing
                                          ? player.pause()
                                          : _playTrack(player),
                                    );
                                  },
                                ),
                                IconButton(
                                  icon: const Icon(Icons.forward_10),
                                  onPressed: () => player.seek(
                                    player.position +
                                        const Duration(seconds: 10),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
