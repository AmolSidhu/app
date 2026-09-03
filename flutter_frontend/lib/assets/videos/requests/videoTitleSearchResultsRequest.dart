import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/videos/popups/videoDetailPopup.dart';

class VideoTitleSearchResultsRequest extends StatefulWidget {
  const VideoTitleSearchResultsRequest({Key? key}) : super(key: key);

  @override
  State<VideoTitleSearchResultsRequest> createState() =>
      _VideoTitleSearchResultsRequestState();
}

class _VideoTitleSearchResultsRequestState
    extends State<VideoTitleSearchResultsRequest> {
  final storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> videos = [];
  String? error;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchVideos();
  }

  Future<void> _fetchVideos() async {
    try {
      final token = await storage.read(key: 'token');
      final query = await storage.read(key: 'videoTitleSearchQuery');

      if (query == null || query.isEmpty) {
        throw Exception('Search query not found');
      }

      final response = await http.get(
        Uri.parse('$server/get/videos_by_search/$query/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to fetch videos');
      }

      final data = jsonDecode(response.body);
      final List fetchedVideos = data['data'];

      List<Map<String, dynamic>> enrichedVideos = [];

      for (var video in fetchedVideos) {
        Uint8List? thumbnailBytes;

        try {
          final thumbResponse = await http.get(
            Uri.parse('$server/get/video_thumbnail/${video['serial']}'),
            headers: {'Authorization': token ?? ''},
          );

          if (thumbResponse.statusCode == 200) {
            thumbnailBytes = thumbResponse.bodyBytes;
          }
        } catch (_) {}

        enrichedVideos.add({...video, 'thumbnail': thumbnailBytes});
      }

      setState(() {
        videos = enrichedVideos;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  void _openPopup(String serial) {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        insetPadding: const EdgeInsets.all(16),
        child: VideoDetailPopup(serial: serial),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Center(
        child: Text('Error: $error', style: const TextStyle(color: Colors.red)),
      );
    }

    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (videos.isEmpty) {
      return const Center(child: Text('No results found'));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Search Results')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: GridView.builder(
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 16 / 9,
          ),
          itemCount: videos.length,
          itemBuilder: (context, index) {
            final video = videos[index];
            final Uint8List? thumbnail = video['thumbnail'];

            return InkWell(
              onTap: () => _openPopup(video['serial']),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.black12,
                  borderRadius: BorderRadius.circular(8),
                ),
                clipBehavior: Clip.antiAlias,
                child: thumbnail != null
                    ? Image.memory(thumbnail, fit: BoxFit.cover)
                    : const Center(child: Icon(Icons.video_library, size: 48)),
              ),
            );
          },
        ),
      ),
    );
  }
}
