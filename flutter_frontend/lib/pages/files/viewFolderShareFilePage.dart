import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/files/requests/viewAllShareFolderFilesRequest.dart';

class ViewFolderShareFilePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('View Folder Share File Page')),
      body: Center(child: ViewAllShareFolderFilesRequest(folderSerial: '')),
    );
  }
}
