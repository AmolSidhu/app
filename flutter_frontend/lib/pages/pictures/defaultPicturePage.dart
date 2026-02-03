import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/pictures/requests/defaultImageRequest.dart';
import 'package:flutter_frontend/assets/pictures/popups/pictureUploadPopup.dart';

class DefaultPicturePage extends StatelessWidget {
  final String pictureId;

  const DefaultPicturePage({super.key, required this.pictureId});

  void _showUploadPopup(BuildContext context) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: 'Upload Picture',
      barrierColor: Colors.black54,
      transitionDuration: const Duration(milliseconds: 200),
      pageBuilder: (context, animation, secondaryAnimation) {
        return SafeArea(
          child: Align(
            alignment: Alignment.topRight,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Material(
                borderRadius: BorderRadius.circular(12),
                elevation: 8,
                child: SizedBox(width: 400, child: const PictureUploadPopup()),
              ),
            ),
          ),
        );
      },
      transitionBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0.2, -0.2),
              end: Offset.zero,
            ).animate(animation),
            child: child,
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Default Picture'),
        actions: [
          IconButton(
            icon: const Icon(Icons.upload),
            tooltip: 'Upload Picture',
            onPressed: () => _showUploadPopup(context),
          ),
        ],
      ),
      body: Center(child: DefaultImageRequest(pictureId: pictureId)),
    );
  }
}
