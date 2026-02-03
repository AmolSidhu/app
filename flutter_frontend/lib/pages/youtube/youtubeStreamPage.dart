import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/youtube/requests/youtubeVideoStreamRequest.dart';
import 'package:flutter_frontend/assets/youtube/requests/youtubeStreamInfoRequest.dart';

class YoutubeStreamPage extends StatelessWidget {
  final String videoSerial;

  const YoutubeStreamPage({Key? key, required this.videoSerial})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('YouTube Stream Page')),
      body: Center(
        child: Column(
          children: [
            YoutubeVideoStreamRequest(videoSerial: videoSerial),
            Expanded(child: YoutubeStreamInfoRequest()),
          ],
        ),
      ),
    );
  }
}
