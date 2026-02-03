import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/forms/videoRequestForm.dart';

class MakeVideoRequestPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Make Video Request')),
      body: Center(child: VideoRequestForm()),
    );
  }
}
