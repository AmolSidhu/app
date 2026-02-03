import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/pictures/requests/customAlbumRequest.dart';
import 'package:flutter_frontend/assets/pictures/popups/createCustomPictureAlbumPopup.dart';

class CustomImageAlbumsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Custom Image Albums'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Create Album',
            onPressed: () {
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (_) => const CreateCustomPictureAlbumPopup(),
              );
            },
          ),
        ],
      ),
      body: CustomAlbumRequest(),
    );
  }
}
