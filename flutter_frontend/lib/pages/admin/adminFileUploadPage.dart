import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/admin/forms/uploadAdminFileForm.dart';

class AdminFileUploadPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Admin File Upload Page')),
      body: Center(child: UploadAdminFileForm()),
    );
  }
}
