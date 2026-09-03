import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CustomMusicPlaylistRequest extends StatefulWidget {
  final VoidCallback onTrackSelected;

  const CustomMusicPlaylistRequest({Key? key, required this.onTrackSelected})
    : super(key: key);

  @override
  State<CustomMusicPlaylistRequest> createState() =>
      _CustomMusicPlaylistRequestState();
}

class _CustomMusicPlaylistRequestState
    extends State<CustomMusicPlaylistRequest> {
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  late Future<List<dynamic>> _tracksFuture;

  String? _token;
  String? _playlistSerial;

  @override
  void initState() {
    super.initState();
    _tracksFuture = _fetchPlaylistTracks();
  }

  String formatDuration(int milliseconds) {
    final totalSeconds = milliseconds ~/ 1000;
    final minutes = totalSeconds ~/ 60;
    final seconds = totalSeconds % 60;
    return '$minutes:${seconds.toString().padLeft(2, '0')}';
  }

  Future<List<dynamic>> _fetchPlaylistTracks() async {
    _token = await _secureStorage.read(key: 'token');
    _playlistSerial = await _secureStorage.read(
      key: 'customMusicPlaylistSerial',
    );

    if (_token == null) {
      throw Exception('Authorization token not found.');
    }

    if (_playlistSerial == null) {
      throw Exception('Playlist serial not found.');
    }

    final response = await http.get(
      Uri.parse('$server/get/custom_music_playlist_tracks/$_playlistSerial/'),
      headers: <String, String>{
        'Authorization': _token!,
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      return decoded['data'] as List<dynamic>;
    } else {
      final decoded = jsonDecode(response.body);
      throw Exception(decoded['message'] ?? 'Failed to fetch tracks');
    }
  }

  Widget _buildThumbnail(String trackSerial) {
    if (_token == null || _playlistSerial == null) {
      return const Icon(Icons.music_note);
    }

    final imageUrl =
        '$server/get/listed_track_thumbnails/$_playlistSerial/$trackSerial/';

    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Image.network(
        imageUrl,
        width: 50,
        height: 50,
        fit: BoxFit.cover,
        headers: {'Authorization': _token!},
        errorBuilder: (context, error, stackTrace) {
          return const Icon(Icons.music_note, size: 50);
        },
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return const SizedBox(
            width: 50,
            height: 50,
            child: Center(
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _onPlayTrackPressed(String trackSerial) async {
    if (_token == null || _playlistSerial == null) return;

    final switchUrl =
        '$server/get/currently_playing_track_data/$_playlistSerial/?track_serial=$trackSerial';

    final switchResponse = await http.get(
      Uri.parse(switchUrl),
      headers: {'Authorization': _token!},
    );

    if (switchResponse.statusCode != 200) return;

    final fetchUrl =
        '$server/get/currently_playing_track_data/$_playlistSerial/';

    final fetchResponse = await http.get(
      Uri.parse(fetchUrl),
      headers: {'Authorization': _token!},
    );

    if (fetchResponse.statusCode != 200) return;

    final data = jsonDecode(fetchResponse.body)['data'];

    await _secureStorage.write(
      key: 'customMusicPlaylistTrackSerial',
      value: data['custom_playlist_track_serial'],
    );

    await _secureStorage.write(
      key: 'musicPlaylistTrackSerial',
      value: data['track_serial'],
    );

    await _secureStorage.write(
      key: 'playOrder',
      value: data['play_order'].toString(),
    );

    await _secureStorage.write(key: 'trackStopTime', value: '0');

    widget.onTrackSelected();

    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: _tracksFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        final tracks = snapshot.data;

        if (tracks == null || tracks.isEmpty) {
          return const Center(child: Text('No tracks found in this playlist.'));
        }

        return ListView.builder(
          itemCount: tracks.length,
          itemBuilder: (context, index) {
            final track = tracks[index];

            final int durationMs = track['track_duration'] as int;
            final String trackSerial = track['track_serial'].toString();

            return ListTile(
              leading: _buildThumbnail(trackSerial),
              title: Text(track['track_name']?.toString() ?? ''),
              subtitle: Text(track['artist_name']?.toString() ?? ''),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        track['track_number'].toString(),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(formatDuration(durationMs)),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.play_arrow, color: Colors.green),
                    onPressed: () => _onPlayTrackPressed(trackSerial),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
