import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class CustomMusicPlaylistRequest extends StatefulWidget {
  const CustomMusicPlaylistRequest({Key? key}) : super(key: key);

  @override
  State<CustomMusicPlaylistRequest> createState() =>
      _CustomMusicPlaylistRequestState();
}

class _CustomMusicPlaylistRequestState
    extends State<CustomMusicPlaylistRequest> {
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  late Future<List<dynamic>> _tracksFuture;

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
    final token = await _secureStorage.read(key: 'token');
    final playlistSerial = await _secureStorage.read(
      key: 'customMusicPlaylistSerial',
    );

    if (token == null) {
      throw Exception('Authorization token not found.');
    }

    if (playlistSerial == null) {
      throw Exception('Playlist serial not found.');
    }

    final response = await http.get(
      Uri.parse('$server/get/custom_music_playlist_tracks/$playlistSerial/'),
      headers: <String, String>{
        'Authorization': token,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Playlist Tracks')),
      body: FutureBuilder<List<dynamic>>(
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
            return const Center(
              child: Text('No tracks found in this playlist.'),
            );
          }

          return ListView.builder(
            itemCount: tracks.length,
            itemBuilder: (context, index) {
              final track = tracks[index];

              final int durationMs = track['track_duration'] as int;

              return ListTile(
                leading: Text(
                  track['track_number'].toString(),
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                title: Text(track['track_name']?.toString() ?? ''),
                subtitle: Text(track['artist_name']?.toString() ?? ''),
                trailing: Text(formatDuration(durationMs)),
              );
            },
          );
        },
      ),
    );
  }
}
