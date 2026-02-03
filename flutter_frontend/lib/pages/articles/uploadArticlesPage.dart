import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/articles/switch/articleUploadSwitch.dart';

class UploadArticlesPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload Articles Page')),
      body: Center(child: ArticleUploadSwitch()),
    );
  }
}
