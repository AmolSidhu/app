import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/music/requests/customMusicPlaylistsRequest.dart';
import 'package:flutter_frontend/assets/music/popups/createCustomMusicPlaylistPopup.dart';

class ViewAllCustomMusicPlaylistPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Custom Music Albums'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Create Album',
            onPressed: () {
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (_) => const CreateCustomMusicPlaylistPopup(),
              );
            },
          ),
        ],
      ),
      body: CustomMusicPlaylistsRequest(),
    );
  }
}
