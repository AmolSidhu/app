import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/switch/videoUploadSwitch.dart';

class VideoUploadPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Upload Page')),
      body: Center(child: VideoUploadSwitch()),
    );
  }
}
