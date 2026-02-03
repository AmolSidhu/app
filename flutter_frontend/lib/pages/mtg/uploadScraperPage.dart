import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/mtg/forms/uploadScraperForm.dart';

class UploadScraperPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload Scraper Page')),
      body: Center(child: UploadScraperForm()),
    );
  }
}
