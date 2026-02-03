import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/admin/requests/adminVideoRequestApprovalRequest.dart';

class VideoRequestApprovalPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Request Approval')),
      body: AdminVideoRequestApprovalRequest(),
    );
  }
}
