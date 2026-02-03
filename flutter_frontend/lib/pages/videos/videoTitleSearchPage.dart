import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/requests/videoTitleSearchResultsRequest.dart';

class VideoTitleSearchPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Title Search Page')),
      body: const VideoTitleSearchResultsRequest(),
    );
  }
}
