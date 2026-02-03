import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/management/requests/ViewVideoRequestsRequest.dart';

class ViewMyVideoRequestsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('My Video Requests')),
      body: Center(child: ViewVideoRequestsRequest()),
    );
  }
}
