import 'package:flutter/material.dart';
import 'videoListRequest.dart';

class Videosrequest extends StatelessWidget {
  const Videosrequest({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text(
          'All Videos',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 8),
        VideoListRequest(videosEndpoint: '/get/videos'),
      ],
    );
  }
}
