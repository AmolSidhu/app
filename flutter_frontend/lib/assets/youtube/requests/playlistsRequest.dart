import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/youtube/youtubeStreamPage.dart';
import 'package:flutter_frontend/assets/youtube/popups/uploadYoutubeVideoToPlaylistPopup.dart';

class YoutubePlaylistsRequest extends StatefulWidget {
  const YoutubePlaylistsRequest({Key? key}) : super(key: key);

  @override
  State<YoutubePlaylistsRequest> createState() =>
      _YoutubePlaylistsRequestState();
}

class Playlist {
  final String serial;
  final String name;
  final String description;

  List<Video> videos = [];
  int page = 0;
  int total = 0;
  bool isLoading = false;

  int dynamicLimit = 4;
  double lastWidth = 0;

  Playlist({
    required this.serial,
    required this.name,
    required this.description,
  });

  factory Playlist.fromJson(Map<String, dynamic> json) {
    return Playlist(
      serial: json['serial'].toString(),
      name: json['name'],
      description: json['description'] ?? '',
    );
  }

  bool get hasMore => (page + 1) * dynamicLimit < total;
}

class Video {
  final String serial;
  final String title;
  final MemoryImage? image;

  Video({required this.serial, required this.title, this.image});
}

class _YoutubePlaylistsRequestState extends State<YoutubePlaylistsRequest> {
  final _storage = const FlutterSecureStorage();

  List<Playlist> playlists = [];
  bool isLoading = true;
  String? error;

  static const double _itemWidth = 200;
  static const double _imageHeight = 120;
  static const double _spacing = 16;

  @override
  void initState() {
    super.initState();
    _fetchPlaylists();
  }

  Future<String> _getToken() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('Not authenticated');
    return token;
  }

  Future<void> _fetchPlaylists() async {
    try {
      final token = await _getToken();
      final res = await http.get(
        Uri.parse('$server/get/youtube_playlists/'),
        headers: {'Authorization': token},
      );

      if (res.statusCode != 200) {
        throw Exception('Failed to load playlists');
      }

      final body = jsonDecode(res.body);
      playlists = (body['data'] as List)
          .map((e) => Playlist.fromJson(e))
          .toList();

      setState(() => isLoading = false);

      for (final p in playlists) {
        _fetchVideos(p);
      }
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  Future<void> _fetchVideos(Playlist playlist) async {
    if (playlist.isLoading || playlist.dynamicLimit <= 0) return;

    playlist.isLoading = true;
    setState(() {});

    try {
      final token = await _getToken();
      final offset = playlist.page * playlist.dynamicLimit;

      final res = await http.get(
        Uri.parse(
          '$server/get/playlist_videos/${playlist.serial}'
          '?offset=$offset&limit=${playlist.dynamicLimit}',
        ),
        headers: {'Authorization': token},
      );

      if (res.statusCode != 200) throw Exception('Fetch failed');

      final body = jsonDecode(res.body);

      playlist.total = body['total'];
      final List data = body['data'];

      final List<Video> loaded = [];

      for (final v in data) {
        MemoryImage? image;
        try {
          final thumbRes = await http.get(
            Uri.parse('$server/get/youtube_thumbnail/${v['serial']}'),
            headers: {'Authorization': token},
          );
          if (thumbRes.statusCode == 200) {
            image = MemoryImage(thumbRes.bodyBytes);
          }
        } catch (_) {}

        loaded.add(
          Video(
            serial: v['serial'].toString(),
            title: v['title'],
            image: image,
          ),
        );
      }

      playlist.videos = loaded;
    } catch (_) {
    } finally {
      playlist.isLoading = false;
      if (mounted) setState(() {});
    }
  }

  void _prevPage(Playlist p) {
    if (p.page > 0) {
      p.page--;
      p.videos.clear();
      _fetchVideos(p);
    }
  }

  void _nextPage(Playlist p) {
    if (p.hasMore) {
      p.page++;
      p.videos.clear();
      _fetchVideos(p);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) return const Center(child: CircularProgressIndicator());
    if (error != null) return Center(child: Text(error!));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(children: playlists.map(_buildPlaylist).toList()),
    );
  }

  Widget _buildPlaylist(Playlist playlist) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final itemsPerRow = (width / (_itemWidth + _spacing)).floor().clamp(
          1,
          10,
        );

        if (itemsPerRow != playlist.dynamicLimit ||
            width != playlist.lastWidth) {
          playlist.dynamicLimit = itemsPerRow;
          playlist.lastWidth = width;

          WidgetsBinding.instance.addPostFrameCallback((_) {
            playlist.page = 0;
            playlist.videos.clear();
            _fetchVideos(playlist);
          });
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              playlist.name,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Text(playlist.description),
            const SizedBox(height: 8),

            ElevatedButton(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (_) => UploadYoutubeVideoToPlaylistPopup(
                    playlistSerial: playlist.serial,
                    onClose: () => Navigator.pop(context),
                  ),
                );
              },
              child: const Text('Upload Video'),
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: playlist.page > 0
                      ? () => _prevPage(playlist)
                      : null,
                ),
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: playlist.videos.map((video) {
                        return GestureDetector(
                          onTap: () async {
                            await _storage.write(
                              key: 'youtubeSerial',
                              value: video.serial,
                            );

                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => YoutubeStreamPage(
                                  videoSerial: video.serial,
                                ),
                              ),
                            );
                          },
                          child: Container(
                            width: _itemWidth,
                            margin: const EdgeInsets.symmetric(horizontal: 8),
                            child: Column(
                              children: [
                                video.image != null
                                    ? Image(
                                        image: video.image!,
                                        height: _imageHeight,
                                        fit: BoxFit.cover,
                                      )
                                    : Container(
                                        height: _imageHeight,
                                        color: Colors.grey[300],
                                      ),
                                const SizedBox(height: 8),
                                Text(
                                  video.title,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: playlist.hasMore
                      ? () => _nextPage(playlist)
                      : null,
                ),
              ],
            ),

            if (playlist.isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: LinearProgressIndicator(),
              ),

            const Divider(thickness: 2),
          ],
        );
      },
    );
  }
}
