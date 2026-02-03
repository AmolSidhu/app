import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/music/popups/musicAlbumPopup.dart';
import 'package:flutter_frontend/assets/music/popups/createMusicAlbumPopup.dart';

class MusicAlbumRequest extends StatefulWidget {
  const MusicAlbumRequest({super.key});

  @override
  State<MusicAlbumRequest> createState() => _MusicAlbumRequestState();
}

class _MusicAlbumRequestState extends State<MusicAlbumRequest> {
  final _storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> _albums = [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchAlbums();
  }

  Future<String> _getToken() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('Token missing');
    return token;
  }

  Future<void> _fetchAlbums() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$server/get/music_albums/'),
        headers: {'Authorization': token},
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to fetch albums');
      }

      final data = jsonDecode(response.body);
      final List<Map<String, dynamic>> albums = data['data'] != null
          ? List<Map<String, dynamic>>.from(data['data'])
          : [];

      for (final album in albums) {
        album['thumbnailBytes'] = await _fetchThumbnail(album['serial'], token);
      }

      setState(() {
        _albums = albums;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error fetching albums';
        _loading = false;
      });
    }
  }

  Future<Uint8List?> _fetchThumbnail(String serial, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$server/get/album_thumbnail/$serial/'),
        headers: {'Authorization': token},
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
    } catch (_) {}
    return null;
  }

  void _openAlbum(Map<String, dynamic> album) {
    showDialog(
      context: context,
      builder: (_) => MusicAlbumPopup(
        album: album,
        onClose: () => Navigator.of(context).pop(),
      ),
    );
  }

  void _openCreateAlbum() {
    showDialog(
      context: context,
      builder: (_) => const CreateMusicAlbumPopup(),
    ).then((_) {
      _fetchAlbums();
    });
  }

  Future<void> _openSpotify(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Music Albums')),

      floatingActionButton: FloatingActionButton(
        onPressed: _openCreateAlbum,
        child: const Icon(Icons.add),
      ),

      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(
              child: Text(_error!, style: const TextStyle(color: Colors.red)),
            )
          : _albums.isEmpty
          ? const Center(
              child: Text(
                'No music albums found',
                style: TextStyle(fontSize: 16),
              ),
            )
          : Padding(
              padding: const EdgeInsets.all(12),
              child: GridView.builder(
                itemCount: _albums.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 0.68,
                ),
                itemBuilder: (context, index) {
                  final album = _albums[index];
                  final Uint8List? thumbnail = album['thumbnailBytes'];

                  return GestureDetector(
                    onTap: () => _openAlbum(album),
                    child: Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(8),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: thumbnail != null
                                  ? ClipRRect(
                                      borderRadius: BorderRadius.circular(8),
                                      child: Image.memory(
                                        thumbnail,
                                        width: double.infinity,
                                        fit: BoxFit.cover,
                                      ),
                                    )
                                  : Container(
                                      alignment: Alignment.center,
                                      decoration: BoxDecoration(
                                        color: Colors.grey.shade300,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: const Text('No Image'),
                                    ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              album['album_name'],
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              'Artist: ${album['artist_record']}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text('Type: ${album['album_type']}'),
                            Text('Popularity: ${album['album_popularity']}'),
                            Text('Tracks: ${album['total_tracks']}'),
                            const SizedBox(height: 6),
                            GestureDetector(
                              onTap: () =>
                                  _openSpotify(album['album_spotify_link']),
                              child: const Text(
                                'Spotify',
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}
