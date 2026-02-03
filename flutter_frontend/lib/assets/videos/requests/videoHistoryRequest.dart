import 'package:flutter/material.dart';
import 'videoListRequest.dart';

class VideoHistoryRequest extends StatelessWidget {
  const VideoHistoryRequest({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text(
          'Recently Watched',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 8),
        VideoListRequest(videosEndpoint: '/get/recently_viewed_videos'),
      ],
    );
  }
}
