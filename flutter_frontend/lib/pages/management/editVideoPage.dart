import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/management/forms/editVideoForm.dart';

class EditVideoPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Edit Video Page')),
      body: Center(child: EditVideoForm()),
    );
  }
}
