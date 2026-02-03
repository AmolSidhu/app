import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/pictures/requests/customImageRequest.dart';

class CustomPicturePage extends StatelessWidget {
  final String pictureId;

  const CustomPicturePage({super.key, required this.pictureId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Custom Picture')),
      body: Center(child: CustomImageRequest(pictureId: pictureId)),
    );
  }
}
