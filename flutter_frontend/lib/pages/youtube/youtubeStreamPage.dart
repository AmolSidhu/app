import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/youtube/requests/youtubeVideoStreamRequest.dart';
import 'package:flutter_frontend/assets/youtube/requests/youtubeStreamInfoRequest.dart';

class YoutubeStreamPage extends StatelessWidget {
  final String videoSerial;

  const YoutubeStreamPage({Key? key, required this.videoSerial})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => Navigator.of(context).pop(),
              ),
              const SizedBox(width: 8),
              const Text(
                'YouTube Stream Page',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),

        Expanded(
          child: Column(
            children: [
              YoutubeVideoStreamRequest(videoSerial: videoSerial),

              Expanded(child: YoutubeStreamInfoRequest()),
            ],
          ),
        ),
      ],
    );
  }
}
