import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/videos/popups/videoDetailPopup.dart';

class VideoListRequest extends StatefulWidget {
  final String videosEndpoint;

  const VideoListRequest({Key? key, required this.videosEndpoint})
    : super(key: key);

  @override
  State<VideoListRequest> createState() => _VideoListRequestState();
}

class _VideoListRequestState extends State<VideoListRequest> {
  final _storage = const FlutterSecureStorage();
  List<Map<String, dynamic>> _videos = [];
  String? _error;
  int _page = 1;
  bool _hasMore = false;
  bool _isLoading = false;

  static const double _itemWidth = 200.0;
  static const double _imageHeight = 150.0;
  static const double _spacing = 16.0;

  int _dynamicLimit = 5;
  double _lastWidth = 0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth = constraints.maxWidth;
        final itemsPerRow = (availableWidth / (_itemWidth + _spacing)).floor();

        if (itemsPerRow != _dynamicLimit || availableWidth != _lastWidth) {
          _dynamicLimit = itemsPerRow;
          _lastWidth = availableWidth;

          WidgetsBinding.instance.addPostFrameCallback((_) {
            _page = 1;
            _videos.clear();
            _fetchVideos();
          });
        }

        if (_error != null) return Center(child: Text('Error: $_error'));
        if (_isLoading && _videos.isEmpty)
          return const Center(child: CircularProgressIndicator());

        return Column(
          children: [
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: _page > 1 ? _handlePrevPage : null,
                ),
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _videos.map((video) {
                        return GestureDetector(
                          onTap: () {
                            showDialog(
                              context: context,
                              builder: (_) => Dialog(
                                child: SizedBox(
                                  width: 600,
                                  height: 600,
                                  child: VideoDetailPopup(
                                    serial: video['serial'],
                                  ),
                                ),
                              ),
                            );
                          },
                          child: Container(
                            width: _itemWidth,
                            margin: const EdgeInsets.symmetric(horizontal: 8),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                video['image'] != null
                                    ? Image(
                                        image: video['image'],
                                        height: _imageHeight,
                                        fit: BoxFit.cover,
                                      )
                                    : Container(
                                        height: _imageHeight,
                                        color: Colors.grey[300],
                                        child: const Icon(Icons.error),
                                      ),
                                const SizedBox(height: 8),
                                Text(
                                  video['title'] ?? 'Unknown',
                                  textAlign: TextAlign.center,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
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
                  onPressed: _hasMore ? _handleNextPage : null,
                ),
              ],
            ),
            if (_isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: LinearProgressIndicator(),
              ),
          ],
        );
      },
    );
  }

  Future<void> _fetchVideos() async {
    if (_isLoading || _dynamicLimit <= 0) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      if (token == null) throw Exception('Token not found');

      final response = await http.get(
        Uri.parse(
          '$server${widget.videosEndpoint}?page=$_page&limit=$_dynamicLimit',
        ),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200)
        throw Exception('HTTP error: ${response.statusCode}');
      final data = jsonDecode(response.body);
      final List<dynamic> videos = data['data']['videos'];

      final List<Map<String, dynamic>> fetchedVideos = [];

      for (var video in videos) {
        try {
          final thumbnailResponse = await http.get(
            Uri.parse('$server/get/video_thumbnail/${video['serial']}'),
            headers: {'Authorization': token},
          );

          if (thumbnailResponse.statusCode != 200)
            throw Exception('Thumbnail error');

          fetchedVideos.add({
            ...video,
            'image': MemoryImage(thumbnailResponse.bodyBytes),
          });
        } catch (_) {
          fetchedVideos.add(video);
        }
      }

      if (!mounted) return;

      setState(() {
        _videos = fetchedVideos;
        _hasMore = data['data']['has_more'];
        _isLoading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.toString();
        _isLoading = false;
      });
    }
  }

  void _handlePrevPage() {
    if (_page > 1) {
      setState(() {
        _page--;
        _videos.clear();
      });
      _fetchVideos();
    }
  }

  void _handleNextPage() {
    if (_hasMore) {
      setState(() {
        _page++;
        _videos.clear();
      });
      _fetchVideos();
    }
  }
}
