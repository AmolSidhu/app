import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/requests/videosRequest.dart';
import 'package:flutter_frontend/assets/videos/requests/videoHistoryRequest.dart';
import 'package:flutter_frontend/assets/videos/requests/videoGenreRequest.dart';
import 'package:flutter_frontend/assets/videos/requests/videoTitleSearchRequest.dart';

class VideoPage extends StatelessWidget {
  const VideoPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Page')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            VideoTitleSearchRequest(),
            SizedBox(height: 32),
            Videosrequest(),
            SizedBox(height: 32),
            VideoHistoryRequest(),
            SizedBox(height: 32),
            VideoGenreRequest(),
          ],
        ),
      ),
    );
  }
}
