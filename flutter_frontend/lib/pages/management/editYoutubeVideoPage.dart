import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/management/forms/editYoutubeVideoForm.dart';

class EditYoutubeVideoPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Edit YouTube Video Page')),
      body: EditVideoForm(),
    );
  }
}
