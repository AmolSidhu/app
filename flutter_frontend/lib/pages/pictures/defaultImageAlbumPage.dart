import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/pictures/requests/defaultAlbumRequest.dart';
import 'package:flutter_frontend/assets/pictures/popups/createDefaultPictureAlbumPopup.dart';

class DefaultImageAlbumPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Default Image Album'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Create Album',
            onPressed: () {
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (_) => const CreateDefaultPictureAlbumPopup(),
              );
            },
          ),
        ],
      ),
      body: DefaultAlbumsRequest(),
    );
  }
}
