import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_frontend/assets/videos/popups/videoDetailPopup.dart';
import 'package:flutter_frontend/static/constants.dart';

class VideoSuggestionsRequest extends StatefulWidget {
  const VideoSuggestionsRequest({super.key});

  @override
  State<VideoSuggestionsRequest> createState() =>
      _VideoSuggestionsRequestState();
}

class _VideoSuggestionsRequestState extends State<VideoSuggestionsRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> videos = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    fetchVideos();
  }

  Future<void> fetchVideos() async {
    try {
      final token = await _storage.read(key: 'token');
      final serial = await _storage.read(key: 'videoSerial');
      if (serial == null) throw Exception('Missing serial');

      final response = await http.get(
        Uri.parse('$server/get/video_suggestions/$serial/'),
        headers: {'Authorization': token ?? ''},
      );

      final decoded = jsonDecode(response.body);
      final List<dynamic> data = decoded['data'] ?? [];

      final fetched = <Map<String, dynamic>>[];

      for (final item in data) {
        final video = Map<String, dynamic>.from(item);
        try {
          final thumb = await http.get(
            Uri.parse('$server/get/video_thumbnail/${video['serial']}'),
            headers: {'Authorization': token ?? ''},
          );
          if (thumb.statusCode == 200) {
            video['image_url'] =
                'data:image/png;base64,${base64Encode(thumb.bodyBytes)}';
          }
        } catch (_) {}
        fetched.add(video);
      }

      setState(() {
        videos = fetched;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  void openPopup(String serial) {
    showDialog(
      context: context,
      builder: (_) => Dialog(child: VideoDetailPopup(serial: serial)),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    if (error != null) return Center(child: Text(error!));
    if (videos.isEmpty) return const SizedBox.shrink();

    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = (constraints.maxWidth / 180).floor().clamp(2, 6);

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Suggested Videos', style: TextStyle(fontSize: 20)),
            ),
            GridView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 16 / 9,
              ),
              itemCount: videos.length,
              itemBuilder: (context, index) {
                final video = videos[index];
                return GestureDetector(
                  onTap: () => openPopup(video['serial']),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: video['image_url'] != null
                        ? Image.network(video['image_url'], fit: BoxFit.cover)
                        : Container(color: Colors.grey),
                  ),
                );
              },
            ),
          ],
        );
      },
    );
  }
}
