import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/management/requests/MyVideoUploadsRequest.dart';

class ViewAllVideoUploadsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('All Video Uploads')),
      body: MyVideoUploadsRequest(),
    );
  }
}
