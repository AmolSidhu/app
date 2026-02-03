import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/files/switch/fileShareSwitch.dart';

class UploadShareFilePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload Share File Page')),
      body: Center(child: FileShareSwitch()),
    );
  }
}
