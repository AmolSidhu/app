import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/general/requests/serverPatchDataRequest.dart';

class AboutPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('About Page')),
      body: Center(child: ServerDataRequestPage()),
    );
  }
}
