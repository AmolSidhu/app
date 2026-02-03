import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/music/customMusicPlaylistPage.dart';

class CustomMusicPlaylistsRequest extends StatefulWidget {
  const CustomMusicPlaylistsRequest({Key? key}) : super(key: key);

  @override
  State<CustomMusicPlaylistsRequest> createState() =>
      _CustomMusicPlaylistsRequestState();
}

class _CustomMusicPlaylistsRequestState
    extends State<CustomMusicPlaylistsRequest> {
  final FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  late Future<List<dynamic>> _playlistsFuture;

  Future<List<dynamic>> _fetchPlaylists() async {
    final token = await _secureStorage.read(key: 'token');
    if (token == null) {
      throw Exception('Authorization token not found.');
    }

    final response = await http.get(
      Uri.parse('$server/get/custom_music_playlists/'),
      headers: <String, String>{'Authorization': token},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];
      return data;
    } else {
      throw Exception(jsonDecode(response.body)['message']);
    }
  }

  @override
  void initState() {
    super.initState();
    _playlistsFuture = _fetchPlaylists();
  }

  Future<void> _onPlaylistTap(String playlistSerial) async {
    await _secureStorage.write(
      key: 'customMusicPlaylistSerial',
      value: playlistSerial,
    );

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => CustomMusicPlaylistPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: _playlistsFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return Center(child: Text('No custom music playlists found.'));
        } else {
          final playlists = snapshot.data!;
          return ListView.builder(
            itemCount: playlists.length,
            itemBuilder: (context, index) {
              final playlist = playlists[index];
              return ListTile(
                title: Text(playlist['playlist_name']),
                subtitle: Text(
                  playlist['playlist_description'] ?? 'No description',
                ),
                onTap: () => _onPlaylistTap(playlist['serial']),
              );
            },
          );
        }
      },
    );
  }
}
