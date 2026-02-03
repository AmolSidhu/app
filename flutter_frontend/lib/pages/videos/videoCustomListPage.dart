import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/requests/videoCustomListRequest.dart';

class VideoCustomListPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Custom Video List')),
      body: Center(child: VideoCustomListRequest()),
    );
  }
}
